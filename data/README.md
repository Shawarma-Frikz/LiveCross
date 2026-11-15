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

- The five-run validation ZIP contains **170 files**: 65 MP4s, 82 CSVs, 10 JSON files, and 13 PCAP files.
- The selected `Run_1003/VisualCamera7_Run_1003.mp4` is 1280×720, reports 30 FPS in its container, and decodes **1,968 frames**. Its matching `VisualCamera7_Run_1003_frame-timing.csv` has **1,968 timestamp rows**.
- The frame timestamps are strictly increasing but irregular: span **73.044 s**, mean interval **37.135 ms** (about **26.93 frames/s**), median interval **34.753 ms**, minimum **5.451 ms**, maximum **113.329 ms**. At the container's nominal 30 FPS, 1,968 frames imply only 65.6 s. Use the supplied per-frame timestamps as source time; do not reconstruct event times from nominal FPS.
- `Run_1003_GT.csv` has 758 rows, with three subclass column blocks in this run: `Passenger_Vehicle`, `VRU_Child`, and `VRU_Adult_Using_Walker`. The metadata dictionary defines 18 road-user subclasses overall; a run's CSV only includes columns represented in that run. GT provides timestamped 3D box centers, dimensions, and orientations in the LiDAR 2 reference frame.
- Projection into the selected Visual Camera 7 is mathematically possible using the supplied LiDAR 2–Visual Camera 6 and Visual Camera 6–Visual Camera 7 extrinsics, plus Visual Camera 7 intrinsics/distortion. However, timestamp-aligned overlays on several frames place GT centers/boxes on apparently empty image regions or outside the image. **Decision: these projected boxes are not usable as image-space ground truth for this camera/run until the mismatch is resolved.** See [`docs/projection-audit.md`](../docs/projection-audit.md) for the transform chain, resolution handling, and evidence.
- `conflict_no_conflict_labels_sample_validation_runs.csv` has one binary label per run; the five sample runs include two conflict and three non-conflict labels. These are not event start/end labels.
- The sample validates access and video decoding, but is too small by itself for strong model-performance claims.

## Local organization

```text
data/
├── README.md                 # tracked instructions and dataset card
├── raw/                      # ignored: downloaded archives and extracted source data
│   ├── validation-sample.zip
│   ├── metadata-and-supporting-docs.zip
│   └── inspection/           # small local audit subset, also ignored
└── processed/                # generated clips, annotations, and features; do not commit by default
```

Download from the official page above and place the file as `data/raw/validation-sample.zip`. Create `data/raw/` if needed. Extract only the runs and files needed for a task. Keep derived annotations local unless they contain no restricted or identifying material and are useful to version; document their provenance either way.

## Labels and project boundaries

The validation data supplies 3D road-user boxes per timestamp and a run-level conflict/no-conflict label. It does not supply event boundaries in the five-run sample. The event-level task therefore needs separately documented manual event intervals, with complete runs kept together across training/development/test splits. DOT conflict labels support vulnerable-road-user–vehicle interactions; they do not validate vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object results.

The 1,104-run training dataset is unlabeled and about 1 TB; the full training set requires an ITS JPO request. The two public training samples (about 7.6 GB and 4.8 GB) are a more appropriate source for manually reviewed training/development examples and hard-negative mining. Keep them out of the held-out test split. The full 41-run validation set is the priority for scaling the VRU–vehicle benchmark.

The downloaded five-run sample is not enough for strong final claims or all five interaction types. Follow [`docs/dataset-expansion-plan.md`](../docs/dataset-expansion-plan.md): use the full DOT validation set for held-out VRU–vehicle results, but first resolve/validate RGB GT projection or use independently reviewed 2D annotations; use the two public DOT training samples only for manually reviewed training/development clips; consider FHWA TGSIM for motion-feature research; and create a small permission-cleared staged video set for visual evaluation of the other interaction types and fixed-object cases. Keep each source’s metrics separate.

## Citation and rights

Cite the DOT dataset in reports and replace the placeholder with the date the dataset was accessed. See [dataset access and terms](../docs/dataset-access.md) for the full citation, metadata, and use notes. Never commit raw archives, raw video, or model weights downloaded from external sources.
