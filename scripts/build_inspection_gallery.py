"""Build a local, source-aware contact-sheet gallery for every split run.

This is a visualization aid, not an event annotator. DOT labels shown here
remain run-level; no event or actor-pair labels are inferred from frames.
"""

from __future__ import annotations

import csv
import datetime as dt
import html
import json
import pathlib
import re
import tempfile
import zipfile
from collections import Counter, defaultdict

import cv2
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SPLIT_FILE = ROOT / "data" / "manifests" / "splits.csv"
OUTPUT = ROOT / "data" / "processed" / "inspection-gallery"
MANIFEST = OUTPUT / "gallery-manifest.csv"
AUDIT = OUTPUT / "gallery-audit.json"
SAMPLES = (0.10, 0.30, 0.50, 0.70, 0.90)
TILE_W = 320
TILE_H = 180
LABEL_H = 25
ROW_HEAD_H = 34
GAP = 8
CAMERA_RE = re.compile(r"^VisualCamera(\d+)_([^/]+)\.mp4$")

MANIFEST_FIELDS = [
    "sequence_id", "split", "source_archive", "source_label", "source_label_scope",
    "camera_view", "archive_video_path", "archive_timestamp_path", "frame_index",
    "sample_position_fraction", "source_timestamp", "frame_timestamp_scope",
    "event_label_status", "track_annotation_status", "review_note",
]


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def available_pairs(archive: zipfile.ZipFile, run_id: str) -> dict[int, tuple[zipfile.ZipInfo, zipfile.ZipInfo]]:
    prefix = run_id + "/"
    files = {
        pathlib.PurePosixPath(info.filename).name: info
        for info in archive.infolist()
        if info.filename.startswith(prefix) and not info.is_dir()
    }
    result: dict[int, tuple[zipfile.ZipInfo, zipfile.ZipInfo]] = {}
    for name, video_info in files.items():
        match = CAMERA_RE.match(name)
        if not match:
            continue
        camera = int(match.group(1))
        timing_name = f"VisualCamera{camera}_{run_id}_frame-timing.csv"
        timing_info = files.get(timing_name)
        if timing_info:
            result[camera] = (video_info, timing_info)
    return result


def choose_camera(pair_map: dict[int, tuple[zipfile.ZipInfo, zipfile.ZipInfo]], common_camera: int | None) -> int:
    if common_camera is not None and common_camera in pair_map:
        return common_camera
    if 7 in pair_map:
        return 7
    if pair_map:
        return min(pair_map)
    raise ValueError("No visual MP4 with a matching frame-timestamp CSV")


