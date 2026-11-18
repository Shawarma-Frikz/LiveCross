# Dataset Setup

## Primary dataset

Use the [U.S. DOT Intersection Safety Challenge Stage 1B Validation Data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4) for the first benchmark. The official validation set has 41 runs (about 30 GB); the public five-run sample is about 3 GB on the portal and is 3,540,625,371 bytes as downloaded here. Download the sample from the page’s attachments before considering the full set.

The data is a multi-sensor set, but the MVP can read a selected visual-camera `.mp4` and its corresponding frame-timestamp `.csv`. The ZIP also contains thermal-camera MP4s, calibration/data files, LiDAR PCAPs, and other sensor records; LiveCross does not need to load these for its RGB-video MVP. Keep all downloaded and extracted raw data under `data/raw/`; that directory is Git-ignored.

## Download inventory (checked locally on 15 November 2026)

All files below are under the Git-ignored `data/raw/` directory. The DOT fetch script recorded the five primary downloads in `download-manifest.json`; it verifies the listed byte sizes and checks archive CRCs before recording completion. The Waterloo and ROCO ZIPs are present and their ZIP directories can be read; their archives have not been CRC-scanned here.

| Local file | Bytes | Source / contents | Intended use and limits |
|---|---:|---|---|
| `validation-sample.zip` | 3,540,625,371 | DOT ISC Stage 1B five-run validation sample | Access and pipeline pilot; run-level conflict labels and timestamped 3D GT |
| `validation-full.zip` | 28,642,566,098 | DOT ISC Stage 1B full 41-run validation archive | Larger VRU–vehicle benchmark pool; needs label and RGB projection checks |
| `training-sample-1.zip` | 8,161,594,056 | DOT public training sample 1 | Unlabeled RGB footage for manually reviewed training/development and hard-negative mining |
| `training-sample-2.zip` | 5,148,222,990 | DOT public training sample 2 | Same role as sample 1; keep separate from held-out validation runs |
| `calibration.zip` | 8,502,530,399 | DOT calibration capture archive | Calibration source material; the projection matrices used in the feasibility audit are in the supporting-documents ZIP below |
| `metadata-and-supporting-docs.zip` | 9,723,626 | DOT metadata, data dictionary, camera intrinsics and extrinsics workbooks | Annotation schema, coordinate frames, and calibration parameters |
| `ISC-Stage-1B-metadata.pdf` | 5,934,149 | DOT metadata PDF | Human-readable dataset and calibration documentation |
| `tgsim-foggy-bottom.csv` | 342,323,446 | FHWA TGSIM Foggy Bottom trajectories | Motion-feature research; not video and not conflict-event ground truth |
| `waterloo/annotated_videos.zip` | 4,673,980,140 | Waterloo Multi-Agent Traffic Dataset: Intersection | Annotated road-user video; tracks are not conflict-event labels |
| `waterloo/intersection_dbfiles.zip` | 610,803,071 | Waterloo intersection trajectory/context databases | Road-user trajectories and context; no complete near-conflict event labels |
| `roco/ROCO.zip` | 25,063,270 | ROCO sample | Labeled vehicle-conflict trajectories; not video and not evidence for other interaction types |

The separately downloaded DOT five-run sample was also extracted selectively for inspection. Temporary range-check binary files in `data/raw/` are download diagnostics, not project data.

## Sample audit

Regenerate the machine-checkable archive inventory, Run_1003 video/timestamp comparison, raw label counts, and GT column summary with `python scripts/audit_sample_data.py`. It writes the environment and measurements to [`results/audits/dot-sample-audit.json`](../results/audits/dot-sample-audit.json). The script does not assign semantic labels or judge projected-box alignment; those decisions stay in the versioned documentation.

- The five-run validation ZIP contains **170 files**: 65 MP4s, 82 CSVs, 10 JSON files, and 13 PCAP files.
- The selected `Run_1003/VisualCamera7_Run_1003.mp4` is 1280×720, reports 30 FPS in its container, and decodes **1,968 frames**. Its matching `VisualCamera7_Run_1003_frame-timing.csv` has **1,968 timestamp rows**.
- The frame timestamps are strictly increasing but irregular: span **73.044 s**, mean interval **37.135 ms** (about **26.93 frames/s**), median interval **34.753 ms**, minimum **5.451 ms**, maximum **113.329 ms**. At the container's nominal 30 FPS, 1,968 frames imply only 65.6 s. Use the supplied per-frame timestamps as source time; do not reconstruct event times from nominal FPS.
- `Run_1003_GT.csv` has 758 rows, with three subclass column blocks in this run: `Passenger_Vehicle`, `VRU_Child`, and `VRU_Adult_Using_Walker`. The metadata dictionary defines 18 road-user subclasses overall; a run's CSV only includes columns represented in that run. GT provides timestamped 3D box centers, dimensions, and orientations in the LiDAR 2 reference frame.
- Projection into the selected Visual Camera 7 is mathematically possible using the supplied LiDAR 2–Visual Camera 6 and Visual Camera 6–Visual Camera 7 extrinsics, plus Visual Camera 7 intrinsics/distortion. However, timestamp-aligned overlays on several frames place GT centers/boxes on apparently empty image regions or outside the image. **Decision: these projected boxes are not usable as image-space ground truth for this camera/run until the mismatch is resolved.** See [`docs/projection-audit.md`](../docs/projection-audit.md) for the transform chain, resolution handling, and evidence.
- `conflict_no_conflict_labels_sample_validation_runs.csv` has one binary label per run; the five sample runs include two conflict and three non-conflict labels. These are not event start/end labels.
- The sample validates access and video decoding, but is too small by itself for strong model-performance claims.

