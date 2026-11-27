import argparse
import json
import math
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np


POSE = (11, 12, 13, 14, 15, 16, 23, 24)
FACE = (
    0, 4, 13, 14, 17, 33, 37, 39, 46, 52, 55, 61, 64, 81, 82, 93, 133, 151,
    152, 159, 172, 178, 181, 263, 269, 276, 282, 285, 291, 294, 311, 323, 362, 386, 397,
)
HAND = tuple(range(21))
FRAME_WIDTH = 340


def read_points(detection, indices):
    if detection is None:
        return None
    return np.array([
        (detection.landmark[i].x, detection.landmark[i].y, detection.landmark[i].z)
        for i in indices
    ], dtype=np.float32)


def frame_features(detection, aspect):
    frame = np.zeros((85, 4), dtype=np.float32)
    pose = read_points(detection.pose_landmarks, POSE)
    if pose is None or not np.isfinite(pose).all():
        return frame.ravel(), False, False
    origin = pose[:2].mean(axis=0)
    scale = max(0.08, math.hypot((pose[0, 0] - pose[1, 0]) * aspect, pose[0, 1] - pose[1, 1]))
    left = read_points(detection.left_hand_landmarks, HAND)
    right = read_points(detection.right_hand_landmarks, HAND)
    face = read_points(detection.face_landmarks, FACE)
    for start, points, z_origin in (
        (0, pose, origin[2]),
        (8, left, left[0, 2] if left is not None else 0),
        (29, right, right[0, 2] if right is not None else 0),
        (50, face, face[0, 2] if face is not None else 0),
    ):
        if points is None or not np.isfinite(points).all():
            continue
        out = frame[start:start + len(points)]
        out[:, :3] = (points - (origin[0], origin[1], z_origin)) * (
            aspect / scale, 1 / scale, aspect / scale,
        )
        np.clip(out[:, :3], -5, 5, out=out[:, :3])
        out[:, 3] = 1
    return frame.ravel(), True, bool(frame[8, 3] or frame[29, 3])


def read_video(path, intervals, crop, sample_fps, complexity):
    remote = isinstance(path, str)
    name = "source video" if remote else path.name
    if remote:
        capture = cv2.VideoCapture(path, cv2.CAP_FFMPEG, [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 30000,
            cv2.CAP_PROP_READ_TIMEOUT_MSEC, 30000,
        ])
    else:
        capture = cv2.VideoCapture(str(path))
    try:
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if not capture.isOpened() or not source_fps > 0 or total_frames < 1:
            raise ValueError(f"Cannot decode {name}")
        duration = total_frames / source_fps
        intervals = sorted((max(0, begin), min(end, duration)) for begin, end in (intervals or [(0, duration)]) if begin < duration)
        if not intervals:
            raise ValueError(f"No labels overlap {name}")
        merged = []
        for begin, end in intervals:
            if merged and begin <= merged[-1][1]:
                merged[-1] = merged[-1][0], max(merged[-1][1], end)
            else:
                merged.append((begin, end))
        stride = max(1, round(source_fps / sample_fps))
        frames, times, poses, hands = [], [], [], []
        with mp.solutions.holistic.Holistic(
            model_complexity=complexity,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
        ) as tracker:
            cursor = None
            for begin, end in merged:
                first, last = math.ceil(begin * source_fps), math.ceil(end * source_fps)
                if cursor is None or first - cursor > source_fps * 2:
                    if not capture.set(cv2.CAP_PROP_POS_FRAMES, first) and remote:
                        raise ValueError("Cannot seek in source video")
                    cursor = first
                while cursor < last:
                    index = cursor
                    cursor += 1
                    if not capture.grab():
                        if remote and index < total_frames - 1:
                            raise ValueError("Source video interrupted")
                        break
                    if index < first or index % stride:
                        continue
                    ok, frame = capture.retrieve()
                    if not ok:
                        continue
                    height, width = frame.shape[:2]
                    x0, y0, x1, y1 = crop
                    image = frame[round(y0 * height):round(y1 * height), round(x0 * width):round(x1 * width)]
                    detection = tracker.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    features, pose_visible, hand_visible = frame_features(detection, image.shape[1] / image.shape[0])
                    frames.append(features)
                    times.append(index / source_fps)
                    poses.append(pose_visible)
                    hands.append(hand_visible)
        return np.array(frames, dtype=np.float32), np.array(times), np.array(poses), np.array(hands), duration
    finally:
        capture.release()


