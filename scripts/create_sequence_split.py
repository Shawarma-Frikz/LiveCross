"""Create a source-run split without leaking official DOT validation runs.

The public DOT training samples are unlabeled and are split into train/dev.
All runs from the official DOT validation archive are reserved for test.
The five-run validation sample is excluded because it duplicates runs in the
full validation archive.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import zipfile
from collections import Counter, defaultdict
from datetime import date
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
TRAIN_ARCHIVES = ["training-sample-1.zip", "training-sample-2.zip"]
VALIDATION_ARCHIVE = "validation-full.zip"
COMPACT_MANIFEST = ROOT / "data" / "manifests" / "compact-subset.csv"
SPLIT_CSV = ROOT / "data" / "manifests" / "splits.csv"
SPLIT_AUDIT = ROOT / "results" / "audits" / "sequence-split-audit.json"
SEED = 42
DEV_FRACTION = 0.20

FIELDS = [
    "sequence_id",
    "source_archive",
    "source_role",
    "split",
    "source_label",
    "source_label_scope",
    "split_seed",
    "assignment_policy",
    "compact_subset_member",
]


def run_ids(archive: zipfile.ZipFile) -> list[str]:
    return sorted({
        pathlib.PurePosixPath(member.filename).parts[0]
        for member in archive.infolist()
        if len(pathlib.PurePosixPath(member.filename).parts) > 1
        and pathlib.PurePosixPath(member.filename).parts[0].startswith("Run_")
    }, key=lambda value: (int(value.removeprefix("Run_")), value))


def validation_labels(archive: zipfile.ZipFile) -> dict[str, str]:
    matches = [
        member for member in archive.infolist()
        if pathlib.PurePosixPath(member.filename).name
        == "conflict_no_conflict_labels_all_validation_runs.csv"
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one full-validation label CSV; found {len(matches)}")
    with archive.open(matches[0]) as raw:
        reader = csv.DictReader(line.decode("utf-8-sig") for line in raw)
        result = {row["Run ID"]: row["Conflict_No_Conflict_Label"] for row in reader}
    counts = Counter(result.values())
    if len(result) != 41 or counts != Counter({"conflict": 12, "no conflict": 29}):
        raise ValueError(f"Unexpected official validation label inventory: {len(result)} runs, {dict(counts)}")
    return result


def read_compact_ids() -> set[str]:
    if not COMPACT_MANIFEST.is_file():
        raise FileNotFoundError(f"Missing {COMPACT_MANIFEST.relative_to(ROOT)}; create the 01.5 manifest first")
    with COMPACT_MANIFEST.open(encoding="utf-8-sig", newline="") as source:
        compact_ids = {row["source_run_id"] for row in csv.DictReader(source)}
    if len(compact_ids) != 10:
        raise ValueError(f"Expected 10 unique compact-subset runs, found {len(compact_ids)}")
    return compact_ids


def rank_for_split(run_id: str, archive_name: str) -> str:
    key = f"{SEED}:{archive_name}:{run_id}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()


def main() -> None:
    compact_ids = read_compact_ids()
    rows: list[dict[str, Any]] = []
    run_owner: dict[str, str] = {}
    training_counts: dict[str, dict[str, int]] = {}
    training_ids: set[str] = set()

    for archive_name in TRAIN_ARCHIVES:
        archive_path = RAW / archive_name
        if not archive_path.is_file():
            raise FileNotFoundError(f"Missing public training archive: {archive_path}")
        with zipfile.ZipFile(archive_path) as archive:
            ids = run_ids(archive)
        if not ids:
            raise ValueError(f"No Run_ID folders found in {archive_name}")
        for run_id in ids:
            if run_id in run_owner:
                raise ValueError(f"Duplicate source run {run_id} in {run_owner[run_id]} and {archive_name}")
            run_owner[run_id] = archive_name
            training_ids.add(run_id)

        ordered = sorted(ids, key=lambda value: rank_for_split(value, archive_name))
        dev_count = max(1, round(len(ordered) * DEV_FRACTION))
        if dev_count >= len(ordered):
            raise ValueError(f"Not enough runs in {archive_name} for both train and development")
        dev_ids = set(ordered[:dev_count])
        training_counts[archive_name] = {"train": len(ids) - len(dev_ids), "validation": len(dev_ids)}
        for run_id in ids:
            rows.append({
                "sequence_id": run_id,
                "source_archive": f"data/raw/{archive_name}",
                "source_role": "unlabeled public training sample",
                "split": "validation" if run_id in dev_ids else "train",
                "source_label": "not provided; source training data is unlabeled",
                "source_label_scope": "none",
                "split_seed": SEED,
                "assignment_policy": f"Deterministic SHA-256 ordering by seed and run within {archive_name}; {dev_count}/{len(ids)} runs reserved for development.",
                "compact_subset_member": "no",
            })

    validation_path = RAW / VALIDATION_ARCHIVE
    if not validation_path.is_file():
        raise FileNotFoundError(f"Missing official validation archive: {validation_path}")
    with zipfile.ZipFile(validation_path) as archive:
        validation_ids = run_ids(archive)
        labels = validation_labels(archive)
    if len(validation_ids) != 41 or set(validation_ids) != set(labels):
        raise ValueError("Validation archive run folders do not match the 41 official labeled runs")
    overlapping = training_ids.intersection(validation_ids)
    if overlapping:
        raise ValueError(f"Train/dev and test sources overlap by run ID: {sorted(overlapping)}")
    if not compact_ids.issubset(validation_ids):
        raise ValueError("Compact-subset runs are not all present in the official validation archive")

    for run_id in validation_ids:
        rows.append({
            "sequence_id": run_id,
            "source_archive": f"data/raw/{VALIDATION_ARCHIVE}",
            "source_role": "official labeled validation archive reserved as final test",
            "split": "test",
            "source_label": labels[run_id],
            "source_label_scope": "run/scenario only; not an event or actor-pair label",
            "split_seed": "not used; official holdout",
            "assignment_policy": "All official validation runs reserved for test before model training; no validation-run tuning or hard-negative mining.",
            "compact_subset_member": "yes" if run_id in compact_ids else "no",
        })

    sequence_ids = [row["sequence_id"] for row in rows]
    if len(sequence_ids) != len(set(sequence_ids)):
        raise ValueError("The final split contains duplicate sequence IDs")
    split_counts = Counter(row["split"] for row in rows)
    if split_counts != Counter({"train": 16, "validation": 4, "test": 41}):
        raise ValueError(f"Unexpected split sizes: {dict(split_counts)}")

    SPLIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SPLIT_CSV.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (row["split"], row["source_archive"], row["sequence_id"])))

    by_source_split: dict[str, Counter[str]] = defaultdict(Counter)
    test_label_counts = Counter()
    for row in rows:
        by_source_split[row["source_archive"]][row["split"]] += 1
        if row["split"] == "test":
            test_label_counts[row["source_label"]] += 1
    report = {
        "audit_date": date.today().isoformat(),
        "split_manifest": SPLIT_CSV.relative_to(ROOT).as_posix(),
        "split_universe": "All source runs in the two downloaded DOT public training-sample archives and the full DOT validation archive.",
        "seed": SEED,
        "split_counts": dict(sorted(split_counts.items())),
        "source_run_count": len(rows),
        "source_counts_by_split": {key: dict(sorted(value.items())) for key, value in sorted(by_source_split.items())},
        "official_validation_test_run_label_counts": dict(sorted(test_label_counts.items())),
        "compact_subset_runs_in_test": len(compact_ids),
        "unlabeled_training_data_note": "The 20 public training-sample runs have no source conflict classes; train/dev assignment is deterministic and archive-balanced, not class-stratified. Manually reviewed event labels are still required before supervised training.",
        "leakage_policy": "Whole source runs are assigned once. Both public training archives supply train/dev only; every official validation run is reserved for test. The five-run sample is not counted separately because it duplicates runs in the full validation archive.",
        "limitations": [
            "All 41 official validation runs are reserved for test, and their run-level labels are known from the source; event-level labels remain uncreated.",
            "The 16 train and 4 development runs are unlabeled until project review; no learned event model is ready to train from this split alone.",
            "The test distribution is the source distribution (12 conflict, 29 no conflict), while the selected 10-run compact subset is a deliberately balanced candidate subset and not prevalence-representative.",
            "This is a single controlled intersection dataset split, not an independent location-level generalization test.",
            "The five-run validation sample is excluded as a separate source because its runs duplicate the full validation archive. Calibration files, trajectory-only supplements, Waterloo media with unresolved reuse terms, and future staged recordings are outside this DOT split universe.",
            "Before adding any supplemental visual recordings to model development/evaluation, extend this split procedure with source/session IDs and assign each complete recording session before inspecting model predictions; never append them to an existing partition based on outcomes.",
        ],
    }
    SPLIT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    SPLIT_AUDIT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {SPLIT_CSV.relative_to(ROOT)} ({len(rows)} source runs)")
    print(f"Split counts: {dict(sorted(split_counts.items()))}")
    print(f"Official test run labels: {dict(sorted(test_label_counts.items()))}")
    print(f"Wrote {SPLIT_AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
