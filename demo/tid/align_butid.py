"""Create a source-disjoint TİD manifest from BUTID and publisher captions."""

import argparse
import csv
import hashlib
import json
import re
import subprocess
from bisect import bisect_left
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}")
TOLERANCE_MS = 80


def milliseconds(timestamp):
    hours, minutes, seconds = timestamp.split(":")
    return (int(hours) * 3600 + int(minutes) * 60) * 1000 + round(float(seconds) * 1000)


def video_split(video_id):
    bucket = int.from_bytes(hashlib.sha256(video_id.encode()).digest()[:4], "big") % 100
    return "train" if bucket < 90 else "dev" if bucket < 95 else "test"


def crop_box(metadata):
    width, height = metadata["width"], metadata["height"]
    x0, x1 = metadata["bbox"]["bounding_box_x"]
    y0, y1 = metadata["bbox"]["bounding_box_y"]
    if 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height:
        return [x0 / width, y0 / height, x1 / width, y1 / height]
    return None


def read_intervals(index, excluded):
    videos = defaultdict(set)
    for split in ("train", "dev", "test"):
        with (index / f"main.{split}.csv").open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                video_id = row["video_id"]
                if video_id in excluded or not VIDEO_ID.fullmatch(video_id):
                    continue
                start, end = milliseconds(row["start"]), milliseconds(row["end"])
                if start >= 0 and 1000 <= end - start <= 17000:
                    videos[video_id].add((start, end, row["clip_id"]))
    return videos


def download_captions(yt_dlp, url, path):
    try:
        subprocess.run(
            [
                yt_dlp, "--ignore-config", "--no-playlist", "--skip-download",
                "--write-subs", "--no-write-auto-subs", "--sub-langs", "^tr$",
                "--sub-format", "json3", "--socket-timeout", "10", "--retries", "1",
                "-o", str(path.parent / "%(id)s.%(ext)s"), url,
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, timeout=35, text=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "download_failed"
    return "ready" if path.is_file() else "missing_captions"


def match_captions(path, intervals, max_clips, isolated=False):
    captions = defaultdict(set)
    timeline = {}
    for event in json.loads(path.read_text(encoding="utf-8"))["events"]:
        text = " ".join("".join(segment.get("utf8", "") for segment in event.get("segs", [])).split())
        start = event["tStartMs"]
        end = start + event.get("dDurationMs", 0)
        if text and end > start:
            timeline[start] = max(timeline.get(start, start), end)
        if 2 <= len(text.split()) and len(text) <= 180 and not re.search(r"[\[\]<>♪]", text):
            captions[start].add((end, text))
    gaps = {}
    if isolated:
        previous_end = -1000
        timeline_starts = sorted(timeline)
        for index, start in enumerate(timeline_starts):
            next_start = timeline_starts[index + 1] if index + 1 < len(timeline_starts) else float("inf")
            gaps[start] = (start - previous_end, next_start)
            previous_end = max(previous_end, timeline[start])
    starts = sorted(captions)
    matches = []
    previous_end = -1
    for start, end, clip_id in sorted(intervals):
        index = bisect_left(starts, start - TOLERANCE_MS)
        candidates = set()
        while index < len(starts) and starts[index] <= start + TOLERANCE_MS:
            caption_start = starts[index]
            for caption_end, text in captions[caption_start]:
                if abs(caption_end - end) <= TOLERANCE_MS:
                    candidates.add((caption_start, caption_end, text))
            index += 1
        if len(candidates) != 1:
            continue
        caption_start, caption_end, text = candidates.pop()
        if caption_start < previous_end:
            continue
        label = {"id": clip_id, "start": caption_start / 1000, "end": caption_end / 1000, "text": text}
        if isolated:
            gap_before, next_start = gaps[caption_start]
            if gap_before < 500 or next_start - caption_end < 2000 or caption_end - caption_start < 2000:
                continue
            label.update(caption_start=label["start"], caption_end=label["end"])
            label["end"] += 1.5
        matches.append(label)
        previous_end = round(label["end"] * 1000)
    if len(matches) > max_clips:
        last = len(matches) - 1
        matches = [matches[round(i * last / (max_clips - 1))] for i in range(max_clips)]
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path, help="BUTID legacy CSV and bbox.json directory")
    parser.add_argument("captions", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--yt-dlp", help="Download missing publisher captions with this executable")
    parser.add_argument("--source-limit", type=int, default=150)
    parser.add_argument("--max-clips-per-source", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--exclude-video", action="append", default=[])
    parser.add_argument("--isolated", action="store_true", help="Keep isolated captions and pad for interpreter delay")
    args = parser.parse_args()
    if args.source_limit < 1 or args.max_clips_per_source < 2 or args.workers < 1:
        parser.error("Set positive source/worker limits and at least two clips per source")

    boxes = json.loads((args.index / "bbox.json").read_text(encoding="utf-8"))
    crops = {video_id: crop_box(box) for video_id, box in boxes.items()}
    intervals = read_intervals(args.index, set(args.exclude_video))
    eligible = [video_id for video_id in intervals if crops.get(video_id)]
    if not args.yt_dlp:
        eligible = [video_id for video_id in eligible if (args.captions / f"{video_id}.tr.json3").is_file()]
    eligible.sort(key=lambda video_id: (-len(intervals[video_id]), video_id))
    args.captions.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def align(video_id):
        path = args.captions / f"{video_id}.tr.json3"
        url = f"https://www.youtube.com/watch?v={video_id}"
        if not path.is_file():
            status = download_captions(args.yt_dlp, url, path)
            if status != "ready":
                return video_id, status, None
        try:
            labels = match_captions(path, intervals[video_id], args.max_clips_per_source, args.isolated)
        except (ValueError, KeyError):
            return video_id, "invalid_captions", None
        if not labels:
            return video_id, "no_matching_timestamps", None
        return video_id, "matched", {
            "id": video_id, "split": video_split(video_id), "group": f"butid:{video_id}",
            "source": url, "caption_source": "publisher-tr", "crop": crops[video_id], "labels": labels,
        }

    status_counts, split_counts = Counter(), Counter()
    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for video_id, status, record in pool.map(align, eligible[:args.source_limit]):
            status_counts[status] += 1
            if record:
                records.append(record)
                split_counts[record["split"]] += len(record["labels"])
            print(video_id, status, len(record["labels"]) if record else 0, flush=True)

    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "sources": len(records), "clips": sum(split_counts.values()), "splits": split_counts,
        "source_status": status_counts,
    }), flush=True)


if __name__ == "__main__":
    main()