def clean_text(text):
    return " ".join(re.sub(r"\[[^]]*\]|\([^)]*\)", "", text).split())


def captions(path):
    for event in json.loads(path.read_text(encoding="utf-8"))["events"]:
        start = event["tStartMs"] / 1000
        end = start + event.get("dDurationMs", 0) / 1000
        text = clean_text(" ".join(segment.get("utf8", "") for segment in event.get("segs", [])))
        if 1 <= end - start <= 17 and 2 <= len(text.split()) and len(text) <= 180:
            yield {"text": text, "start": start, "end": end}


def resolve_video(yt_dlp, source):
    result = subprocess.run(
        [
            yt_dlp, "--ignore-config", "--no-playlist", "--socket-timeout", "10",
            "--retries", "1", "-g", "-f", "bestvideo[height<=720][ext=mp4][protocol=https]", source,
        ],
        check=True, capture_output=True, text=True, timeout=35,
    )
    urls = result.stdout.splitlines()
    if len(urls) != 1 or not urls[0].startswith("https://"):
        raise ValueError("No seekable MP4 source")
    return urls[0]


def signing_window(frames, times):
    points = frames.reshape(-1, 85, 4)
    shoulders = points[:, :2, 1].mean(axis=1)
    hips = points[:, 6:8, 1].mean(axis=1)
    boundary = shoulders + (2 / 3) * (hips - shoulders)
    wrists = points[:, (8, 29)]
    raised = ((wrists[:, :, 3] > 0) & (wrists[:, :, 1] < boundary[:, None])).any(axis=1)
    raised &= (points[:, 0, 3] > 0) & (hips > shoulders)
    pairs = raised[1:] & raised[:-1]
    active = np.flatnonzero(np.r_[pairs, False] | np.r_[False, pairs])
    if len(active) < 5:
        return None
    hands = points[:, 8:50]
    displacement = np.linalg.norm(hands[1:, :, :2] - hands[:-1, :, :2], axis=2)
    tracked = (hands[1:, :, 3] > 0) & (hands[:-1, :, 3] > 0) & pairs[:, None]
    if not tracked.any() or np.quantile(displacement[tracked], 0.8) < 0.025:
        return None
    return times[active[0]], times[active[-1]]