## Compact validation subset

The current 01.5 candidate pool uses 10 complete VisualCamera7 sequences from `validation-full.zip`: five DOT run-level conflict labels and five no-conflict labels. It is balanced across three daylight and two low-light midpoint views per source-label group. The selected camera files total about 7 minutes 21 seconds by supplied timestamps; all 10 timestamp row counts match the decoded video frame counts. Selection rationale and limits are in [`docs/compact-subset-selection.md`](../docs/compact-subset-selection.md).

Recreate the row-level list in [`manifests/compact-subset.csv`](manifests/compact-subset.csv) and the aggregate audit in [`results/audits/compact-subset-audit.json`](../results/audits/compact-subset-audit.json) with:

```powershell
python scripts/build_compact_subset_manifest.py
```

The selected 10-run subset is a balanced **candidate pool inside the held-out test partition**. Its source labels remain run-level only; event times, actor pairs, and the other four interaction types still require separately reviewed annotations.

### Extract the selected video pairs

The 28.6 GB validation ZIP does not need to be fully unpacked. For frame-by-frame review, annotation, and later video-pipeline work, extract only the ten selected VisualCamera7 MP4s and their ten matching timestamp CSVs (about 328.4 MiB of video plus small CSV files). Keep the original ZIP as the source archive. Run from the repository root:

```powershell
python scripts/extract_compact_subset.py
```

The script reads the reviewed subset manifest, checks the archived video sizes against it, extracts complete files with ZIP CRC verification, and writes them under `data/raw/selected-validation/<Run_ID>/`. The destination is Git-ignored. The extraction is repeatable and does not create labels or a train/development/test split. Do not extract the unrelated sensor streams for the RGB MVP.

## Sequence-level split

The split manifest covers all **61 unique source runs** in the two downloaded public training samples and the full 41-run validation archive. It assigns 16 training-sample runs to `train`, 4 to `validation` (development), and all 41 official validation runs to `test`. Within each 10-run training archive, a deterministic SHA-256 ranking with seed **42** selects 2 development runs and 8 training runs. The official validation labels are preserved at their native run-level scope (12 conflict, 29 no conflict); all 10 runs in the compact subset are in `test`.

This source-aware split prevents run leakage and protects the official validation archive from training, tuning, and hard-negative mining. The two training samples are unlabeled, so class stratification is not possible for the 16/4 train/development split; the manifest records that limitation. The five-run sample is omitted as a separate source because its runs are included in the full validation archive. The split covers the downloaded DOT run archives only; calibration files, trajectory-only supplements, Waterloo footage with unresolved reuse terms, and future staged recordings are outside this manifest. Add any future visual recording sessions to the split procedure before model predictions are inspected. Recreate the split CSV and audit report with:

```powershell
python scripts/create_sequence_split.py
```

This writes [`manifests/splits.csv`](manifests/splits.csv) and [`results/audits/sequence-split-audit.json`](../results/audits/sequence-split-audit.json). The split assigns source runs, not event labels. Human event annotations are still needed before supervised event training, and the known run-level test labels must not be used to tune event-level predictions.

For a clean regeneration of both subset and split records, run `python scripts/build_compact_subset_manifest.py`, then `python scripts/create_sequence_split.py`, then `python scripts/build_compact_subset_manifest.py` once more. The final subset manifest will then carry its `test` assignment from the global split file.

## Local organization

```text
data/
├── README.md                 # tracked instructions and dataset card
├── raw/                      # ignored: downloaded archives and extracted source data
│   ├── validation-sample.zip
│   ├── metadata-and-supporting-docs.zip
│   ├── selected-validation/   # ignored: 10 selected MP4/timestamp pairs
│   └── inspection/           # small local audit subset, also ignored
└── processed/                # generated clips, annotations, and features; do not commit by default
```

Download from the official page above and place the file as `data/raw/validation-sample.zip`. Create `data/raw/` if needed. Extract only the runs and files needed for a task. Keep derived annotations local unless they contain no restricted or identifying material and are useful to version; document their provenance either way.

## Labels and project boundaries

The DOT validation data supplies 3D road-user boxes per timestamp and a run-level conflict/no-conflict label. It does not supply event boundaries or pair-level event labels. For LiveCross's two-category scope, DOT video is a source for future manual pedestrian–vehicle and vehicle–vehicle event annotation; the native run label only describes the documented DOT scenario and must never be copied to an event or actor pair. The audited VisualCamera7 projection is not approved as RGB image-space ground truth.

The 1,104-run training dataset is unlabeled and about 1 TB; the full training set requires an ITS JPO request. The two public training samples (about 7.6 GB and 4.8 GB) are a more appropriate source for manually reviewed training/development examples and hard-negative mining. Keep them out of the held-out test split. The full 41-run validation set is the priority for scaling the VRU–vehicle benchmark.

The downloaded samples are not sufficient for strong event-level performance claims. Use DOT training samples for training/development annotation and retain the official validation archive as the designated test split; do not tune from its run labels. ROCO is trajectory-only and can support a separately reported vehicle–vehicle trajectory comparator, not video evaluation. Waterloo is excluded from public use until reuse terms are clarified. See [`docs/dataset-decision.md`](../docs/dataset-decision.md) and [`docs/phase0-phase1-freeze.md`](../docs/phase0-phase1-freeze.md) for current category readiness and required human review.

## Citation and rights

Cite the DOT dataset in reports and replace the placeholder with the date the dataset was accessed. See [dataset access and terms](../docs/dataset-access.md) for the full citation, metadata, and use notes. Never commit raw archives, raw video, or model weights downloaded from external sources.
