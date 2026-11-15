"""Create a repeatable inventory and timing audit for the local DOT sample.

This script records machine-checkable facts only. Human label interpretation,
camera-projection decisions, and annotation judgments remain in docs/.
The DOT archives must already exist under data/raw/; this script downloads nothing.
"""

from __future__ import annotations

import csv
import json
import re
import statistics
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INSPECTION = RAW / "inspection"
OUTPUT = ROOT / "results" / "audits" / "dot-sample-audit.json"

SAMPLE_ZIP = RAW / "validation-sample.zip"
VIDEO = INSPECTION / "VisualCamera7_Run_1003.mp4"
TIMING_CSV = INSPECTION / "VisualCamera7_Run_1003_frame-timing.csv"
GROUND_TRUTH_CSV = INSPECTION / "Run_1003_GT.csv"
RUN_LABELS_CSV = INSPECTION / "conflict_no_conflict_labels_sample_validation_runs.csv"


def require_file(path: Path) -> None:
    if not path.is_file():
        relative = path.relative_to(ROOT)
        raise FileNotFoundError(
            f"Required local input is missing: {relative}\n"
            "Download/extract the DOT validation sample and representative Run_1003 "
            "inspection files first; see docs/dataset-access.md."
        )


def inspect_archive() -> dict[str, object]:
    with zipfile.ZipFile(SAMPLE_ZIP) as archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        extensions = Counter(Path(info.filename).suffix.lower() or "[no extension]" for info in members)
        run_ids = sorted(
            {
                component
                for info in members
                for component in Path(info.filename).parts[:-1]
                if re.fullmatch(r"Run_\d+", component)
            }
        )
        return {
            "path": SAMPLE_ZIP.relative_to(ROOT).as_posix(),
            "bytes": SAMPLE_ZIP.stat().st_size,
            "member_count": len(members),
            "members_by_extension": dict(sorted(extensions.items())),
            "run_ids": run_ids,
        }


def inspect_labels() -> dict[str, object]:
    with RUN_LABELS_CSV.open("r", newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {"Run ID", "Conflict_No_Conflict_Label"}.issubset(rows[0]):
        raise ValueError("Run-label CSV is missing the expected DOT columns.")
    labels = Counter(row["Conflict_No_Conflict_Label"].strip() for row in rows)
    return {
        "path": RUN_LABELS_CSV.relative_to(ROOT).as_posix(),
        "annotation_level": "run-level (semantic interpretation documented separately)",
        "rows": len(rows),
        "labels_by_original_value": dict(sorted(labels.items())),
        "runs_by_original_value": {
            label: sorted(row["Run ID"].strip() for row in rows if row["Conflict_No_Conflict_Label"].strip() == label)
            for label in sorted(labels)
        },
    }


def inspect_video_and_timing() -> dict[str, object]:
    capture = cv2.VideoCapture(str(VIDEO))
    if not capture.isOpened():
        raise RuntimeError(f"OpenCV could not open {VIDEO.relative_to(ROOT)}")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    reported_fps = float(capture.get(cv2.CAP_PROP_FPS))
    reported_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    decoded_frames = 0
    while True:
        ok, _ = capture.read()
        if not ok:
            break
        decoded_frames += 1
    capture.release()

    with TIMING_CSV.open("r", newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {"Image_number", "Timestamp"}.issubset(rows[0]):
        raise ValueError("Frame-timing CSV is missing the expected DOT columns.")
    timestamps = [
        datetime.strptime(row["Timestamp"], "%Y-%m-%d-%H-%M-%S_%f")
        for row in rows
    ]
    intervals = [(later - earlier).total_seconds() for earlier, later in zip(timestamps, timestamps[1:])]
    span = (timestamps[-1] - timestamps[0]).total_seconds()
    mean_interval = statistics.mean(intervals) if intervals else None

    return {
        "video": {
            "path": VIDEO.relative_to(ROOT).as_posix(),
            "bytes": VIDEO.stat().st_size,
            "width": width,
            "height": height,
            "container_fps": reported_fps,
            "container_frame_count": reported_frames,
            "decoded_frame_count": decoded_frames,
        },
        "frame_timing_csv": {
            "path": TIMING_CSV.relative_to(ROOT).as_posix(),
            "bytes": TIMING_CSV.stat().st_size,
            "rows": len(rows),
            "first_timestamp": rows[0]["Timestamp"],
            "last_timestamp": rows[-1]["Timestamp"],
            "span_seconds": round(span, 6),
            "strictly_increasing": all(interval > 0 for interval in intervals),
            "mean_interval_ms": round(mean_interval * 1000, 3) if mean_interval is not None else None,
            "median_interval_ms": round(statistics.median(intervals) * 1000, 3) if intervals else None,
            "minimum_interval_ms": round(min(intervals) * 1000, 3) if intervals else None,
            "maximum_interval_ms": round(max(intervals) * 1000, 3) if intervals else None,
            "timestamp_rate_hz_from_mean_interval": round(1 / mean_interval, 3) if mean_interval else None,
        },
        "frame_count_matches_timestamp_rows": decoded_frames == len(rows),
    }


def inspect_ground_truth() -> dict[str, object]:
    with GROUND_TRUTH_CSV.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    classes = sorted(name[:-5] for name in fieldnames if name.endswith("_xctr"))
    nonempty_centers = {
        class_name: sum(bool(row.get(f"{class_name}_xctr", "").strip()) for row in rows)
        for class_name in classes
    }
    return {
        "path": GROUND_TRUTH_CSV.relative_to(ROOT).as_posix(),
        "bytes": GROUND_TRUTH_CSV.stat().st_size,
        "rows": len(rows),
        "subclass_blocks_in_this_run": classes,
        "rows_with_nonempty_center_by_subclass": nonempty_centers,
        "coordinate_frame_and_projection_status": "See docs/data-card.md and docs/projection-audit.md; not inferred by this script.",
    }


def main() -> int:
    for path in (SAMPLE_ZIP, VIDEO, TIMING_CSV, GROUND_TRUTH_CSV, RUN_LABELS_CSV):
        require_file(path)

    report = {
        "audit_schema": "1.0",
        "scope": "Machine-checkable inventory, video decode, timestamp, and raw-label summary for DOT ISC Stage 1B validation sample.",
        "inputs": {
            "sample_archive": inspect_archive(),
            "run_labels": inspect_labels(),
            "selected_run_camera": inspect_video_and_timing(),
            "selected_run_ground_truth": inspect_ground_truth(),
        },
        "interpretation_boundary": "This report does not convert run-level labels into event labels and does not validate 3D-to-image projection. See docs/event-vocabulary.md and docs/projection-audit.md.",
        "environment": {
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Audit report written to {OUTPUT.relative_to(ROOT)}")
    print(f"Decoded frames: {report['inputs']['selected_run_camera']['video']['decoded_frame_count']}")
    print(f"Timestamp rows: {report['inputs']['selected_run_camera']['frame_timing_csv']['rows']}")
    print(f"Run labels: {report['inputs']['run_labels']['labels_by_original_value']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, RuntimeError, ValueError, zipfile.BadZipFile) as error:
        print(f"Audit failed: {error}", file=sys.stderr)
        raise SystemExit(1)