def collect_source(record, media, output, fps, complexity, yt_dlp=None):
    identifier = record["id"]
    manifest_path = output / f"{identifier}.json"
    feature_path = output / f"{identifier}.npz"
    if manifest_path.is_file() and feature_path.is_file():
        return
    labels = record.get("labels")
    video = media
    if not media.is_file():
        if not yt_dlp or not record.get("source") or not labels:
            print(f"Missing media: {identifier}", flush=True)
            return
        try:
            video = resolve_video(yt_dlp, record["source"])
        except (subprocess.SubprocessError, ValueError):
            print(f"Cannot resolve source video: {identifier}", flush=True)
            return
    if labels is None and "text" not in record:
        subtitle_path = media.with_suffix(".tr.json3")
        if not subtitle_path.is_file():
            print(f"Missing captions: {identifier}", flush=True)
            return
        labels = list(captions(subtitle_path))
        if not labels:
            print(f"No usable captions: {identifier}", flush=True)
            return
    intervals = [(item["start"], item["end"]) for item in labels] if labels else None
    crop = record.get("crop", (0, 0, 1, 1))
    try:
        frames, times, poses, hands, duration = read_video(video, intervals, crop, fps, complexity)
    except ValueError as error:
        if isinstance(video, Path):
            raise
        print(f"{error}: {identifier}", flush=True)
        return
    if labels is None:
        labels = [{"text": clean_text(record["text"]), "start": 0, "end": duration}]
    arrays, segments = {}, []
    for item in labels:
        clip = (times >= item["start"]) & (times < item["end"])
        if "caption_end" in item:
            bounds = signing_window(frames[clip], times[clip])
            if bounds is None:
                continue
            start, end = bounds
            clip &= (times >= start - 0.12) & (times <= end + 0.12)
            item = {**item, "signing_start": round(float(start), 3), "signing_end": round(float(end), 3)}
        if clip.sum() < 8 or poses[clip].mean() < 0.65 or hands[clip].mean() < 0.30:
            continue
        name = f"clip_{len(segments):04d}"
        arrays[name] = frames[clip]
        segments.append({**item, "key": name})
    if not arrays:
        print(f"No usable landmark clips: {identifier}", flush=True)
        return
    temporary = feature_path.with_suffix(".tmp.npz")
    np.savez_compressed(temporary, **arrays)
    temporary.replace(feature_path)
    manifest_tmp = manifest_path.with_suffix(".tmp")
    manifest_tmp.write_text(json.dumps({
        "id": identifier, "split": record.get("split", "train"),
        "group": record.get("group", "dictionary"), "segments": segments,
    }, ensure_ascii=False), encoding="utf-8")
    manifest_tmp.replace(manifest_path)
    print(f"{identifier} {len(segments)}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--dictionary", action="store_true")
    parser.add_argument("--split", choices=("train", "dev", "test", "conversation"))
    parser.add_argument("--max-seconds", type=float)
    parser.add_argument("--fps", type=float, default=10)
    parser.add_argument("--complexity", type=int, choices=range(3), default=0)
    parser.add_argument("--yt-dlp", help="Stream missing sources with labeled intervals instead of saving the videos")
    parser.add_argument("--workers", type=int, default=1, help="Number of videos to process concurrently")
    args = parser.parse_args()
    if args.dictionary == bool(args.sources):
        parser.error("Specify either --sources or --dictionary")
    if not 0 < args.fps <= 30:
        parser.error("--fps must be in (0, 30]")
    if args.max_seconds is not None and (args.max_seconds <= 0 or args.dictionary):
        parser.error("--max-seconds must be positive and requires --sources")
    if args.yt_dlp and (not args.sources or not shutil.which(args.yt_dlp)):
        parser.error("--yt-dlp requires --sources and an executable")
    if args.workers < 1:
        parser.error("--workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    cv2.setNumThreads(1)
    metadata = (
        [json.loads(line) for line in (args.input / "dictionary.jsonl").read_text(encoding="utf-8").splitlines() if line]
        if args.dictionary else json.loads(args.sources.read_text(encoding="utf-8"))
    )
    selected = [record for record in metadata if not args.split or record.get("split", "train") == args.split]
    if len({record["id"] for record in selected}) != len(selected):
        parser.error("Source identifiers must be unique")

    def prepare_source(record):
        media = args.input / f"{record['id']}.mp4"
        if args.max_seconds is not None and "labels" not in record:
            subtitle_path = media.with_suffix(".tr.json3")
            if subtitle_path.is_file():
                labels = [item for item in captions(subtitle_path) if item["end"] <= args.max_seconds]
                if not labels:
                    return
                record = {**record, "labels": labels}
        collect_source(record, media, args.output, args.fps, args.complexity, yt_dlp=args.yt_dlp)

    if args.workers == 1:
        for record in selected:
            prepare_source(record)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for _ in pool.map(prepare_source, selected):
                pass


if __name__ == "__main__":
    main()
