"""Validate and summarize a versioned LiveCross event annotation table."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import zipfile
from collections import Counter
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[1]
ANNOTATION_DIR = ROOT / "data" / "annotations" / "v1"
EVENTS = ANNOTATION_DIR / "events.csv"
EXCLUSIONS = ANNOTATION_DIR / "exclusions.csv"
SPLITS = ROOT / "data" / "manifests" / "splits.csv"
REVIEW_ROOT = ROOT / "data" / "processed"
OUT = ROOT / "results" / "annotation-summary-v1.json"
PAIR_TYPES = (
    "pedestrian_vehicle",
    "vehicle_vehicle",
)
SPLIT_NAMES = ("train", "validation", "test")
POSITIVE = "potential_conflict"
NEGATIVE = "non_conflict_interaction"


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d-%H-%M-%S_%f")


def main() -> None:
    event_rows = read_csv(EVENTS)
    exclusion_rows = read_csv(EXCLUSIONS)
    split_rows = read_csv(SPLITS)
    split_lookup = {row["sequence_id"]: row for row in split_rows}
    if len(split_lookup) != len(split_rows):
        raise ValueError("Split manifest has duplicate sequence IDs")

    event_ids: set[str] = set()
    timing_cache: dict[tuple[str, str], list[str]] = {}
    for row in event_rows:
        event_id = row["event_id"].strip()
        if not event_id or event_id in event_ids:
            raise ValueError(f"Missing or duplicate event_id: {event_id!r}")
        event_ids.add(event_id)
        if row["pair_type"] not in PAIR_TYPES:
            raise ValueError(f"Unknown pair type in {event_id}: {row['pair_type']}")
        if row["status"] not in (POSITIVE, NEGATIVE, "uncertain"):
            raise ValueError(f"Unknown status in {event_id}: {row['status']}")
        if row["review_stage"] != "student_adjudicated":
            if row["status"] != "uncertain" and row["review_stage"] != "assistant_first_pass_requires_student_adjudication":
                raise ValueError(f"Unadjudicated non-uncertain row has invalid review_stage: {event_id}")
        if row["source_run"] not in split_lookup:
            raise ValueError(f"Run not present in split manifest: {event_id}")
        if split_lookup[row["source_run"]]["split"] != row["split"]:
            raise ValueError(f"Split mismatch in {event_id}")
        if row["split"] == "test":
            raise ValueError(f"Test footage cannot be part of development annotations: {event_id}")
        start_frame = int(row["start_frame"])
        end_frame = int(row["end_frame"])
        if start_frame < 0 or end_frame < start_frame:
            raise ValueError(f"Invalid frame interval in {event_id}")
        start = parse_timestamp(row["start_timestamp"])
        end = parse_timestamp(row["end_timestamp"])
        duration = (end - start).total_seconds()
        if duration < 0 or abs(duration - float(row["window_duration_seconds"])) > 0.002:
            raise ValueError(f"Invalid event window duration in {event_id}")

        # Ground-truth windows must reference the exact source timing rows, not
        # nominal FPS estimates or timestamps copied from another camera/run.
        archive_row = pathlib.Path(split_lookup[row["source_run"]]["source_archive"])
        if archive_row.name != pathlib.Path(row["source_archive"]).name:
            raise ValueError(f"Source archive mismatch in {event_id}")
        archive_path = ROOT / archive_row
        cache_key = (str(archive_path), row["source_run"])
        if cache_key not in timing_cache:
            member = f"{row['source_run']}/VisualCamera7_{row['source_run']}_frame-timing.csv"
            with zipfile.ZipFile(archive_path) as archive:
                try:
                    with archive.open(member) as stream:
                        timing_cache[cache_key] = [
                            line.decode("utf-8-sig").rstrip("\r\n").split(",")[-1].strip().strip('"')
                            for line in stream
                        ][1:]
                except KeyError as error:
                    raise ValueError(f"Source timing CSV missing for {event_id}: {member}") from error
        timestamps = timing_cache[cache_key]
        if end_frame >= len(timestamps):
            raise ValueError(f"Frame interval exceeds source length in {event_id}")
        if timestamps[start_frame] != row["start_timestamp"] or timestamps[end_frame] != row["end_timestamp"]:
            raise ValueError(f"Frame/timestamp mismatch against source CSV in {event_id}")

    exclusion_ids: set[str] = set()
    for row in exclusion_rows:
        exclusion_id = row["exclusion_id"].strip()
        if not exclusion_id or exclusion_id in exclusion_ids:
            raise ValueError(f"Missing or duplicate exclusion_id: {exclusion_id!r}")
        exclusion_ids.add(exclusion_id)
        if row["source_run"] not in split_lookup or split_lookup[row["source_run"]]["split"] != row["split"]:
            raise ValueError(f"Exclusion run/split mismatch: {exclusion_id}")
        if row["split"] == "test":
            raise ValueError(f"Test footage cannot be part of development exclusions: {exclusion_id}")
        start = parse_timestamp(row["source_timestamp_start"])
        end = parse_timestamp(row["source_timestamp_end"])
        if end < start:
            raise ValueError(f"Invalid exclusion time window: {exclusion_id}")

    counts: dict[str, dict[str, dict[str, int | float]]] = {}
    for split in SPLIT_NAMES:
        counts[split] = {}
        for pair_type in PAIR_TYPES:
            selected = [row for row in event_rows if row["split"] == split and row["pair_type"] == pair_type]
            by_status = Counter(row["status"] for row in selected)
            counts[split][pair_type] = {
                "potential_conflict_count": by_status[POSITIVE],
                "non_conflict_interaction_count": by_status[NEGATIVE],
                "uncertain_count": by_status["uncertain"],
                "annotated_window_duration_seconds": round(sum(float(row["window_duration_seconds"]) for row in selected), 6),
            }

    category_gate = {}
    for pair_type in PAIR_TYPES:
        selected = [row for row in event_rows if row["pair_type"] == pair_type]
        positives = [row for row in selected if row["status"] == POSITIVE and row["review_stage"] == "student_adjudicated"]
        negatives = [row for row in selected if row["status"] == NEGATIVE and row["review_stage"] == "student_adjudicated"]
        positive_runs = sorted({row["source_run"] for row in positives})
        negative_runs = sorted({row["source_run"] for row in negatives})
        meets = len(positives) >= 20 and len(negatives) >= 20 and len(set(positive_runs + negative_runs)) >= 5
        category_gate[pair_type] = {
            "adjudicated_potential_conflict_windows": len(positives),
            "adjudicated_non_conflict_windows": len(negatives),
            "distinct_source_runs": len(set(positive_runs + negative_runs)),
            "target_per_status": 20,
            "target_distinct_source_runs": 5,
            "sample_gate_met": meets,
            "reporting_status": "eligible_for_primary_metrics" if meets else "exploratory",
        }

    review_manifests = sorted(REVIEW_ROOT.glob("annotation-review-*s/review-pack-manifest.csv"))
    review_rows = [row for path in review_manifests for row in read_csv(path)]
    pack_inventory_by_run: dict[str, dict] = {}
    for run_id in sorted({row["sequence_id"] for row in review_rows}):
        rows = [row for row in review_rows if row["sequence_id"] == run_id]
        packs = []
        for interval in sorted({float(row["sample_interval_seconds"]) for row in rows}):
            pack_rows = [row for row in rows if float(row["sample_interval_seconds"]) == interval]
            times = [parse_timestamp(row["source_timestamp"]) for row in pack_rows]
            packs.append({
                "sample_interval_seconds": interval,
                "sampled_frames": len(pack_rows),
                "source_timeline_span_seconds": round((max(times) - min(times)).total_seconds(), 6),
                "generated_by": "scripts/build_annotation_review_pack.py",
                "content_reviewed": False,
            })
        pack_inventory_by_run[run_id] = {
            "split": rows[0]["split"],
            "review_packs": packs,
            "pack_generated": True,
            "content_reviewed": False,
        }
    coarse_runs = {
        run_id: next((pack for pack in record["review_packs"] if pack["sample_interval_seconds"] == 1.0), record["review_packs"][0])
        for run_id, record in pack_inventory_by_run.items()
    }
    pack_inventory_by_split = {
        split: {
            "sequence_count_with_pack": sum(1 for row in pack_inventory_by_run.values() if row["split"] == split),
            "sampled_source_timeline_seconds": round(sum(pack["source_timeline_span_seconds"] for run_id, pack in coarse_runs.items() if pack_inventory_by_run[run_id]["split"] == split), 6),
            "event_annotation_records": sum(1 for row in event_rows if row["split"] == split),
        }
        for split in SPLIT_NAMES
    }

    reviewers: dict[str, dict] = {}
    for reviewer in sorted({row["annotator_id"] for row in event_rows}):
        rows = [row for row in event_rows if row["annotator_id"] == reviewer]
        reviewers[reviewer] = {
            "records": len(rows),
            "source_runs": sorted({row["source_run"] for row in rows}),
            "is_independent_human_annotator": False,
            "adjudication_required": any(row["review_stage"] != "student_adjudicated" for row in rows),
        }

    report = {
        "generated_on": datetime.now().date().isoformat(),
        "annotation_version": "1.0.0-draft",
        "manual_rule_version": "visual-categorical-v1.0.0",
        "annotation_table": EVENTS.relative_to(ROOT).as_posix(),
        "annotation_table_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "events_by_split_and_pair_type": counts,
        "category_sample_gates": category_gate,
        "uncertain_examples": [row for row in event_rows if row["status"] == "uncertain"],
        "excluded_examples": exclusion_rows,
        "review_pack_inventory": {
            "by_split": pack_inventory_by_split,
            "by_run": pack_inventory_by_run,
            "interpretation": "Generated contact sheets identify footage available for review; pack generation alone does not mean a human reviewed the clip.",
        },
        "reviewer_coverage": {
            "by_annotator": reviewers,
            "independent_second_annotator_count": 0,
            "student_adjudication_complete": False,
        },
        "test_label_control": {
            "test_event_rows_in_table": sum(1 for row in event_rows if row["split"] == "test"),
            "test_event_labels": "sealed; not annotated or used for model/threshold selection in this pilot",
        },
        "interpretation": "Both core pair types (pedestrian_vehicle and vehicle_vehicle) remain exploratory. Assistant first-pass rows are not eligible for training or primary metrics until student frame-level adjudication. Uncertain/excluded windows are never counted as non-conflict examples.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
