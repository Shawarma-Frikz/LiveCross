# LiveCross — Candidate Dataset Audit

**Audit date:** 18 November 2026  
**Standard applied:** Follows the same audit standard established in the U.S. DOT ISC Stage 1B validation and supplemental dataset audits ([`docs/dataset-access.md`](dataset-access.md), [`docs/supplemental-data-audit.md`](supplemental-data-audit.md)).  
**Machine-readable audit output:** [`results/audits/candidate-dataset-audit.json`](../results/audits/candidate-dataset-audit.json).

Re-run the audit anytime with:
```powershell
python scripts/audit_candidate_datasets.py
```

---

## Executive Summary & LiveCross Category Fit

| Candidate Dataset | Source & Perspective | Local Status | vehicle–vehicle | pedestrian–vehicle | pedestrian–pedestrian | vehicle–fixed-obj | ped–fixed-obj | Verdict |
|---|---|---|---|---|---|---|---|---|
| **TUMTraf-Accid3nD** | Roadside gantry (1920×1200 @ 25 Hz), A9 Motorway (Munich) | Verified sample downloaded (5 image/label pairs; 3.0 MB). Full dataset: 46.59 GB across 5 WebDAV archives. | ⚠️ Motorway collisions only (not intersection conflicts) | ❌ Zero coverage (motorway) | ❌ Zero coverage | ⚠️ Motorway barrier impacts | ❌ Zero coverage | Exploratory / perception reference only |
| **DoTA** | Egocentric dashcam (moving car, YouTube driving videos) | Complete annotations & splits downloaded (11.4 MB). Video frames: ~55 GB on Google Drive. | ⚠️ Ego-camera accidents (turning, lateral, rear-end) | ⚠️ 100 dashcam accident clips | ❌ Zero coverage | ⚠️ 95 dashcam obstacle clips | ❌ Zero coverage | Exploratory / ego-view comparator only |
| **JRDB / JRDB-Social** | Mobile robot (JackRabbot) eye-level, university campus | Access-gated (account registration required at Monash portal) | ❌ Zero vehicles in dataset | ❌ Zero vehicles in dataset | ⚠️ Semantic mismatch: social interaction ≠ conflict | ❌ Zero vehicles in dataset | ❌ Zero road objects | Not suitable for conflict benchmarking |

---

## 1. TUMTraf-Accid3nD

