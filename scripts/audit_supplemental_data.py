"""Create a reproducible, metadata-only audit of downloaded LiveCross supplements.

The script reads TGSIM CSV rows, the ROCO sample ZIP, and one representative
Waterloo SQLite database directly from its ZIP. It does not extract or copy
videos into the repository and does not modify source archives.
"""

from __future__ import annotations

import csv
import io
import json
import pathlib
import sqlite3
import tempfile
import zipfile
from collections import Counter
from datetime import date


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results" / "audits" / "supplemental-dataset-audit.json"
TGSIM_TYPES = {
    "0": "person/pedestrian",
    "1": "bicycle",
    "2": "scooter",
    "3": "passenger car",
    "4": "automated vehicle",
    "5": "motorcycle",
    "6": "bus",
    "7": "truck",
}


def file_record(path: pathlib.Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size}


def audit_tgsim() -> dict:
    path = RAW / "tgsim-foggy-bottom.csv"
    if not path.is_file():
        return {"available": False, "expected_path": path.relative_to(ROOT).as_posix()}
    rows = 0
    ids: set[str] = set()
    type_counts: Counter[str] = Counter()
    time_min = float("inf")
    time_max = float("-inf")
    previous: dict[str, float] = {}
    intervals: Counter[float] = Counter()
    missing: Counter[str] = Counter()
    columns: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        for row in reader:
            rows += 1
            track_id = (row.get("id") or "").replace(",", "").strip()
            timestamp = float((row.get("time") or "").replace(",", ""))
            type_code = (row.get("type_most_common") or "").strip()
            ids.add(track_id)
            type_counts[type_code] += 1
            time_min = min(time_min, timestamp)
            time_max = max(time_max, timestamp)
            if track_id in previous:
                intervals[round(timestamp - previous[track_id], 3)] += 1
            previous[track_id] = timestamp
            for key, value in row.items():
                if value is None or not value.strip():
                    missing[key] += 1
    return {
        "available": True,
        "file": file_record(path),
        "rows": rows,
        "columns": columns,
        "unique_track_ids": len(ids),
        "time_seconds_min_max": [time_min, time_max],
        "most_common_per_track_time_intervals_seconds": [
            {"interval": interval, "count": count}
            for interval, count in intervals.most_common(10)
        ],
        "type_code_counts": [
            {"code": code, "meaning_from_official_data_dictionary": TGSIM_TYPES.get(code, "unmapped"), "rows": count}
            for code, count in sorted(type_counts.items())
        ],
        "missing_cell_counts": dict(missing),
        "interpretation": "Trajectory observations only; no RGB video or source-provided conflict-event labels in this CSV.",
    }


def audit_roco() -> dict:
    path = RAW / "roco" / "ROCO.zip"
    if not path.is_file():
        return {"available": False, "expected_path": path.relative_to(ROOT).as_posix()}
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        label_name = next(name for name in archive.namelist() if name.endswith("conflict_label.csv"))
        text = io.TextIOWrapper(archive.open(label_name), encoding="utf-8-sig", newline="")
        reader = csv.reader(text)
        header = next(reader)
        physical_rows = list(reader)
        # The published pair is written as `(id1, id2)` without CSV quoting.
        # That produces six fields under a five-field header; recover the pair
        # and final effect column by position, and fail loudly on other shapes.
        normalized = []
        row_widths = Counter()
        for row in physical_rows:
            row_widths[len(row)] += 1
            if len(row) != 6:
                raise ValueError(f"Unexpected ROCO label row width {len(row)}: {row!r}")
            normalized.append({
                "event_time": row[0],
                "severity": row[1],
                "reason": row[2],
                "pair_ids": [row[3].lstrip(" (").strip(), row[4].rstrip(" )").strip()],
                "effect": row[5],
            })
        severity = Counter(row["severity"] for row in normalized)
        reason = Counter(row["reason"] for row in normalized)
        effect = Counter(row["effect"] for row in normalized)
        json_files = [item for item in members if item.filename.lower().endswith(".json")]
        event_dirs = sorted({str(pathlib.PurePosixPath(item.filename).parent) for item in json_files})
        sample_json_name = json_files[0].filename
        sample_json = json.loads(archive.read(sample_json_name))
    return {
        "available": True,
        "file": file_record(path),
        "archive_entries_including_directories": len(members),
        "trajectory_json_frame_files": len(json_files),
        "event_folders_with_json": len(event_dirs),
        "label_csv": {
            "path_in_archive": label_name,
            "header_as_published": header,
            "rows": len(normalized),
            "physical_row_width_counts": {str(width): count for width, count in sorted(row_widths.items())},
            "severity_code_counts": dict(sorted(severity.items())),
            "reason_code_counts": dict(sorted(reason.items())),
            "effect_code_counts": dict(sorted(effect.items())),
            "sample_normalized_row": normalized[0],
            "format_note": "Each local data row has six fields although its physical header has five: the conflict-pair tuple is unquoted and splits across two fields. The local header also differs from the upstream README: event_time vs event_timestamp, and no time offset field. The audit reconstructs pair IDs and effect by position; do not infer a missing offset.",
        },
        "sample_trajectory_frame": {
            "path_in_archive": sample_json_name,
            "top_level_keys": list(sample_json) if isinstance(sample_json, dict) else None,
            "fusion_agent_count": len(sample_json.get("fusion", [])) if isinstance(sample_json, dict) else None,
            "agent_fields": list(sample_json.get("fusion", [{}])[0]) if isinstance(sample_json, dict) and sample_json.get("fusion") else [],
        },
        "interpretation": "Vehicle conflict-event trajectories and labels; no RGB frames in this sample archive, so it cannot validate visual detection or image-space explanations.",
    }


