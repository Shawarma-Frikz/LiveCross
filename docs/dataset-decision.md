# LiveCross — Dataset Alignment & Selection Decision

**Version:** 2.1
**Decision date:** 18 November 2026
**Scope:** Pedestrian–vehicle and vehicle–vehicle only

## Decision

The project targets two interaction categories, but the available data do **not** currently provide complete event-level video ground truth for either category. The source roles below are deliberately separated by modality and label meaning.

| Source | Current role | What it supports | What it does not support |
|---|---|---|---|
| **U.S. DOT ISC Stage 1B** | Primary fixed-camera video source for both target categories, with category-specific manual annotation required | Pedestrian/vehicle scenarios, fixed-camera video, and run-level conflict/no-conflict labels for the source's documented scenarios | Event boundaries or pair IDs; native vehicle–vehicle conflict labels; approved RGB boxes from the audited VisualCamera7 projection |
| **ROCO** | Separate vehicle–vehicle trajectory comparator | Author-provided vehicle conflict trajectory events and IDs | RGB video, visual detection/tracking, image overlays, or ground truth for DOT footage |
| **TUMTraf-Accid3nD sample** | Exploratory roadside vehicle-perception reference | Native image-space vehicle boxes/masks in a highway setting | Urban intersection conflict benchmark or pedestrian–vehicle coverage |
| **Waterloo Intersection** | Excluded from the public benchmark pending permission | Local archives contain video and track/context databases | Any public or published use until reuse terms are clarified; route intersection records are not verified conflict-event labels |
| **TGSIM** | Trajectory-method research only | Road-user trajectory features and candidate generation | RGB video or source conflict-event labels |
| **DoTA / JRDB** | Audited and not selected for primary evaluation | Taxonomy or general perception context only | Fixed-camera event ground truth matching the LiveCross targets |

## Category-specific plan

### Pedestrian–vehicle

Use DOT VisualCamera7 footage. Preserve the source conflict/no-conflict field as a **run-level scenario label** only. It must not be copied to every frame, actor pair, or event. Create project event windows only by reviewing continuous source video and recording timestamps, actors, uncertainty, split, and reviewer provenance. The existing two draft event records are not adjudicated and are ineligible for training or primary metrics.

### Vehicle–vehicle

Use DOT training/development video for the visual pipeline only after manually annotating vehicle pairs from continuous footage. DOT does not supply source vehicle–vehicle event labels. Use ROCO only as a distinct trajectory-only comparator; report its results separately and do not present them as visual benchmark performance. There are currently **zero** vehicle–vehicle video event rows.

## Split and evaluation policy

- Keep full source recordings indivisible. The existing DOT manifest assigns 16 training-sample runs to train, 4 to development, and 41 official validation runs to test.
- Do not use DOT run-level test labels to tune event-level thresholds or model features.
- Test contact sheets were generated as part of the inspection gallery. The repository does not establish whether a person viewed every test sheet; therefore, describe the test partition as **not used for model/threshold tuning**, but do not claim it was entirely unseen or content-blind.
- Keep any future data source in its own source-aware split and preserve source/modality distinctions in all reports.

## Scope exclusions

Pedestrian–pedestrian and vehicle-/pedestrian–fixed-object interactions are outside this project version. Waterloo is not a public benchmark unless the dataset publisher confirms reuse terms. Do not claim an event-level benchmark is ready until annotations are adjudicated and the per-category sample requirements in [`acceptance-targets.md`](acceptance-targets.md) are met or explicitly revised before test evaluation.

## Decision status

The **category scope is frozen**. Dataset readiness is **not frozen as complete**: DOT event labels require human review, and the visual vehicle–vehicle label set is absent. This decision supersedes earlier wording that described Waterloo as an active demo source or ROCO as an RGB/video benchmark.
