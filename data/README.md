# Dataset Setup

## Primary dataset

Use the [U.S. DOT Intersection Safety Challenge Stage 1B Validation Data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4) for the first benchmark. The official validation set has 41 runs (about 30 GB); the public five-run sample is about 3 GB on the portal and is 3,540,625,371 bytes as downloaded here. Download the sample from the page’s attachments before considering the full set.

The data is a multi-sensor set, but the MVP can read a selected visual-camera `.mp4` and its corresponding frame-timestamp `.csv`. The ZIP also contains thermal-camera MP4s, calibration/data files, LiDAR PCAPs, and other sensor records; LiveCross does not need to load these for its RGB-video MVP. Keep all downloaded and extracted raw data under `data/raw/`; that directory is Git-ignored.

## Sample audit

- Five validation runs; official archive extracted locally.
- Sample inventory: 65 MP4s, 82 CSVs, 10 JSON files, and 13 PCAP files.
- The selected `Run_1003/VisualCamera7_Run_1003.mp4` is 1280×720, 30 FPS as reported by its MP4 container, with 1,968 decodable frames.
- Its matching `VisualCamera7_Run_1003_frame-timing.csv` has 1,968 timestamp rows. The timestamps span about 73 seconds, so use those timestamps as source time instead of deriving time from nominal FPS alone.
- `Run_1003_GT.csv` contains timestamped 3D world-coordinate box fields. The inspected header includes `Passenger_Vehicle`, `VRU_Child`, and `VRU_Adult_Using_Walker` position, size, and orientation fields. Confirm the full class dictionary and camera projection before using those boxes as image-space evaluation annotations.
- `conflict_no_conflict_labels_sample_validation_runs.csv` has one binary label per run; the five sample runs include two conflict and three non-conflict labels. These are not event start/end labels.
- This sample validates access and video decoding, but is too small by itself for strong model-performance claims.

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

The 1,104-run training dataset is unlabeled and about 1 TB; the full training set requires an ITS JPO request. It is not needed for the initial prototype. The full 41-run validation set is the first candidate for scaling evaluation after sample feasibility is confirmed.

## Citation and rights

Cite the DOT dataset in reports and replace the placeholder with the date the dataset was accessed. See [dataset access and terms](../docs/dataset-access.md) for the full citation, metadata, and use notes. Never commit raw archives, raw video, or model weights downloaded from external sources.
