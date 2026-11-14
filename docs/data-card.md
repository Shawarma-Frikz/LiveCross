# DOT Stage 1B Data Card

**Purpose:** Record the source, content, labels, and limitations of the data used by LiveCross. This initial card describes the downloaded five-run validation sample, not the entire 41-run validation dataset.

## Source and collection

- **Source:** U.S. DOT Intersection Safety Challenge Stage 1B Validation Data, [official page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4).
- **Collection:** Controlled signalized four-way intersection at FHWA Turner-Fairbank Highway Research Center, McLean, Virginia; collected October 2023 through March 2024.
- **Sensors:** Eight visual CCTV cameras, five thermal cameras, two LiDAR sensors, four radar sensors, plus traffic-controller data.
- **Scenarios:** Conflict/non-conflict scenarios between vulnerable road users (for example, pedestrians and bicyclists) and vehicles, in day/night conditions. Surrogate VRU systems were used so no human VRU was placed at risk.
- **Raw data access:** Public sample and validation files; access routes and terms are in [`dataset-access.md`](dataset-access.md). Raw archives and derived media are excluded from Git.

## Sample used for the initial audit

- Five runs, downloaded archive size **3,540,625,371 bytes**.
- Inventory: 65 MP4 videos, 82 CSV files, 10 JSON files, and 13 PCAP files.
- The five run IDs listed in the sample label file are `Run_1003`, `Run_1023`, `Run_108`, `Run_1290`, and `Run_850`.
- For `Run_1003`, `VisualCamera7_Run_1003.mp4` is 1280×720, reports 30 FPS, and decodes 1,968 frames. Its matching frame-timing CSV has 1,968 rows. The timestamp span is about 73 seconds; investigate the difference from nominal container FPS before defining temporal thresholds.
- The inspected GT CSV has timestamped 3D world-coordinate box fields. The Run_1003 header includes `Passenger_Vehicle`, `VRU_Child`, and `VRU_Adult_Using_Walker`; the full class inventory remains to be confirmed from the data dictionary.

## Labels and intended prediction target

- The validation data includes a binary **run-level** conflict/no-conflict label and timestamped 3D road-user boxes.
- The five-run sample has **two conflict runs and three non-conflict runs**.
- The run label does not identify event start/end times or automatically assign a conflict label to each detected actor pair. Manual event annotation and adjudication are required for event-level SVM training/evaluation.
- The primary project target is pedestrian/bicyclist–vehicle interaction review. The DOT description does not establish labels for vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object events.
- The 3D GT file uses world-coordinate centers, dimensions, and orientations. Projection to image coordinates depends on camera calibration; this project has not yet verified that transformation.

## Intended preprocessing and data split

Use one documented visual camera, decode its MP4, and align every frame with its supplied timestamp CSV. Store camera resolution, measured video metadata, dropped/duplicate-frame handling, crossing-zone configuration, and preprocessing parameters in the experiment manifest. Do not treat nominal FPS as the timestamp source.

The five-run sample is for access and pipeline feasibility only. Before final experiments, inspect the full 41-run validation data and consider using separate public training-sample runs for manually labeled train/development windows and validation runs for held-out evaluation. The training sample is unlabeled, so any interaction-level target must be manually verified; preserve whole runs in one split. Freeze the final split only after class counts and usable event intervals are known.

## Known biases and limits

- One controlled intersection and a limited number of runs; do not claim generalization to arbitrary public roads, locations, weather, or camera viewpoints.
- Surrogate VRUs and scripted scenarios may not match natural human movement.
- The five-run sample has few run labels and no event boundaries, so it cannot support strong event-level performance claims by itself.
- Some sensor streams may be missing in particular runs; RGB-only processing does not mean every run/camera is complete.
- Image-plane motion estimates are not physical distance or collision probability without validated calibration.

## Changes to record

Update this card when the full annotation dictionary has been reviewed, a dataset subset is fixed, manual labels are created, camera projection is validated, or train/development/test run IDs are frozen.
