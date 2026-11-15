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
- For `Run_1003`, `VisualCamera7_Run_1003.mp4` is 1280×720, reports 30 FPS, and decodes 1,968 frames. Its matching frame-timing CSV has 1,968 rows. The timestamp span is 73.044 seconds; mean frame interval is 37.135 ms (about 26.93 Hz), with intervals from 5.451 to 113.329 ms. The nominal 30 FPS duration is 65.6 seconds. Use frame timestamps rather than nominal FPS for timing.
- The inspected GT CSV has 758 timestamp rows and three run-specific class blocks: `Passenger_Vehicle`, `VRU_Child`, and `VRU_Adult_Using_Walker`. The metadata defines 18 subclasses overall. GT contains 3D box centers, dimensions, and orientations in the LiDAR 2 reference frame.

## Labels and intended prediction target

- The validation data includes a binary **run-level** conflict/no-conflict label and timestamped 3D road-user boxes.
- The five-run sample has **two conflict runs and three non-conflict runs**.
- The run label does not identify event start/end times or automatically assign a conflict label to each detected actor pair. Manual event annotation and adjudication are required for event-level SVM training/evaluation.
- Metadata §4.3.2 describes a run as conflict based on TTC when two road users are identified as having a path-intersection point. The inspected metadata does not state a numeric TTC threshold; do not invent one or interpret `conflict` as proof that a collision occurred. The label CSV contains no ambiguous/uncertain state.
- Sample mapping: `Run_1023` and `Run_1290` are source-labeled `conflict`; `Run_1003`, `Run_108`, and `Run_850` are source-labeled `no conflict`. Keep these values at run level; they are not event windows or per-frame labels. The field-by-field mapping and eligibility decisions are in [`event-vocabulary.md`](event-vocabulary.md).
- DOT is one evidence source for the five-type MVP, not complete coverage: its description establishes VRU–vehicle scenarios but not labels for vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object events.
- **Projection feasibility:** The metadata states that GT coordinates are in the LiDAR 2 frame. Supporting workbooks provide a LiDAR 2–Visual Camera 6 extrinsic (reported mean reprojection error 3.89 px), a Visual Camera 6–Visual Camera 7 pairwise extrinsic (0.50 px), and Visual Camera 7 intrinsics/distortion (intrinsic reprojection error 0.2150 px). The chain allows a mathematical projection into the selected RGB camera.
- **Projection usability decision (15 November 2026):** Camera 7 calibration intrinsics are reported for 1920×1080, while the selected MP4 is 1280×720; the intrinsic matrix was scaled by 2/3 for the audit, with distortion coefficients retained and ordered for OpenCV. GT UTC timestamps were aligned to camera timestamps using the recording date's Eastern Standard Time offset, and nearby frames were compared. Across several timestamp-matched frames, projected actor centers/boxes fell on empty image regions or outside the image rather than clearly matching visible road users. The failure may be due to visibility/occlusion, timestamp/frame correspondence, calibration chain direction/quality, or GT semantics; this audit does not identify which cause is responsible. **Do not use these projections as image-space detection ground truth for Run_1003 / Visual Camera 7.** Keep the source GT in its LiDAR 2 frame, and use independently reviewed 2D annotations for RGB evaluation until a validated overlay is obtained. Method and evidence: [`projection-audit.md`](projection-audit.md).

## Intended preprocessing and data split

Use one documented visual camera, decode its MP4, and align every frame with its supplied timestamp CSV. Store camera resolution, measured video metadata, dropped/duplicate-frame handling, crossing-zone configuration, and preprocessing parameters in the experiment manifest. Do not treat nominal FPS as the timestamp source.

The five-run sample is for access and pipeline feasibility only. A separate compact candidate pool of 10 complete VisualCamera7 runs has now been selected from the full 41-run validation archive; its 5/5 run-label balance and limits are in [`compact-subset-selection.md`](compact-subset-selection.md) and its row manifest is [`data/manifests/compact-subset.csv`](../data/manifests/compact-subset.csv). Before final experiments, use separate public training-sample runs for manually labeled train/development windows and keep validation runs for held-out evaluation. The training sample is unlabeled, so any interaction-level target must be manually verified; preserve whole runs in one split. Freeze the final split only after class counts and usable event intervals are known. See [`dataset-decision.md`](dataset-decision.md) for the DOT-versus-PIE choice and [`dataset-expansion-plan.md`](dataset-expansion-plan.md) for separate supplemental sources and coverage gaps.

## Known biases and limits

- One controlled intersection and a limited number of runs; do not claim generalization to arbitrary public roads, locations, weather, or camera viewpoints.
- Surrogate VRUs and scripted scenarios may not match natural human movement.
- The five-run sample has few run labels and no event boundaries, so it cannot support strong event-level performance claims by itself.
- Some sensor streams may be missing in particular runs; RGB-only processing does not mean every run/camera is complete.
- Image-plane motion estimates are not physical distance or collision probability without validated calibration.

## Changes to record

Update this card when the full annotation dictionary has been reviewed, a dataset subset is fixed, manual labels are created, camera projection is validated, or train/development/test run IDs are frozen.

## Supplemental sources are separate evidence tracks

The downloaded TGSIM, ROCO, and Waterloo files are not part of the DOT validation sample and must not be merged into its labels. Their local inventory, schema, terms, and intended use are documented separately in [`supplemental-data-audit.md`](supplemental-data-audit.md), with a reproducible output at [`results/audits/supplemental-dataset-audit.json`](../results/audits/supplemental-dataset-audit.json). In short: TGSIM and ROCO are trajectory data without RGB; ROCO has vehicle conflict-event labels; Waterloo has video and tracks but its reuse terms remain unresolved, and its route conflict points are not observed conflict-event labels.
