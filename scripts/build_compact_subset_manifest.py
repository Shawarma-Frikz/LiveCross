"""Select and audit a compact, complete-run DOT validation subset for LiveCross.

The source label is run/scenario-level only. This script does not create event
labels, assign train/dev/test splits, or claim camera-specific ground truth.
It writes a small manifest and summary; source video stays in the ZIP archive.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import pathlib
import tempfile
import zipfile
from collections import Counter, defaultdict

import cv2


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SOURCE_ARCHIVE = RAW / "validation-full.zip"
MANIFEST = ROOT / "data" / "manifests" / "compact-subset.csv"
REPORT = ROOT / "results" / "audits" / "compact-subset-audit.json"
CAMERA = 7

# Five source-positive and five source-negative complete runs. The selection
# was made from the 41-run validation inventory to balance source label and
# reviewed midpoint lighting (3 daylight + 2 low-light in each source class),
# while keeping the summed timestamp spans similar. Midpoint-light judgments
# are descriptive sampling strata, not dataset labels or ground truth.
SELECTED = {
    "Run_1290": {"label": "conflict", "midpoint_light": "daylight"},
    "Run_359": {"label": "conflict", "midpoint_light": "daylight"},
    "Run_315": {"label": "conflict", "midpoint_light": "low-light"},
    "Run_1023": {"label": "conflict", "midpoint_light": "low-light"},
    "Run_856": {"label": "conflict", "midpoint_light": "daylight"},
    "Run_179": {"label": "no conflict", "midpoint_light": "low-light"},
    "Run_761": {"label": "no conflict", "midpoint_light": "daylight"},
    "Run_410": {"label": "no conflict", "midpoint_light": "daylight"},
    "Run_48": {"label": "no conflict", "midpoint_light": "daylight"},
    "Run_965": {"label": "no conflict", "midpoint_light": "low-light"},
}

FIELDS = [
    "subset_id",
    "source_archive",
    "source_run_id",
    "source_label",
    "source_label_scope",
    "selected_view",
    "source_video_path",
    "video_uncompressed_bytes",
    "video_frame_count",
    "video_reported_fps",
    "video_width",
    "video_height",
    "midpoint_frame_decoded",
    "midpoint_review_frame_index",
    "midpoint_review_timestamp_source",
    "timestamp_csv_path",
    "timestamp_row_count",
    "timestamp_timezone",
    "timestamp_first_source",
    "timestamp_last_source",
    "timestamp_span_seconds",
    "timestamp_mean_interval_ms",
    "timestamp_min_interval_ms",
    "timestamp_max_interval_ms",
    "reviewed_midpoint_light",
    "sequence_integrity",
    "split_assignment",
    "selection_note",
]


def member_for(archive: zipfile.ZipFile, suffix: str) -> zipfile.ZipInfo:
    matches = [item for item in archive.infolist() if item.filename.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one archive member ending in {suffix!r}; found {len(matches)}")
    return matches[0]


def parse_timestamp(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d-%H-%M-%S_%f")


def inspect_video(archive: zipfile.ZipFile, info: zipfile.ZipInfo, scratch: pathlib.Path) -> dict:
    video_path = scratch / pathlib.PurePosixPath(info.filename).name
    with archive.open(info) as source, video_path.open("wb") as destination:
        while chunk := source.read(8 * 1024 * 1024):
            destination.write(chunk)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"OpenCV could not open {info.filename}")
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_count // 2))
    decoded, _ = capture.read()
    capture.release()
    video_path.unlink()
    if frame_count <= 0 or width <= 0 or height <= 0 or not decoded:
        raise RuntimeError(f"Video metadata or midpoint decode failed for {info.filename}")
    return {
        "uncompressed_bytes": info.file_size,
        "frame_count": frame_count,
        "midpoint_frame_index": max(0, frame_count // 2),
        "reported_fps": fps,
        "width": width,
        "height": height,
        "midpoint_frame_decoded": bool(decoded),
    }


def main() -> None:
    if not SOURCE_ARCHIVE.is_file():
        raise FileNotFoundError(
            f"Missing {SOURCE_ARCHIVE.relative_to(ROOT)}. Download the DOT full validation archive first."
        )

    rows: list[dict] = []
    available_labels: dict[str, str] = {}
    with zipfile.ZipFile(SOURCE_ARCHIVE) as archive:
        label_info = member_for(archive, "conflict_no_conflict_labels_all_validation_runs.csv")
        with archive.open(label_info) as raw:
            labels = list(csv.DictReader(raw.read().decode("utf-8-sig").splitlines()))
        available_labels = {row["Run ID"]: row["Conflict_No_Conflict_Label"] for row in labels}
        counts = Counter(available_labels.values())
        if counts != Counter({"conflict": 12, "no conflict": 29}):
            raise ValueError(f"Full validation run-label inventory changed: {dict(counts)}")
        missing_runs = sorted(set(SELECTED) - set(available_labels))
        if missing_runs:
            raise ValueError(f"Selected source runs are missing from the validation labels: {missing_runs}")

        inspection = RAW / "inspection"
        inspection.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="livecross-subset-", dir=inspection) as temp:
            scratch = pathlib.Path(temp)
            for index, (run_id, selection) in enumerate(SELECTED.items(), start=1):
                source_label = available_labels[run_id]
                if source_label != selection["label"]:
                    raise ValueError(f"Unexpected source label for {run_id}: {source_label}")
                video = member_for(archive, f"VisualCamera{CAMERA}_{run_id}.mp4")
                timing = member_for(archive, f"VisualCamera{CAMERA}_{run_id}_frame-timing.csv")
                with archive.open(timing) as raw:
                    timestamp_rows = list(csv.DictReader(raw.read().decode("utf-8-sig").splitlines()))
                stamps = [parse_timestamp(row["Timestamp"]) for row in timestamp_rows]
                intervals = [(b - a).total_seconds() for a, b in zip(stamps, stamps[1:])]
                if not stamps or not intervals or not all(value > 0 for value in intervals):
                    raise ValueError(f"Missing or non-monotonic timestamps in {timing.filename}")
                metadata = inspect_video(archive, video, scratch)
                if metadata["frame_count"] != len(timestamp_rows):
                    raise ValueError(
                        f"Frame/timestamp row mismatch for {run_id}: "
                        f"{metadata['frame_count']} vs {len(timestamp_rows)}"
                    )
                rows.append({
                    "subset_id": f"DOTV-{index:02d}",
                    "source_archive": SOURCE_ARCHIVE.relative_to(ROOT).as_posix(),
                    "source_run_id": run_id,
                    "source_label": source_label,
                    "source_label_scope": "run/scenario; not an event or actor-pair label",
                    "selected_view": f"VisualCamera{CAMERA}",
                    "source_video_path": video.filename,
                    "video_uncompressed_bytes": metadata["uncompressed_bytes"],
                    "video_frame_count": metadata["frame_count"],
                    "video_reported_fps": metadata["reported_fps"],
                    "video_width": metadata["width"],
                    "video_height": metadata["height"],
                    "midpoint_frame_decoded": metadata["midpoint_frame_decoded"],
                    "midpoint_review_frame_index": metadata["midpoint_frame_index"],
                    "midpoint_review_timestamp_source": timestamp_rows[metadata["midpoint_frame_index"]]["Timestamp"],
                    "timestamp_csv_path": timing.filename,
                    "timestamp_row_count": len(timestamp_rows),
                    "timestamp_timezone": "not specified in source CSV",
                    "timestamp_first_source": timestamp_rows[0]["Timestamp"],
                    "timestamp_last_source": timestamp_rows[-1]["Timestamp"],
                    "timestamp_span_seconds": round((stamps[-1] - stamps[0]).total_seconds(), 6),
                    "timestamp_mean_interval_ms": round(sum(intervals) / len(intervals) * 1000, 3),
                    "timestamp_min_interval_ms": round(min(intervals) * 1000, 3),
                    "timestamp_max_interval_ms": round(max(intervals) * 1000, 3),
                    "reviewed_midpoint_light": selection["midpoint_light"],
                    "sequence_integrity": "complete camera stream; no temporal crop",
                    "split_assignment": "unassigned; validation candidate pool; preserve source run as the split group",
                    "selection_note": "Balanced compact candidate pool; source label remains run-level.",
                })

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    by_label = Counter(row["source_label"] for row in rows)
    by_label_light: dict[str, Counter] = defaultdict(Counter)
    by_camera = Counter(row["selected_view"] for row in rows)
    duration_by_label: dict[str, float] = defaultdict(float)
    for row in rows:
        by_label_light[row["source_label"]][row["reviewed_midpoint_light"]] += 1
        duration_by_label[row["source_label"]] += row["timestamp_span_seconds"]
    report = {
        "audit_date": dt.date.today().isoformat(),
        "subset_id": "LiveCross-DOT-validation-compact-v1",
        "source_archive": SOURCE_ARCHIVE.relative_to(ROOT).as_posix(),
        "source_archive_bytes": SOURCE_ARCHIVE.stat().st_size,
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "selection_rule": [
            "Choose five DOT source-conflict and five source-no-conflict runs from the 41-run validation archive.",
            "Use VisualCamera7 consistently (same recorded fixed roadside view across selected runs).",
            "Balance reviewed midpoint appearance at three daylight and two low-light runs in each source-label class.",
            "Retain each selected camera stream in full; do not sample or crop temporal segments.",
            "Leave split assignment unassigned for the separate sequence-level split task.",
        ],
        "source_label_inventory_full_validation": dict(sorted(counts.items())),
        "selected_run_count": len(rows),
        "selected_source_run_label_counts": dict(sorted(by_label.items())),
        "selected_counts_by_source_label_and_reviewed_midpoint_light": {
            label: dict(sorted(counter.items())) for label, counter in sorted(by_label_light.items())
        },
        "selected_camera_counts": dict(sorted(by_camera.items())),
        "resolution_counts": dict(sorted(Counter(f"{r['video_width']}x{r['video_height']}" for r in rows).items())),
        "timestamp_span_seconds_by_source_label": {
            label: round(total, 6) for label, total in sorted(duration_by_label.items())
        },
        "total_selected_timestamp_span_seconds": round(sum(r["timestamp_span_seconds"] for r in rows), 6),
        "total_selected_video_bytes_uncompressed": sum(r["video_uncompressed_bytes"] for r in rows),
        "all_midpoint_frames_decoded": all(r["midpoint_frame_decoded"] for r in rows),
        "all_frame_counts_match_timestamp_rows": all(r["video_frame_count"] == r["timestamp_row_count"] for r in rows),
        "split_status": "unassigned; candidate pool from the official validation archive; no train/dev/test assignment is implied",
        "label_limit": "Conflict/no-conflict values are DOT run/scenario labels only. They do not identify event times, actor pairs, or per-camera event labels. Event-level labels must be created separately under the manual annotation protocol.",
        "scope_limit": "This compact DOT subset covers only DOT's VRU–vehicle scenario domain. It does not supply source ground truth for vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object events.",
        "runs": [
            {
                "run_id": r["source_run_id"],
                "source_label": r["source_label"],
                "view": r["selected_view"],
                "midpoint_light_review": r["reviewed_midpoint_light"],
                "midpoint_review_frame_index": r["midpoint_review_frame_index"],
                "midpoint_review_timestamp_source": r["midpoint_review_timestamp_source"],
                "timestamp_span_seconds": r["timestamp_span_seconds"],
                "frame_count": r["video_frame_count"],
                "video_bytes": r["video_uncompressed_bytes"],
            }
            for r in rows
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
