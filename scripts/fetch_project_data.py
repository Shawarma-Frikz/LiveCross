"""Download the public data sources planned for LiveCross.

Large Socrata file attachments are fetched in resumable-by-chunk byte ranges.
The TGSIM CSV endpoint is streamed because it does not advertise byte ranges.
All downloaded files stay under the Git-ignored data/raw directory.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CHUNK_SIZE = 32 * 1024 * 1024
WORKERS = 8
SOURCES = [
    {
        "name": "DOT ISC Stage 1B full validation",
        "filename": "validation-full.zip",
        "size": 28_642_566_098,
        "url": "https://data.transportation.gov/api/views/j58q-ymi4/files/df6e4db6-abfc-44bf-898d-e489760efb06?download=true&filename=Validation%20Data.zip",
        "archive": True,
    },
    {
        "name": "DOT ISC Stage 1B public training sample 1",
        "filename": "training-sample-1.zip",
        "size": 8_161_594_056,
        "url": "https://data.transportation.gov/api/views/vq7s-mv3v/files/77757448-b184-4c88-b6b7-44a4cb2ebecc?download=true&filename=Training%20Data%20Sample%201.zip",
        "archive": True,
    },
    {
        "name": "DOT ISC Stage 1B public training sample 2",
        "filename": "training-sample-2.zip",
        "size": 5_148_222_990,
        "url": "https://data.transportation.gov/api/views/vq7s-mv3v/files/997606a0-4c55-4c41-a550-2c0b4c3f1819?download=true&filename=Training%20Data%20Sample%202.zip",
        "archive": True,
    },
    {
        "name": "DOT ISC Stage 1B calibration data",
        "filename": "calibration.zip",
        "size": 8_502_530_399,
        "url": "https://data.transportation.gov/api/views/j58q-ymi4/files/d177dd7f-9093-4e6b-9a30-dbe7067c93f3?download=true&filename=Calibration%20Data_8GB.zip",
        "archive": True,
    },
]
TGSIM = {
    "name": "FHWA TGSIM Foggy Bottom trajectories",
    "filename": "tgsim-foggy-bottom.csv",
    "url": "https://data.transportation.gov/api/v3/views/brzy-6zfh/export.csv?accessType=DOWNLOAD",
}


def fetch_range(url: str, start: int, end: int, destination: Path) -> int:
    expected = end - start + 1
    if destination.exists() and destination.stat().st_size == expected:
        return expected
    destination.unlink(missing_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, 9):
        try:
            request = urllib.request.Request(
                url,
                headers={"Range": f"bytes={start}-{end}", "User-Agent": "LiveCross-course-project/1.0"},
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                if response.status != 206:
                    raise RuntimeError(f"Expected HTTP 206 for bytes {start}-{end}; got {response.status}")
                content_range = response.headers.get("Content-Range", "")
                if not content_range.startswith(f"bytes {start}-{end}/"):
                    raise RuntimeError(f"Unexpected Content-Range: {content_range!r}")
                received = 0
                with destination.open("wb") as output:
                    while block := response.read(1024 * 1024):
                        output.write(block)
                        received += len(block)
                if received != expected:
                    raise RuntimeError(f"Expected {expected} bytes; got {received}")
                return received
        except Exception as error:  # retry transient portal/network failures
            last_error = error
            destination.unlink(missing_ok=True)
            if attempt < 8:
                time.sleep(min(30, 2**attempt))
    raise RuntimeError(f"Range {start}-{end} failed after retries: {last_error}")


def download_attachment(source: dict[str, object]) -> dict[str, object]:
    filename = str(source["filename"])
    total = int(source["size"])
    url = str(source["url"])
    target = RAW / filename
    already_complete = target.exists() and target.stat().st_size == total
    previously_verified = False
    manifest_path = RAW / "download-manifest.json"
    if already_complete and manifest_path.exists():
        try:
            old = json.loads(manifest_path.read_text(encoding="utf-8"))
            previously_verified = any(
                asset.get("filename") == filename and asset.get("bytes") == total
                for asset in old.get("assets", [])
            )
        except (OSError, json.JSONDecodeError, AttributeError):
            previously_verified = False
    if already_complete:
        print(f"Already complete: {filename} ({total:,} bytes)", flush=True)
    else:
        parts = RAW / f".{filename}.parts"
        parts.mkdir(parents=True, exist_ok=True)
        spans = [(start, min(start + CHUNK_SIZE, total) - 1) for start in range(0, total, CHUNK_SIZE)]
        print(f"Downloading {source['name']}: {total:,} bytes in {len(spans)} chunks", flush=True)
        completed = sum(
            min(CHUNK_SIZE, total - start)
            for start, _ in spans
            if (parts / f"{start:012d}.part").exists()
            and (parts / f"{start:012d}.part").stat().st_size == min(CHUNK_SIZE, total - start)
        )
        last_report = -1
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {
                pool.submit(fetch_range, url, start, end, parts / f"{start:012d}.part"): (start, end)
                for start, end in spans
            }
            for future in as_completed(futures):
                completed += future.result()
                percent = int(completed * 100 / total)
                if percent != last_report:
                    print(f"{filename}: {percent}% ({completed:,}/{total:,} bytes)", flush=True)
                    last_report = percent
        assembled = target.with_suffix(target.suffix + ".assembling")
        with assembled.open("wb") as output:
            for start, _ in spans:
                with (parts / f"{start:012d}.part").open("rb") as piece:
                    while block := piece.read(8 * 1024 * 1024):
                        output.write(block)
        if assembled.stat().st_size != total:
            raise RuntimeError(f"Assembled {filename} has wrong size: {assembled.stat().st_size}")
        os.replace(assembled, target)
        for part in parts.glob("*.part"):
            part.unlink()
        parts.rmdir()
        print(f"Saved {filename}: {total:,} bytes", flush=True)

    if bool(source["archive"]) and not previously_verified:
        print(f"Checking ZIP directory: {filename}", flush=True)
        with zipfile.ZipFile(target) as archive:
            members = archive.infolist()
            bad_member = archive.testzip()
            if bad_member:
                raise RuntimeError(f"CRC failure in {filename}: {bad_member}")
        print(f"ZIP verified: {filename}; {len(members):,} members", flush=True)
    elif bool(source["archive"]):
        print(f"Previously size- and CRC-verified ZIP: {filename}", flush=True)
    return {"name": source["name"], "filename": filename, "bytes": target.stat().st_size}


def download_tgsim() -> dict[str, object]:
    target = RAW / str(TGSIM["filename"])
    partial = target.with_suffix(target.suffix + ".part")
    # The official catalog describes this export as roughly 350 MB; a smaller
    # file is likely an interrupted transfer, not a complete dataset.
    if target.exists() and target.stat().st_size >= 300_000_000:
        return {"name": TGSIM["name"], "filename": target.name, "bytes": target.stat().st_size}
    partial.unlink(missing_ok=True)
    request = urllib.request.Request(str(TGSIM["url"]), headers={"User-Agent": "LiveCross-course-project/1.0"})
    print(f"Streaming {TGSIM['name']} (the portal uses chunked transfer)", flush=True)
    received = 0
    last_report = 0
    with urllib.request.urlopen(request, timeout=180) as response, partial.open("wb") as output:
        while block := response.read(4 * 1024 * 1024):
            output.write(block)
            received += len(block)
            if received - last_report >= 64 * 1024 * 1024:
                print(f"TGSIM: {received / 1_000_000:.0f} MB received", flush=True)
                last_report = received
    if received < 300_000_000:
        raise RuntimeError(f"TGSIM export unexpectedly small: {received:,} bytes")
    os.replace(partial, target)
    return {"name": TGSIM["name"], "filename": target.name, "bytes": received}


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    try:
        for source in SOURCES:
            manifest.append(download_attachment(source))
        manifest.append(download_tgsim())
    except (OSError, urllib.error.URLError, RuntimeError, zipfile.BadZipFile) as error:
        print(f"Download/verification stopped: {error}", file=sys.stderr, flush=True)
        return 1
    record = {
        "accessed_utc": datetime.now(timezone.utc).isoformat(),
        "assets": manifest,
        "notes": [
            "DOT training archive (~1 TB) was not downloaded: it is unlabeled and not needed for the defined evaluation.",
            "TGSIM contains trajectories and is not a substitute for labeled RGB video.",
            "Raw data is excluded from Git; follow each source's terms and citation requirements.",
        ],
    }
    (RAW / "download-manifest.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("All planned downloads completed and verified.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
