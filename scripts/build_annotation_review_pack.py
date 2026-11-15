"""Build timestamped visual review packs from non-test runs.

The pack is a human-review aid, not an automatic annotator. It deliberately
excludes test runs so annotation criteria can be checked without exposing
held-out footage or labels during development. By default it uses development
runs; training runs can be explicitly added for training-label review.
"""

from __future__ import annotations

import csv
import datetime as dt
import argparse
import bisect
import pathlib
import tempfile
import zipfile

import cv2
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SPLIT_FILE = ROOT / "data" / "manifests" / "splits.csv"
OUTPUT_ROOT = ROOT / "data" / "processed"
TILE_SIZE = (480, 270)
TILE_LABEL_H = 34
COLS = 3
GAP = 10
HEADER_H = 48


def timestamp_value(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d-%H-%M-%S_%f")


def read_split_rows() -> list[dict[str, str]]:
    with SPLIT_FILE.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def find_camera_pair(archive: zipfile.ZipFile, run_id: str) -> tuple[zipfile.ZipInfo, zipfile.ZipInfo]:
    files = {
        pathlib.PurePosixPath(item.filename).name: item
        for item in archive.infolist()
        if item.filename.startswith(f"{run_id}/") and not item.is_dir()
    }
    video_name = f"VisualCamera7_{run_id}.mp4"
    timing_name = f"VisualCamera7_{run_id}_frame-timing.csv"
    if video_name not in files or timing_name not in files:
        raise FileNotFoundError(f"VisualCamera7 video/timing pair missing for {run_id}")
    return files[video_name], files[timing_name]


def make_tiles(video: pathlib.Path, stamps: list[dict[str, str]], sample_seconds: float, start_frame: int | None = None, end_frame: int | None = None) -> tuple[list[np.ndarray], list[int]]:
    times = [timestamp_value(row["Timestamp"]) for row in stamps]
    if not times:
        raise ValueError(f"No timestamps for {video.name}")
    first = 0 if start_frame is None else start_frame
    last = len(stamps) - 1 if end_frame is None else end_frame
    if first < 0 or last < first or last >= len(stamps):
        raise ValueError(f"Invalid requested frame interval {first}:{last} for {video.name} ({len(stamps)} frames)")
    duration = (times[last] - times[first]).total_seconds()
    targets = np.arange(0.0, duration + sample_seconds, sample_seconds)
    indices = {first, last}
    for target in targets:
        target_time = times[first] + dt.timedelta(seconds=float(target))
        index = bisect.bisect_left(times, target_time)
        index = max(first, min(index, last))
        if index >= len(times):
            index = len(times) - 1
        elif index > first and abs((times[index - 1] - target_time).total_seconds()) <= abs((times[index] - target_time).total_seconds()):
            index -= 1
        indices.add(index)

    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open {video.name}")
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count != len(stamps):
        capture.release()
        raise ValueError(f"Frame/timestamp mismatch for {video.name}: {frame_count} != {len(stamps)}")

    tiles: list[np.ndarray] = []
    for index in sorted(indices):
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        decoded, frame = capture.read()
        if not decoded or frame is None:
            capture.release()
            raise RuntimeError(f"Could not decode frame {index} from {video.name}")
        tile = cv2.resize(frame, TILE_SIZE, interpolation=cv2.INTER_AREA)
        cv2.rectangle(tile, (0, TILE_SIZE[1] - TILE_LABEL_H), (TILE_SIZE[0], TILE_SIZE[1]), (24, 35, 38), -1)
        label = f"frame {index} | {stamps[index]['Timestamp']}"
        cv2.putText(tile, label, (8, TILE_SIZE[1] - 11), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (245, 243, 236), 1, cv2.LINE_AA)
        tiles.append(tile)
    capture.release()
    return tiles, sorted(indices)


def write_sheet(output: pathlib.Path, run_id: str, split: str, source_archive: str, sample_seconds: float, tiles: list[np.ndarray], frame_range: tuple[int, int] | None = None) -> pathlib.Path:
    tile_h = TILE_SIZE[1]
    tile_w = TILE_SIZE[0]
    rows = (len(tiles) + COLS - 1) // COLS
    canvas = np.full(
        (HEADER_H + GAP + rows * (tile_h + GAP), GAP + COLS * (tile_w + GAP), 3),
        (245, 244, 238),
        dtype=np.uint8,
    )
    title = f"{run_id} | {split} only | {source_archive} | {sample_seconds:g}-second review samples"
    if frame_range:
        title += f" | frames {frame_range[0]}-{frame_range[1]}"
    cv2.putText(canvas, title[:110], (GAP, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (32, 47, 48), 1, cv2.LINE_AA)
    for offset, tile in enumerate(tiles):
        row, col = divmod(offset, COLS)
        y = HEADER_H + GAP + row * (tile_h + GAP)
        x = GAP + col * (tile_w + GAP)
        canvas[y:y + tile_h, x:x + tile_w] = tile
    suffix = f"-frames-{frame_range[0]}-{frame_range[1]}" if frame_range else ""
    path = output / f"{run_id}{suffix}-review-sheet.jpg"
    if not cv2.imwrite(str(path), canvas, [cv2.IMWRITE_JPEG_QUALITY, 88]):
        raise IOError(f"Could not write {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=1.0, help="Approximate sampling interval in source seconds (default: 1).")
    parser.add_argument("--splits", nargs="+", choices=("train", "validation"), default=["validation"], help="Source-run splits to review. Test is deliberately unavailable.")
    parser.add_argument("--runs", nargs="*", help="Optional source sequence IDs to render from the selected non-test splits.")
    parser.add_argument("--start-frame", type=int, help="Optional inclusive start frame for one focused clip review; requires --end-frame and one --runs ID.")
    parser.add_argument("--end-frame", type=int, help="Optional inclusive end frame for one focused clip review; requires --start-frame and one --runs ID.")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")
    if (args.start_frame is None) != (args.end_frame is None):
        parser.error("--start-frame and --end-frame must be supplied together")
    if args.start_frame is not None and (not args.runs or len(args.runs) != 1):
        parser.error("Focused frame ranges require exactly one --runs ID")

    rows = read_split_rows()
    development = [row for row in rows if row["split"] in set(args.splits)]
    if args.runs:
        unknown = sorted(set(args.runs) - {row["sequence_id"] for row in development})
        if unknown:
            parser.error(f"Only selected train/development runs are permitted; unknown or test IDs: {', '.join(unknown)}")
        development = [row for row in development if row["sequence_id"] in set(args.runs)]
    if not development:
        raise ValueError("No development runs in split manifest")

    output = OUTPUT_ROOT / f"annotation-review-{args.interval:g}s"
    output.mkdir(parents=True, exist_ok=True)
    archive_paths = sorted({row["source_archive"] for row in development})
    archives = {name: zipfile.ZipFile(ROOT / pathlib.Path(name)) for name in archive_paths}
    manifest_path = output / "review-pack-manifest.csv"
    manifest_fields = ["sequence_id", "split", "source_archive", "source_label_scope", "camera_view", "frame_index", "source_timestamp", "sample_interval_seconds", "review_image"]
    try:
        with manifest_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=manifest_fields)
            writer.writeheader()
            with tempfile.TemporaryDirectory(prefix="livecross-review-pack-", dir=RAW / "inspection") as temp_dir:
                scratch = pathlib.Path(temp_dir)
                for row in development:
                    archive = archives[row["source_archive"]]
                    video_info, timing_info = find_camera_pair(archive, row["sequence_id"])
                    with archive.open(timing_info) as source:
                        stamps = list(csv.DictReader(line.decode("utf-8-sig") for line in source))
                    video_path = scratch / f"{row['sequence_id']}.mp4"
                    with archive.open(video_info) as source, video_path.open("wb") as target:
                        while chunk := source.read(8 * 1024 * 1024):
                            target.write(chunk)
                    tiles, indices = make_tiles(video_path, stamps, args.interval, args.start_frame, args.end_frame)
                    frame_range = (args.start_frame, args.end_frame) if args.start_frame is not None else None
                    sheet_path = write_sheet(output, row["sequence_id"], row["split"], pathlib.PurePosixPath(row["source_archive"]).name, args.interval, tiles, frame_range)
                    for index in indices:
                        writer.writerow({
                            "sequence_id": row["sequence_id"],
                            "split": row["split"],
                            "source_archive": row["source_archive"],
                            "source_label_scope": row["source_label_scope"],
                            "camera_view": "VisualCamera7",
                            "frame_index": index,
                            "source_timestamp": stamps[index]["Timestamp"],
                            "sample_interval_seconds": args.interval,
                            "review_image": sheet_path.name,
                        })
    finally:
        for archive in archives.values():
            archive.close()
    print(f"Wrote non-test annotation review pack: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
