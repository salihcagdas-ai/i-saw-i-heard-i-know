import argparse
import hashlib
import json
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urldefrag, urljoin, urlsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE = "https://tidsozluk.aile.gov.tr/"
LETTERS = "ABCÇDEFGHİKLMNOPRSŞTUÜVYZ"


def fetch(url):
    for attempt in range(3):
        time.sleep(0.36)
        try:
            request = Request(url, headers={"User-Agent": "TID academic prototype (local) / 1.0"})
            with urlopen(request, timeout=15) as response:
                if urlsplit(response.geturl()).netloc != urlsplit(BASE).netloc:
                    raise ValueError("Unexpected redirect from the dictionary")
                return response.read()
        except HTTPError as error:
            if error.code not in (408, 429, 502, 503, 504) or attempt == 2:
                raise
            retry_after = error.headers.get("Retry-After", "")
            time.sleep(float(retry_after) if retry_after.isdecimal() else 2 ** attempt)
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def soup(url):
    return BeautifulSoup(fetch(url), "html.parser")


def entries(page):
    for letter in LETTERS:
        listing = soup(urljoin(BASE, f"tr/Alfabetik/Arama/{quote(letter)}?p={page}"))
        for item in listing.select(".rezult_item a[href]"):
            url = urljoin(BASE, item["href"])
            if urlsplit(url).netloc == urlsplit(BASE).netloc:
                yield url


def examples(entry):
    for row in soup(entry).select(".ornek"):
        video = row.select_one('video source[src*="/ornek/"]')
        labels = {
            label.get_text(strip=True).split(":")[0].strip(): label.find_next_sibling("div")
            for label in row.select(".ornek_txt_title")
        }
        translation = labels.get("Çeviri")
        if video is None or translation is None:
            continue
        text = " ".join(translation.stripped_strings)
        if len(text.split()) < 3:
            continue
        url = urldefrag(urljoin(BASE, video["src"])).url
        if urlsplit(url).netloc != urlsplit(BASE).netloc:
            continue
        transcript = labels.get("TRANSKRİPSİYON")
        gloss = " ".join(transcript.stripped_strings) if transcript is not None else ""
        yield url, text, gloss


def video_id(url):
    return "dictionary-" + hashlib.sha256(url.encode()).hexdigest()[:16]


def collect_glosses(directory):
    entries_with_videos = {}
    with (directory / "dictionary.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            entries_with_videos.setdefault(record["entry"], set()).add(record["id"])
    found = {}
    for entry, identifiers in entries_with_videos.items():
        for video, _, gloss in examples(entry):
            identifier = video_id(video)
            if gloss and identifier in identifiers:
                found[identifier] = gloss
    target = directory / "glosses.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(found, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)
    print(f"Dictionary videos with sign-order labels: {len(found)}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--glosses", action="store_true")
    args = parser.parse_args()
    if args.limit < 1 or args.pages < 1:
        parser.error("Expected positive --limit and --pages")
    args.output.mkdir(parents=True, exist_ok=True)
    if args.glosses:
        collect_glosses(args.output)
        return
    log = args.output / "dictionary.jsonl"
    seen = set()
    if log.is_file():
        with log.open(encoding="utf-8") as stream:
            seen = {json.loads(line)["id"] for line in stream if line.strip()}
    seen_entries = set()
    with log.open("a", encoding="utf-8") as stream:
        for page in range(1, args.pages + 1):
            for entry in entries(page):
                if len(seen) >= args.limit:
                    return
                if entry in seen_entries:
                    continue
                seen_entries.add(entry)
                try:
                    for video, text, gloss in examples(entry):
                        identifier = video_id(video)
                        if identifier in seen:
                            continue
                        media = fetch(video)
                        if media[4:8] != b"ftyp":
                            raise ValueError("Expected MP4 media")
                        with tempfile.NamedTemporaryFile(dir=args.output, delete=False) as temporary:
                            temporary.write(media)
                        Path(temporary.name).replace(args.output / f"{identifier}.mp4")
                        record = {"id": identifier, "entry": entry, "text": text, "gloss": gloss}
                        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                        stream.flush()
                        seen.add(identifier)
                        if len(seen) % 25 == 0:
                            print(f"Dictionary videos: {len(seen)}", flush=True)
                        if len(seen) >= args.limit:
                            return
                except (URLError, TimeoutError, ValueError) as error:
                    print(f"Dictionary entry skipped: {error}", flush=True)
    print(f"Dictionary videos: {len(seen)}", flush=True)


if __name__ == "__main__":
    main()