def audit_waterloo() -> dict:
    db_zip = RAW / "waterloo" / "intersection_dbfiles.zip"
    video_zip = RAW / "waterloo" / "annotated_videos.zip"
    missing = [path.relative_to(ROOT).as_posix() for path in (db_zip, video_zip) if not path.is_file()]
    if missing:
        return {"available": False, "missing_files": missing}
    with zipfile.ZipFile(db_zip) as db_archive, zipfile.ZipFile(video_zip) as video_archive:
        db_members = sorted(name for name in db_archive.namelist() if name.lower().endswith(".db"))
        videos = [name for name in video_archive.namelist() if name.lower().endswith(".avi")]
        representative = next(name for name in db_members if pathlib.PurePosixPath(name).name == "intsc_data_769.db")
        inspection_dir = RAW / "inspection"
        inspection_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="livecross-waterloo-audit-", dir=inspection_dir) as temp_dir:
            db_path = pathlib.Path(temp_dir) / pathlib.PurePosixPath(representative).name
            with db_archive.open(representative) as source, db_path.open("wb") as destination:
                while chunk := source.read(8 * 1024 * 1024):
                    destination.write(chunk)
            connection = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
            try:
                table_names = [row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )]
                tables = {}
                for table in table_names:
                    escaped = table.replace('"', '""')
                    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{escaped}")')]
                    count = connection.execute(f'SELECT COUNT(*) FROM "{escaped}"').fetchone()[0]
                    tables[table] = {"rows": count, "columns": columns}
                track_types = dict(connection.execute(
                    "SELECT TYPE, COUNT(*) FROM TRACKS GROUP BY TYPE ORDER BY TYPE"
                ).fetchall())
                trajectory_types = dict(connection.execute(
                    "SELECT TYPE, COUNT(*) FROM TRAJECTORY_MOVEMENTS GROUP BY TYPE ORDER BY TYPE"
                ).fetchall())
            finally:
                connection.close()
    return {
        "available": True,
        "database_archive": file_record(db_zip),
        "annotated_video_archive": file_record(video_zip),
        "database_files": len(db_members),
        "video_files": len(videos),
        "matched_file_stems": sorted(
            {pathlib.PurePosixPath(name).stem.replace("intsc_data_", "") for name in db_members}
            & {pathlib.PurePosixPath(name).stem for name in videos}
        ),
        "representative_database": {
            "path_in_archive": representative,
            "tables": tables,
            "track_type_counts": track_types,
            "trajectory_movement_type_counts": trajectory_types,
        },
        "interpretation": "Includes ID-annotated video and pedestrian/vehicle trajectories. CONFLICT_POINTS describe geometric route intersections, not observed pair-level near-miss/collision labels. Publisher page currently states no reuse license; treat reuse/redistribution permission as unresolved.",
    }


def main() -> None:
    report = {
        "audit_date": date.today().isoformat(),
        "purpose": "Local inventory/schema/label audit of downloaded supplementary candidate datasets; not a model evaluation.",
        "sources": {
            "tgsim_foggy_bottom": audit_tgsim(),
            "roco_sample": audit_roco(),
            "waterloo_intersection": audit_waterloo(),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
