# LiveCross — DOT Dataset Access and Terms

**Reviewed:** 14 November 2026  
**Dataset:** U.S. DOT Intersection Safety Challenge (ISC), Stage 1B

## Recommended first download

Start with the public **Validation Data Sample** linked from the [official validation dataset page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4). It contains five runs and is approximately **3 GB**. The portal recommends inspecting this sample before committing to the full validation download. Download the ZIP from the page’s attachments and extract it locally; keep the archive and extracted footage out of Git.

After extraction, choose one run and locate a visual camera `.mp4` plus the matching `.csv` of frame timestamps. The official data story says the visual-camera MP4 recordings and per-frame timestamp CSVs are included in both training and validation datasets. LiveCross can use the chosen video and its timestamps without loading LiDAR, radar, thermal, or traffic-controller streams. The full archive is still needed for the first download; the pipeline can then read only the selected RGB video and timestamp file. Confirm the exact folder/file pairing and camera identifier using the included metadata and supporting documentation before analysis.

## Dataset sizes and access routes

| Asset | Officially listed size / coverage | Access route |
|---|---|---|
| Validation sample | 5 runs; about 3 GB | Public ZIP attachment on the [validation page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4). Recommended first choice for checking the data. |
| Full validation | 41 runs; about 30 GB | Public full validation ZIP linked from the same page/data story. |
| Training sample 1 | 8,161,594,056 bytes (~7.6 GiB) | Public ZIP attachment on the [training page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Training-Da/vq7s-mv3v). Unlabeled; suitable for manually reviewed training/development windows, not direct supervised evaluation. |
| Training sample 2 | 5,148,222,990 bytes (~4.8 GiB) | Public ZIP attachment on the training page. Unlabeled; suitable for manually reviewed training/development windows, not direct supervised evaluation. |
| Full training | 1,104 runs; about 1 TB | Submit the ITS JPO [data request form](https://its.dot.gov/data/data-request/); the portal says an administrator follows up with download instructions. The form is available to anyone; organization and use-case details are requested, and use case is optional. |

The full training asset is explicitly described as **unlabeled**. The validation asset provides timestamped 3D road-user boxes and a **run-level** conflict/no-conflict label. This is not event-timing ground truth, so event-level evaluation still needs documented manual event annotations. See [`acceptance-targets.md`](acceptance-targets.md).

## Use, terms, and attribution

The DOT validation page marks access as **public** and rights as **public**; its catalog entry does not expose a separate validation-specific license field. The training dataset’s Data.gov catalog entry lists the [USA.gov Public Domain Mark 1.0](https://www.usa.gov/government-works), but do not assume that a catalog field resolves every condition for all supporting material or derived media. Follow the dataset citation below, retain the source and access date, and check with ITS JPO if planning redistribution beyond the project repository or publication. Do not commit raw data to Git. The data story asks users to cite the dataset and replace `YYYY-MM-DD` with the date they accessed it.

Use the relevant citation in project reports:

**Training:** U.S. Department of Transportation Intelligent Transportation Systems Joint Program Office. (2025). *Intersection Safety Challenge Stage 1B Dataset. Training Data.* Provided by ITS DataHub through Data.transportation.gov. Accessed [access date] from https://doi.org/10.21949/1404202

**Validation:** U.S. Department of Transportation Intelligent Transportation Systems Joint Program Office. (2026). *Intersection Safety Challenge Stage 1B Dataset. Validation Data.* Provided by ITS DataHub through Data.transportation.gov. Accessed [access date] from https://doi.org/10.21949/1404202

## Scope and limitations to record

- Data were collected at one controlled, signalized four-way intersection at FHWA’s TFHRC facility, not from open public-road deployment.
- Scenarios include vulnerable-road-user/vehicle conflict and non-conflict cases. Do not treat the labels as validation for vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object interactions.
- The dataset includes surrogate vulnerable road users; the data story says no humans were put at risk during collection.
- The public samples are large multi-sensor ZIPs. For LiveCross, first confirm that one representative RGB video and its timestamps extract and play correctly; additional sensor types are optional for this project.
- “Live” camera operation is a separate staged demo. This dataset is recorded video, suitable for replay through the same frame-processing pipeline.

## Completion record

- [x] Official training and validation pages reviewed.
- [x] Sample/full download routes and listed sizes recorded.
- [x] Public access/rights fields and citation instructions recorded; license metadata distinguished between training and validation entries.
- [x] Video-only processing path confirmed by the data story’s MP4 and timestamp-CSV description.
- [x] Downloaded the official five-run validation sample to `data/raw/validation-sample.zip` (3,540,625,371 bytes); raw data is excluded by `.gitignore`.
- [x] Opened the archive and extracted only a representative run's files under the ignored `data/raw/inspection/` folder.
- [x] Verified `Run_1003/VisualCamera7_Run_1003.mp4` and its frame-timing CSV are paired and complete: 31,852,808-byte MP4, 62,999-byte CSV, 1,968 decoded video frames, and 1,968 timestamp rows. OpenCV opened the MP4 at 1280×720, reported 30 FPS, and decoded a frame successfully. A sampled frame shows a fixed roadside intersection with a marked crosswalk.
- [x] Inspected the run-level label file: Run_1003 is marked `no conflict`; the sample provides one label per run, not event start/end times.
- [x] Reviewed the metadata's 18-subclass taxonomy, GT coordinate frame, and available calibration chain into Visual Camera 7. A multi-frame timestamp-aligned projection audit did not produce convincing actor alignment; projected labels are not approved as image-space GT for this camera/run. Details: [`projection-audit.md`](projection-audit.md).
- [x] Downloaded the full 41-run validation archive, both public training-sample archives, and calibration archive with [`scripts/fetch_project_data.py`](../scripts/fetch_project_data.py); recorded sizes and ZIP verification in the download manifest.
- [x] Downloaded the FHWA TGSIM Foggy Bottom trajectory CSV (342,323,446 bytes). [ ] Inspect its schema, units, attribution, and use terms before analysis; do not treat it as video or conflict ground truth.

**Timing note:** The timestamp CSV spans 73.044 seconds for 1,968 frames, while the MP4 container reports 30 FPS. Its mean timestamp interval is 37.135 ms (about 26.93 Hz), with irregular gaps. Use the supplied per-frame timestamps as source time rather than reconstructing event times from nominal FPS alone; inspect this behavior across more runs before locking timing logic.