### 1.1 Source, Access & Infrastructure
- **Official Portal:** [accident-dataset.github.io](https://accident-dataset.github.io/)
- **Publication:** Zimmer et al., *"Towards Vision Zero: The TUM Traffic Accid3nD Dataset"*, arXiv:2503.12095 (2025).
- **Hosting Architecture:** Hosted on an institutional Nextcloud instance (`https://nx21496.your-storageshare.de/s/Zd4rwsMwwXMaXiK/download`).
- **Transfer Caveat:** The Nextcloud web portal serves downloads using `Transfer-Encoding: chunked` and omits the HTTP `Content-Length` header. However, direct WebDAV inspection of `/public.php/webdav/accid3nd_dataset/` reveals the underlying archive layout:
  - `train1.zip`: 9,436,619,494 bytes (8.79 GiB)
  - `train2.zip`: 9,436,522,698 bytes (8.79 GiB)
  - `train3.zip`: 9,436,612,632 bytes (8.79 GiB)
  - `train4.zip`: 9,435,983,723 bytes (8.79 GiB)
  - `train5.zip`: 8,841,778,208 bytes (8.23 GiB)
  - **Total payload:** **46,587,516,755 bytes (43.39 GiB / 46.59 GB)**.
- **License & Terms:** **CC BY-NC-SA 4.0** (Attribution-NonCommercial-ShareAlike). Non-commercial educational/research use is fully permitted. Adaptations must carry identical licensing and cite Zimmer et al.

### 1.2 Local Sample Inspection
To maintain data discipline without prematurely saturating local disk storage (available: 132.5 GB), a representative 5-frame sequence (`r09_s02`) was extracted directly from `train1.zip` via range requests to [`data/raw/tumtraf-accid3nd/sample/`](../data/raw/tumtraf-accid3nd/sample/):
- **Camera Sensor:** `s040_camera_basler_north_50mm` (Basler industrial gantry camera looking north).
- **Image Resolution:** Confirmed decoded OpenCV shape: `(1200, 1920, 3)` (1080p+ widescreen color).
- **Frame Timestamps:** Nanosecond-resolution timestamps (e.g. `1634804504_413000000`). Frame images and OpenLABEL JSON files match timestamps exactly.
- **Annotation Format:** ASAM OpenLABEL v1.0.0 JSON standard.
- **Bounding Box Quality:** Unlike the DOT dataset (where 3D LiDAR boxes failed to project reliably into camera pixels without calibration errors), TUMTraf provides **native, highly accurate 2D bounding boxes** (`bbox`: `[x, y, w, h]`), **2D instance segmentation polygons** (`poly2d`), and **3D cuboids** (`cuboid`).
- **Classes Observed:** `CAR`, `TRUCK` (high-density motorway traffic).

### 1.3 Label Semantics & LiveCross Fit
- **Actual Collisions vs. Potential Conflicts:** TUMTraf labels actual, high-speed motorway crashes (collisions, overturns, rear-ends). LiveCross is specifically designed to detect *pre-collision potential conflicts* and near-miss interactions at fixed crossings.
- **Environment Gap:** High-speed Autobahn motorway vs. urban pedestrian intersection. There are no marked crosswalks, traffic signals, or pedestrians.
- **Verdict:** Highly valuable for testing and benchmarking multi-object vehicle detection and tracking from elevated roadside cameras. However, it **cannot** serve as ground truth for intersection conflict evaluation or VRU interaction types.

---

## 2. DoTA (Detection of Traffic Anomaly)

### 2.1 Source, Access & Infrastructure
- **Official Repository:** [MoonBlvd/Detection-of-Traffic-Anomaly](https://github.com/MoonBlvd/Detection-of-Traffic-Anomaly)
- **Publication:** Yao et al., *"DoTA: Unsupervised Detection of Traffic Anomaly in Driving Videos"*, IEEE TPAMI 2022.
- **Downloaded Assets:** Preserved under [`data/raw/dota/`](../data/raw/dota/):
  - `DoTA_annotations.zip`: 10,357,806 bytes (4,677 clip annotations, 477,650 frames).
  - `metadata_train.json`: 696,987 bytes (3,275 clips).
  - `metadata_val.json`: 295,463 bytes (1,402 clips).
  - `train_split.txt` & `val_split.txt`: Official split definitions.
  - `DoTA_urls.txt`: 8,096 bytes (Source YouTube mappings).
- **Video Storage Gate:** Raw video frames are hosted on Google Drive (~55 GB total, split into 5× 10 GB + 1× 5 GB archives). Access requires interactive Google account download. Automated video harvesting via `download_DoTA.py` requires `yt-dlp`, `ffmpeg`, and a YouTube cookie file to access age-restricted dashcam crash videos.
- **License:** Code and annotations are MIT licensed. Raw video clips are sourced from YouTube dashcam channels and cannot be redistributed without third-party authorization.

### 2.2 Split Leakage Audit (Critical Finding)
Applying LiveCross's strict split integrity standard ([`docs/data-card.md`](data-card.md)):
- **Train Split:** 3,275 clips originating from 188 distinct YouTube source videos.
- **Val Split:** 1,402 clips originating from 179 distinct YouTube source videos.
- **Source Video Overlap:** **177 source videos appear in BOTH Train and Validation!**
- **Leakage Severity:** **94.1% of training source videos are leaked into validation.** The official DoTA benchmark splits clips temporally within identical recording sessions. This violates LiveCross's sequence-level split requirement and causes severe leakage of camera intrinsic parameters, dashboard reflections, weather, and vehicle appearance.

### 2.3 Label Semantics & LiveCross Fit
- **Camera Perspective:** 100% egocentric moving dashcams. LiveCross requires a fixed roadside or overhead camera. Trajectory velocity in DoTA conflates ego-vehicle motion with scene actor motion.
- **Class Breakdown:**
  - *Vehicle–vehicle anomalies:* Turning (1,696 clips), Lateral (726 clips), Moving ahead/waiting (663 clips), Oncoming (478 clips).
  - *Pedestrian anomalies:* 100 clips (61 train, 39 val) capturing pedestrian-vehicle near-misses and collisions from dashcams.
  - *Fixed-obstacle anomalies:* 95 clips (59 train, 36 val) capturing collisions with road debris, stationary wrecks, and construction barriers.
- **Verdict:** DoTA provides a rich taxonomy of real-world road anomalies, but its moving egocentric viewpoint and severe train-to-val scene leakage make it unsuitable as a primary benchmark for fixed-crossing safety review. It may serve only as a secondary exploratory comparator.

---

## 3. JRDB & JRDB-Social

### 3.1 Source, Access & Infrastructure
- **Official Portal:** [jrdb.erc.monash.edu.au](https://jrdb.erc.monash.edu.au/)
- **Publications:** Rezatofighi et al. (CVPR 2022), Vendrow et al. (CVPR 2023).
- **Access Gate:** **Strictly gated behind account registration and user verification.** Anonymous or unauthenticated API downloads are blocked by design.
- **License:** **CC BY-NC-SA 3.0** (Attribution-NonCommercial-ShareAlike).

### 3.2 Semantic & Operational Mismatch (Critical Finding)
1. **Zero Road Vehicles:** JRDB was collected on Stanford University campus corridors, plazas, and pedestrian malls by the JackRabbot mobile robot. There are zero cars, trucks, or buses.
2. **Social Interaction ≠ Road Conflict:** JRDB-Social annotates human social behavior:
   - Level 1: Demographics (age, gender, race).
   - Level 2: Interpersonal interactions (`talking`, `walking together`, `gesturing`).
   - Level 3: Group activities (`queueing`, `meeting`, `conversing`).
   - *These are cooperative social interactions.* Inferring conflict or near-miss ground truth from two people walking together or standing close would directly violate LiveCross guideline §5 ("Do not infer conflict ground truth from proximity alone").
3. **Camera Perspective:** Low-profile mobile robot moving through pedestrians. Completely different optical flow, occlusion patterns, and viewpoint compared to an elevated roadside safety camera.
4. **Verdict:** **Not suitable for LiveCross conflict benchmarking.** Gated access and complete absence of vehicles or adversarial/collision scenarios make JRDB irrelevant to LiveCross's 5 interaction categories.

---

## Final Project Recommendation

1. **Retain U.S. DOT ISC Stage 1B** as the primary fixed-camera video source for VRU–vehicle interactions, maintaining its run-level label boundaries.
2. **Leverage TUMTraf-Accid3nD sample** for high-resolution vehicle detection and tracking pipeline verification (benefiting from native 2D bounding boxes and roadside camera geometry).
3. **Do not attempt to replace the project's manual annotation plan** with DoTA or JRDB:
   - DoTA's ego-camera dashcam perspective and 94.1% split leakage prevent reliable fixed-camera evaluation.
   - JRDB's social proximity annotations do not represent traffic collision conflicts.
4. **Maintain the staged/cleared fixed-camera recording protocol** defined in [`docs/dataset-expansion-plan.md`](dataset-expansion-plan.md) to close the remaining ground-truth gap across all 5 interaction categories.