def timestamp_rows(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> list[dict[str, str]]:
    with archive.open(info) as raw:
        return list(csv.DictReader(line.decode("utf-8-sig") for line in raw))


def overlay_tile(frame: np.ndarray, timestamp: str, frame_index: int) -> np.ndarray:
    tile = cv2.resize(frame, (TILE_W, TILE_H), interpolation=cv2.INTER_AREA)
    cv2.rectangle(tile, (0, TILE_H - LABEL_H), (TILE_W, TILE_H), (20, 30, 35), thickness=-1)
    label = f"frame {frame_index}  |  {timestamp}"
    cv2.putText(tile, label[:54], (7, TILE_H - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (245, 243, 236), 1, cv2.LINE_AA)
    return tile


def make_sheet(split: str, rows: list[dict], output_path: pathlib.Path) -> None:
    if not rows:
        raise ValueError(f"No gallery rows for split {split}")
    width = GAP + 5 * (TILE_W + GAP)
    row_height = ROW_HEAD_H + TILE_H + GAP
    canvas = np.full((GAP + len(rows) * row_height, width, 3), (245, 244, 238), dtype=np.uint8)
    for row_number, row in enumerate(rows):
        y = GAP + row_number * row_height
        source_label = row["source_label"]
        if source_label == "conflict":
            label_text = "DOT RUN LABEL: CONFLICT — RUN-LEVEL ONLY"
            label_color = (0, 110, 170)
        elif source_label == "no conflict":
            label_text = "DOT RUN LABEL: NO CONFLICT — RUN-LEVEL ONLY"
            label_color = (45, 115, 65)
        else:
            label_text = "SOURCE LABEL UNAVAILABLE — NOT AN EVENT LABEL"
            label_color = (95, 95, 95)
        header = f"{row['sequence_id']}  |  {row['camera_view']}  |  {label_text}"
        cv2.putText(canvas, header[:120], (GAP, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, label_color, 1, cv2.LINE_AA)
        for column, frame in enumerate(row["tiles"]):
            x = GAP + column * (TILE_W + GAP)
            canvas[y + ROW_HEAD_H:y + ROW_HEAD_H + TILE_H, x:x + TILE_W] = frame
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), canvas, [cv2.IMWRITE_JPEG_QUALITY, 82]):
        raise IOError(f"Could not write contact sheet {output_path}")


def make_html(audit: dict, split_files: dict[str, str]) -> None:
    sections: list[str] = []
    for split in ("train", "validation", "test"):
        name = split_files[split]
        title = {"train": "Training runs", "validation": "Development runs", "test": "Held-out test runs"}[split]
        count = audit["run_counts_by_split"][split]
        sections.append(
            f'<section><h2>{title} <span>{count} runs</span></h2>'
            f'<p>Five timestamped frames per complete source run. <a href="{html.escape(name)}">Open contact sheet</a></p>'
            f'<img loading="lazy" src="{html.escape(name)}" alt="{html.escape(title)} contact sheet"></section>'
        )
    notes = "".join(f"<li>{html.escape(note)}</li>" for note in audit["interpretation_notes"])
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LiveCross — Data Inspection Gallery</title>
<style>
:root{{--ink:#243238;--muted:#637176;--paper:#f4f3ee;--panel:#fffefa;--line:#d8d9d1;--accent:#176b6b;--warm:#d98a42}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1200px;margin:auto;padding:28px 20px 64px}}header{{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:24px}}
h1{{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.1;margin:0 0 10px}}h2{{display:flex;justify-content:space-between;gap:12px;align-items:baseline;font-size:1.35rem;margin:0 0 8px}}
h2 span,.tag{{font-size:.85rem;color:var(--muted);font-weight:500}}section,.notice{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px;margin:18px 0;overflow:hidden}}
.notice{{border-left:4px solid var(--warm)}}.notice ul{{padding-left:20px}}a{{color:var(--accent)}}img{{display:block;width:100%;height:auto;margin:14px 0 0;border:1px solid var(--line);background:#fff}}
.actions{{display:flex;gap:12px;flex-wrap:wrap}}.tag{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 10px;margin:4px 5px 0 0}}
@media(max-width:640px){{main{{padding:18px 12px 40px}}section,.notice{{padding:14px}}h2{{font-size:1.1rem}}}}
</style></head><body><main>
<header><p class="tag">LiveCross · Phase 01.7</p><h1>Data inspection gallery</h1>
<p>Local contact sheets sampling five real timestamps from every source run in the frozen train/development/test split.</p>
<div class="actions"><a href="gallery-manifest.csv">Frame and label-scope manifest</a><a href="gallery-audit.json">Gallery audit</a></div></header>
<div class="notice"><strong>Read labels at their real scope.</strong><ul>{notes}</ul>
<h3>Label dictionary</h3><dl>
<dt><strong>DOT “conflict”</strong></dt><dd>The source marks a complete VRU–vehicle run as a potential-conflict scenario. It does not provide an event interval, a specific actor pair, or evidence that an impact occurred.</dd>
<dt><strong>DOT “no conflict”</strong></dt><dd>The source marks a complete run as non-conflict. It does not label every frame or actor pair as safe.</dd>
<dt><strong>LiveCross conflict candidate / non-conflict interaction</strong></dt><dd>These are event-level human-review labels defined in the project protocol. No such event annotations are present in this gallery yet.</dd>
<dt><strong>Uncertain / difficult</strong></dt><dd>Use uncertain when the video or tracking cannot support a reliable decision; record occlusion, glare, or poor visibility as a reason. The current gallery shows varied lighting for context but does not assign these event labels.</dd>
</dl><p>Read the <a href="../../../docs/event-vocabulary.md">event vocabulary</a> and <a href="../../../docs/manual-annotation-protocol.md">manual annotation protocol</a>.</p></div>
{''.join(sections)}
<p class="tag">Generated {html.escape(audit['generated_on'])}</p>
</main></body></html>'''
    (OUTPUT / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    if not SPLIT_FILE.is_file():
        raise FileNotFoundError(f"Missing {SPLIT_FILE.relative_to(ROOT)}")
    split_rows = read_rows(SPLIT_FILE)
    ids = [row["sequence_id"] for row in split_rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Split file contains duplicate sequence IDs")

    rows_by_split: dict[str, list[dict]] = defaultdict(list)
    detail_rows: list[dict[str, str]] = []
    camera_presence: Counter[str] = Counter()
    archive_paths = sorted({row["source_archive"] for row in split_rows})
    archive_run_pairs: dict[str, dict[str, dict[int, tuple[zipfile.ZipInfo, zipfile.ZipInfo]]]] = {}
    archive_handles: dict[str, zipfile.ZipFile] = {}
    try:
        for relative_path in archive_paths:
            path = ROOT / pathlib.Path(relative_path)
            if not path.is_file():
                raise FileNotFoundError(f"Missing local source archive {relative_path}")
            archive = zipfile.ZipFile(path)
            archive_handles[relative_path] = archive
            run_map: dict[str, dict[int, tuple[zipfile.ZipInfo, zipfile.ZipInfo]]] = {}
            for split_row in split_rows:
                if split_row["source_archive"] == relative_path:
                    pairs = available_pairs(archive, split_row["sequence_id"])
                    run_map[split_row["sequence_id"]] = pairs
                    camera_presence.update(pairs.keys())
            archive_run_pairs[relative_path] = run_map

        common_camera_by_archive: dict[str, int | None] = {}
        for archive_path, run_map in archive_run_pairs.items():
            intersections = set.intersection(*(set(pairs) for pairs in run_map.values())) if run_map else set()
            common_camera_by_archive[archive_path] = 7 if 7 in intersections else min(intersections) if intersections else None

        OUTPUT.mkdir(parents=True, exist_ok=True)
        scratch_root = RAW / "inspection"
        scratch_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="livecross-gallery-", dir=scratch_root) as temp_dir:
            scratch = pathlib.Path(temp_dir)
            for split_row in split_rows:
                run_id = split_row["sequence_id"]
                archive_path = split_row["source_archive"]
                archive = archive_handles[archive_path]
                pair_map = archive_run_pairs[archive_path][run_id]
                camera = choose_camera(pair_map, common_camera_by_archive[archive_path])
                video_info, timing_info = pair_map[camera]
                stamps = timestamp_rows(archive, timing_info)
                if not stamps or "Timestamp" not in stamps[0]:
                    raise ValueError(f"Missing Timestamp column for {run_id}")

                extracted = scratch / f"{run_id}_VisualCamera{camera}.mp4"
                with archive.open(video_info) as source, extracted.open("wb") as target:
                    while chunk := source.read(8 * 1024 * 1024):
                        target.write(chunk)
                capture = cv2.VideoCapture(str(extracted))
                if not capture.isOpened():
                    capture.release()
                    raise RuntimeError(f"Could not open {video_info.filename}")
                frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count != len(stamps):
                    capture.release()
                    raise ValueError(f"Frame/timestamp count mismatch for {run_id}: {frame_count} != {len(stamps)}")
                sample_indices = sorted({round(fraction * (frame_count - 1)) for fraction in SAMPLES})
                tile_rows: list[np.ndarray] = []
                for frame_index in sample_indices:
                    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                    decoded, frame = capture.read()
                    if not decoded or frame is None:
                        capture.release()
                        raise RuntimeError(f"Could not decode frame {frame_index} from {run_id}")
                    timestamp = stamps[frame_index]["Timestamp"]
                    tile_rows.append(overlay_tile(frame, timestamp, frame_index))
                    detail_rows.append({
                        "sequence_id": run_id,
                        "split": split_row["split"],
                        "source_archive": archive_path,
                        "source_label": split_row["source_label"],
                        "source_label_scope": split_row["source_label_scope"],
                        "camera_view": f"VisualCamera{camera}",
                        "archive_video_path": video_info.filename,
                        "archive_timestamp_path": timing_info.filename,
                        "frame_index": str(frame_index),
                        "sample_position_fraction": f"{frame_index / max(1, frame_count - 1):.6f}",
                        "source_timestamp": timestamp,
                        "frame_timestamp_scope": "frame timestamp; not event annotation",
                        "event_label_status": "not available; DOT label is run-level only or absent",
                        "track_annotation_status": "not available; RGB ground truth not approved for this camera",
                        "review_note": "Context sample only; do not infer event class from this frame.",
                    })
                capture.release()
                rows_by_split[split_row["split"]].append({
                    **split_row,
                    "camera_view": f"VisualCamera{camera}",
                    "tiles": tile_rows,
                })
                print(f"Sampled {run_id} ({split_row['split']}) at {len(sample_indices)} timestamped frames")

        split_files = {split: f"{split}-contact-sheet.jpg" for split in ("train", "validation", "test")}
        for split, rows in rows_by_split.items():
            make_sheet(split, rows, OUTPUT / split_files[split])

        with MANIFEST.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=MANIFEST_FIELDS)
            writer.writeheader()
            writer.writerows(detail_rows)

        source_labels_by_split = {
            split: dict(sorted(Counter(row["source_label"] for row in rows).items()))
            for split, rows in rows_by_split.items()
        }
        audit = {
            "generated_on": dt.date.today().isoformat(),
            "split_manifest": SPLIT_FILE.relative_to(ROOT).as_posix(),
            "output_directory": OUTPUT.relative_to(ROOT).as_posix(),
            "source_run_count": len(split_rows),
            "frame_sample_count": len(detail_rows),
            "sample_positions": list(SAMPLES),
            "run_counts_by_split": dict(sorted(Counter(row["split"] for row in split_rows).items())),
            "source_label_counts_by_split": source_labels_by_split,
            "visual_camera_pair_coverage_by_run": dict(sorted(camera_presence.items())),
            "selected_view_policy": "Choose VisualCamera7 when it is present for every run in the source archive; all runs in this split had a matching VisualCamera7 video/timestamp pair.",
            "contact_sheets": split_files,
            "interpretation_notes": [
                "The DOT conflict/no-conflict value is a run/scenario-level source label; it is not copied as a frame, event, or actor-pair label.",
                "The two public DOT training samples have no source conflict labels. Their gallery rows are explicitly marked unlabeled.",
                "The currently audited DOT 3D boxes are not approved as RGB ground truth for the selected camera, so this gallery has no track boxes or actor-pair annotations.",
                "Frames are sampled at 10%, 30%, 50%, 70%, and 90% of each complete source recording for context; these are not positive, negative, difficult, or uncertain event annotations.",
                "No difficult/uncertain event examples are asserted because reviewed event labels do not yet exist. Add those examples after the manual annotation task, using the same frozen source-run split.",
                "The generated gallery is local-only under Git-ignored data/processed; do not publish frames without checking source terms and privacy.",
            ],
        }
        AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
        make_html(audit, split_files)
        print(f"Wrote local gallery: {OUTPUT / 'index.html'}")
        print(f"Wrote {len(detail_rows)} frame records and {len(split_rows)} source runs.")
    finally:
        for archive in archive_handles.values():
            archive.close()


if __name__ == "__main__":
    main()
