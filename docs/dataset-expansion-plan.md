# LiveCross — Dataset Expansion Plan

**Decision:** The data currently downloaded is **not sufficient for final evaluation** of the five-interaction MVP. Keep the DOT five-run sample as the access and pipeline pilot. Expand evaluation in separate, auditable tracks; no single source currently supplies labeled video ground truth for all five interaction types.

## Existing data

| Source | What it can support | What it cannot support | Project use |
|---|---|---|---|
| U.S. DOT Intersection Safety Challenge Stage 1B five-run validation sample (3.54 GB locally) | RGB video and timestamps; VRU–vehicle scenario labels at run level; timestamped 3D road-user boxes | Event-boundary labels are absent in the inspected sample; labels do not establish vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object truth | Pipeline smoke check and manual event-window pilot; not strong final metric evidence |
| Full DOT Stage 1B validation set (41 runs, about 28.64 GB locally) | Larger held-out validation pool for DOT’s VRU–vehicle scenarios; same source-specific labels | Does not validate vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object; still requires event-level annotation and validated RGB projection | Benchmark track for DOT VRU–vehicle results, with whole-run splits |
| DOT public training samples 1 and 2 (about 12.9 GB combined) | Additional recorded runs for training/development clips and hard-negative mining after manual review; useful RGB footage if the relevant views are present | Official training data is unlabeled; it cannot supply conflict labels without human review and it is not a test set | Use as training/development source only; preserve run separation from validation |

## Downloaded motion/conflict supplements (audited 15 November 2026)

Three downloaded sources have now been inspected locally. Full counts, schema, parsing caveats, and rights decisions are recorded in [`supplemental-data-audit.md`](supplemental-data-audit.md) and reproducible via [`scripts/audit_supplemental_data.py`](../scripts/audit_supplemental_data.py).

### FHWA TGSIM Foggy Bottom

The local CSV is 342,323,446 bytes with 2,492,261 rows, 20,511 IDs, eight road-user types, and mostly 0.1-second within-track intervals. It has trajectory coordinates and motion fields, no RGB video, and no source conflict-event labels. Use it for trajectory feature experiments and candidate generation only. Any TTC/PET threshold is a project-defined surrogate, not observed or author-labeled ground truth. See the [official FHWA catalog](https://catalog.data.gov/dataset/third-generation-simulation-data-tgsim-foggy-bottom-trajectories) and [DOT TGSIM data story](https://data.transportation.gov/stories/s/Third-Generation-Simulation-Data-TGSIM-/uwv8-dpvx/) for units, code meanings, citation, and terms.

### ROCO

The local sample contains 101 vehicle conflict events and 8,080 trajectory JSON frame files, with author-provided severity/reason/effect labels. It has no video frames and only vehicle events, so it can support a **separate trajectory-only vehicle conflict experiment**, not video detection, pedestrian interactions, fixed-object interactions, or image-space XAI. Its label CSV has a format quirk: unquoted pair IDs cause six physical fields under a five-column header; use the documented parser in the audit script. It is licensed CC BY-SA 4.0 with additional dataset terms; preserve attribution/share-alike. Source: [official ROCO repository](https://github.com/michigan-traffic-lab/ROCO).

### Waterloo Intersection

The local download contains 14 matched AVI/SQLite pairs. A representative database includes pedestrian tracks, vehicle tracks, and per-frame motion data. The publisher's `CONFLICT_POINTS` are intersections of planned/geometric paths, **not event labels** for a tracked pair. This is a candidate visual/tracking demo, pending validation of frame/ID alignment and explicit reuse permission. The [WISE Lab dataset page](https://uwaterloo.ca/waterloo-intelligent-systems-engineering-lab/datasets/waterloo-multi-agent-traffic-dataset-intersection) does not state a license; do not redistribute or make it a required public deliverable until terms are confirmed.

## Fill the fixed-object and visual-evidence gap

Create a small supplemental video set from **permission-cleared, safely staged recordings** at a stationary camera view. Include ordinary passes and controlled path-near-object cases for both vehicles and pedestrians around a configured static hazard (for example, a traffic cone or marked, non-moving stand-in); never stage an actual collision or place an obstacle in live traffic. Also stage or source suitable vehicle–vehicle and pedestrian–pedestrian examples if the public trajectory supplement cannot supply sufficient category coverage.

For every clip, record source, permission/consent, scene, category, pair IDs, timestamps, positive/non-conflict/uncertain decision, and reviewer. Keep all clips from one recording session together in one split. Do not publish identifiable raw footage or derived clips without permission. These annotations provide project-specific event labels, not an external benchmark.

## Evaluation plan and stop/go gate

1. Keep the DOT benchmark results for VRU–vehicle separate from all supplementary results.
2. Report TGSIM motion-feature experiments separately; clearly tag any derived conflict outcome as a surrogate.
3. Use ROCO only for a separate vehicle-trajectory event-label analysis; do not report it as visual model evaluation.
4. Keep Waterloo out of public redistribution and core evaluation until its reuse terms and video/ID alignment are confirmed.
5. Use staged/cleared video to exercise and evaluate the visual pipeline for all five interaction types, reporting its small sample size and non-independent annotation limitation clearly.
6. Preserve complete runs or recording sessions as groups across train/development/test. Mine hard negatives from training only.
7. Report per-category counts, event precision/recall/F1, false alerts per minute, and delay only where annotations support them. If a category has too few independent test examples, mark it exploratory; do not pool it with another category.
8. Before claiming final benchmark-level performance, inspect DOT’s full 41-run validation data, read the complete annotation guide, and confirm whether the relevant 3D boxes can be projected into the chosen RGB camera.

**Current readiness:** MVP implementation can proceed on the current sample, but a strong final five-type evaluation cannot. The data expansion above is now a project task and the necessary evidence boundary is part of the plan. The public DOT training samples are included for practical manual training/mining data; the roughly 1 TB full training archive remains unnecessary for this student-scale project.
