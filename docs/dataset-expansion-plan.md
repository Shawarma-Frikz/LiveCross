# LiveCross — Dataset Expansion Plan

**Decision:** The data currently downloaded is **not sufficient for final evaluation** of the five-interaction MVP. Keep the DOT five-run sample as the access and pipeline pilot. Expand evaluation in separate, auditable tracks; no single source currently supplies labeled video ground truth for all five interaction types.

## Existing data

| Source | What it can support | What it cannot support | Project use |
|---|---|---|---|
| U.S. DOT Intersection Safety Challenge Stage 1B five-run validation sample (3.54 GB locally) | RGB video and timestamps; VRU–vehicle scenario labels at run level; timestamped 3D road-user boxes | Event-boundary labels are absent in the inspected sample; labels do not establish vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object truth | Pipeline smoke check and manual event-window pilot; not strong final metric evidence |
| Full DOT Stage 1B validation set (41 runs, about 28.64 GB locally) | Larger held-out validation pool for DOT’s VRU–vehicle scenarios; same source-specific labels | Does not validate vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object; still requires event-level annotation and validated RGB projection | Benchmark track for DOT VRU–vehicle results, with whole-run splits |
| DOT public training samples 1 and 2 (about 12.9 GB combined) | Additional recorded runs for training/development clips and hard-negative mining after manual review; useful RGB footage if the relevant views are present | Official training data is unlabeled; it cannot supply conflict labels without human review and it is not a test set | Use as training/development source only; preserve run separation from validation |

## Add a public motion-data supplement

Use **FHWA TGSIM Foggy Bottom trajectory data** as a separate motion-analysis supplement. The official catalog lists a roughly 350 MB trajectory CSV covering pedestrians, bicycles, scooters, cars, automated vehicles, motorcycles, buses, and trucks, sampled every 0.1 seconds, along with an aerial reference image and roadway-region polygons. It is public and has four intersections in the collection. This provides a practical source for generating and manually checking candidate pedestrian–vehicle, vehicle–vehicle, and pedestrian–pedestrian trajectory windows, then testing motion features and pair-aware rules across those dynamic-agent interactions. It does not provide visual evidence or fixed-object pair labels.

Important boundary: the catalog describes trajectories and reference/region files, not a ready-to-use collection of per-event conflict labels or downloadable RGB clips. Treat any conflict labels derived from distance, time-to-collision, or post-encroachment rules as **surrogate labels**, define the rule before evaluation, and do not call them observed collisions or human-validated near misses. This supplement can test motion scoring; it cannot test the video detector or replace DOT video.

- Official FHWA catalog: [TGSIM Foggy Bottom Trajectories](https://catalog.data.gov/dataset/third-generation-simulation-data-tgsim-foggy-bottom-trajectories)
- Dataset landing page/resource access: [DOT data portal](https://data.transportation.gov/d/brzy-6zfh)
- Before use: inspect columns, units, participant IDs, missingness, region semantics, attribution, and use terms; save the access date and checksum in the experiment manifest.

## Fill the fixed-object and visual-evidence gap

Create a small supplemental video set from **permission-cleared, safely staged recordings** at a stationary camera view. Include ordinary passes and controlled path-near-object cases for both vehicles and pedestrians around a configured static hazard (for example, a traffic cone or marked, non-moving stand-in); never stage an actual collision or place an obstacle in live traffic. Also stage or source suitable vehicle–vehicle and pedestrian–pedestrian examples if the public trajectory supplement cannot supply sufficient category coverage.

For every clip, record source, permission/consent, scene, category, pair IDs, timestamps, positive/non-conflict/uncertain decision, and reviewer. Keep all clips from one recording session together in one split. Do not publish identifiable raw footage or derived clips without permission. These annotations provide project-specific event labels, not an external benchmark.

## Evaluation plan and stop/go gate

1. Keep the DOT benchmark results for VRU–vehicle separate from all supplementary results.
2. Use TGSIM only for trajectory/motion-feature evaluation unless visual videos and redistribution/use permissions are independently confirmed.
3. Use staged/cleared video to exercise and evaluate the visual pipeline for all five interaction types, reporting its small sample size and non-independent annotation limitation clearly.
4. Preserve complete runs or recording sessions as groups across train/development/test. Mine hard negatives from training only.
5. Report per-category counts, event precision/recall/F1, false alerts per minute, and delay only where annotations support them. If a category has too few independent test examples, mark it exploratory; do not pool it with another category.
6. Before claiming final benchmark-level performance, inspect DOT’s full 41-run validation set, read the complete annotation guide, and confirm whether the relevant 3D boxes can be projected into the chosen RGB camera.

**Current readiness:** MVP implementation can proceed on the current sample, but a strong final five-type evaluation cannot. The data expansion above is now a project task and the necessary evidence boundary is part of the plan. The public DOT training samples are included for practical manual training/mining data; the roughly 1 TB full training archive remains unnecessary for this student-scale project.
