# LiveCross — Data Card

**Version:** 1.0

**Reviewed:** 15 November 2026
**Status:** Source inventory, camera choice, label boundaries, subset, and run split are documented. No project event labels or model results exist yet.

## Purpose and scope

This card describes the data currently downloaded and audited for LiveCross: three DOT archives used for RGB video, plus separate trajectory/video supplements. It does not describe the full approximately 1 TB DOT training corpus. The primary visual track uses fixed-camera video to study potential vulnerable-road-user–vehicle conflicts. LiveCross's five planned pair types are pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object; the DOT conflict labels support only the first of these at **run level**. The other types need separate permission-cleared, project-reviewed annotations and must be reported separately.

LiveCross is intended for human review of potential-conflict candidates. It is not an accident detector, crash predictor, certified warning system, or determination of fault. A source `conflict` label does not establish that an impact occurred.

## Primary source and collection context

**Source:** [U.S. DOT Intersection Safety Challenge Stage 1B](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4), collected at FHWA’s Turner-Fairbank Highway Research Center Smart Intersection facility in McLean, Virginia, from October 2023 through March 2024. The site is a controlled, signalized four-way intersection. The source describes one intersection instrumented with eight CCTV visual cameras, five thermal cameras, two LiDAR sensors, four radar sensors, and traffic-controller data. The scenarios include potential-conflict and non-conflict VRU–vehicle activity in daytime and nighttime conditions. DOT states that no human VRU was put at risk; surrogate VRU systems were used in the collection.

The official [DOT data story](https://data.transportation.gov/stories/s/U-S-DOT-Intersection-Safety-Challenge-Stage-1B-Sys/smqb-i5sx/) says visual-camera recordings are MP4 files accompanied by a CSV of per-frame timestamps. LiveCross currently uses the roadside **VisualCamera7** view, not a moving dash-camera view. It is a fixed 1280×720 stream that reports nominal 30 FPS in the inspected runs. The frame-timing CSV is the source of frame time: timestamps are irregular, so do not reconstruct event time from nominal FPS alone. The representative Run_1003 stream has 1,968 frames and 1,968 timestamp rows spanning 73.044 seconds, while 30 FPS would imply 65.6 seconds.

## Downloaded assets and roles

| Asset | Local inventory | Label/content scope | LiveCross role |
|---|---|---|---|
| DOT full validation archive | 41 runs; 28,642,566,098 bytes | Timestamped 3D road-user boxes and one `conflict`/`no conflict` value per run; inventory is 12 conflict and 29 no-conflict runs | Held-out test partition for DOT source-label reporting and future manually annotated event evaluation; never use for training, tuning, or hard-negative mining |
| DOT public training sample 1 | 10 runs; 8,161,594,056 bytes | Official training data is unlabeled | Eight complete runs assigned to train; two to development after manual review/annotation |
| DOT public training sample 2 | 10 runs; 5,148,222,990 bytes | Official training data is unlabeled | Eight complete runs assigned to train; two to development after manual review/annotation |
| DOT five-run validation sample | Five runs; 3,540,625,371 bytes | Two source-labeled conflict and three no-conflict runs | Used for initial access, schema, and decoding audit; not counted as a separate split because these runs are included in the full 41-run validation archive |
| DOT compact VisualCamera7 subset | 10 complete runs from full validation; 344,268,302 video bytes (about 328.4 MiB), plus timestamp CSVs | Five source-run conflict and five source-run no-conflict; three daylight and two low-light reviewed midpoints per label group | Balanced inspection/evaluation candidate subset, wholly inside test; not representative of natural prevalence and not event-labeled |

All 61 unique runs in the two training samples and full validation archive are recorded once in [`data/manifests/splits.csv`](../data/manifests/splits.csv). Seed 42 is used for deterministic, archive-balanced train/development assignment: eight train and two development runs from each training sample. All 41 official validation runs are held out as test. The training archives have no source conflict classes, so class stratification for train/development is impossible. Test source labels are known at run level (12/29); only future project-created event labels must remain unavailable to model and threshold selection. See the reproducible [split audit](../results/audits/sequence-split-audit.json).

The compact subset selection is described in [`compact-subset-selection.md`](compact-subset-selection.md). It uses whole runs, one fixed roadside view covering the intersection/crosswalk, source-label balance, and qualitative midpoint-light strata. All 10 streams are 1280×720 and report 30 FPS; their supplied timestamp spans total 441.422 seconds (about 7 minutes 21 seconds). The five-run sample is a duplicate view of runs in the full validation archive, not an independent evaluation set. The compact subset does not assign a run label to each frame or actor pair.

## Labels and annotation status

DOT validation provides:

- **Run-level conflict/no-conflict labels.** The metadata describes conflict ground truth in terms of TTC and road users with intersecting paths, but the label file provides no event start/end time, responsible actor-pair ID, or ambiguous class. The metadata does not specify a numeric TTC threshold. Do not expand the run label across frames or pairs.
- **Timestamped 3D road-user boxes** in the LiDAR 2 coordinate frame. These are not automatically RGB boxes. A projection feasibility audit for Run_1003 / VisualCamera7 produced visibly misaligned boxes; those projections are not approved as image-space ground truth. See [`projection-audit.md`](projection-audit.md).
- **No event-level LiveCross annotations yet.** Conflict candidate, non-conflict interaction, and uncertain are project-created human labels defined in [`event-vocabulary.md`](event-vocabulary.md) and [`manual-annotation-protocol.md`](manual-annotation-protocol.md). Event times, pair type, IDs where visible, reviewer, provenance, and uncertainty reasons still need to be recorded before event-level training or scoring.

DOT labels cover the source's documented VRU–vehicle scenarios only. They do not validate vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object events. No source currently supplies RGB event labels for all five types. If a category lacks enough independent annotated clips, mark it exploratory rather than pooling its results with another category. Frozen metric targets and the sample-size gate are in [`acceptance-targets.md`](acceptance-targets.md).

## Separate supplementary sources

These sources are not mixed into the DOT split or its metrics:

| Source | Audited content | Intended use and exclusion |
|---|---|---|
| FHWA TGSIM Foggy Bottom | 342,323,446-byte trajectory CSV; 2,492,261 rows and 20,511 IDs | Motion-feature and candidate-window research only. No RGB or source conflict labels; derived thresholds are surrogate labels. |
| ROCO sample | 25,063,270-byte archive; 101 labeled vehicle-conflict trajectory events and 8,080 trajectory-frame JSON files; no RGB | Separate trajectory-only vehicle-conflict study, not visual evaluation. The sample contains three severity-2 traffic-accident records, but no accident video. CSV parsing caveat and CC BY-SA 4.0/additional terms are recorded in the audit. |
| Waterloo Intersection | 14 AVI/SQLite pairs with track data; route conflict points are geometric path intersections, not observed pairwise events | Not part of the core/public evaluation: the publisher page does not state reuse terms. Do not redistribute or publish derived clips until permission is established. |

See [`supplemental-data-audit.md`](supplemental-data-audit.md) and its reproducible [`audit report`](../results/audits/supplemental-dataset-audit.json) for schemas, terms, citations, and parsing limits. The full DOT training corpus (1,104 runs, about 1 TB) was not requested or downloaded: it is unlabeled and outside the current course-sized download plan; the public samples still require project annotations before supervised event training. Calibration archives and non-RGB DOT sensors are not part of the current RGB split; calibration material was consulted only for the projection feasibility review.

## Selection, preprocessing, and reproducibility

- Keep each source run intact in one partition. Never randomly split adjacent frames from one run.
- The 10-run compact subset uses complete VisualCamera7 MP4s plus matching timestamp CSVs. Their midpoint light labels are qualitative visual-review strata, not dataset annotations.
- Only the selected validation videos and timing CSVs are extracted under the Git-ignored `data/raw/selected-validation/`; the source ZIP archives remain intact. The compact video payload is about 328.4 MiB. No full multi-sensor extraction is required.
- A local [inspection gallery](inspection-gallery.md) samples five timestamped context frames from each of the 61 runs (16 train, 4 development, 41 test). Its images and HTML remain under Git-ignored `data/processed/inspection-gallery/`; it does not add event labels or track boxes.
- Rebuild the source-run split with `python scripts/create_sequence_split.py`. Rebuild the compact inventory with `python scripts/build_compact_subset_manifest.py`; rebuild the gallery with `python scripts/build_inspection_gallery.py`.
- Future staged or permission-cleared footage must be added by complete recording session to the split procedure before model predictions are inspected. It is not in the present 61-run manifest.

## Bias, privacy, terms, and excluded use

Known limitations and biases:

- Data come from one controlled intersection and one fixed-camera viewpoint in the selected RGB track; this is not independent-location validation or natural traffic prevalence.
- Scenarios are experimental and include surrogate VRUs; their motion may not represent natural human behavior. Conditions include day and night but do not establish broad weather or camera coverage.
- The 5/5 compact subset is deliberately balanced against a 12/29 source-label distribution. Do not use it to estimate real-world prevalence.
- Training samples are unlabeled, and event labels/actor pairs are absent. Visual quality, glare, occlusion, and difficult/uncertain event classes have not been formally annotated.
- Current RGB box projection is not approved; do not report image-space detection metrics from those projected boxes.

The DOT validation catalog marks access and rights as public, but does not expose a separate validation-specific license field; this is not blanket permission to republish all raw or derived media. Preserve the official citation/access date in [`dataset-access.md`](dataset-access.md), keep raw archives and generated imagery out of Git, process locally, and check terms before external sharing or publication. Before sharing any imagery, inspect for faces, plates, or other identifying details and blur them where needed. LiveCross does not identify people or track identity across sessions. Any future staged footage requires permission/consent and safe staging; never record or stage beside active traffic. Waterloo media remain excluded until reuse rights are confirmed.

The following are outside the current card's supervised visual scope: the full unlabeled 1 TB training corpus, the duplicate five-run sample as an independent split, non-RGB LiDAR/radar/thermal/controller streams in the MVP, trajectory-only TGSIM/ROCO as image ground truth, Waterloo footage pending terms, and any future staged clips until they are permission-cleared and assigned to a source-session split.

## Sources and related records

- [Official DOT Stage 1B validation data page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4) and [DOT collection/data story](https://data.transportation.gov/stories/s/U-S-DOT-Intersection-Safety-Challenge-Stage-1B-Sys/smqb-i5sx/).
- [`dataset-access.md`](dataset-access.md) records download sizes, terms, and recommended citations.
- [`dataset-decision.md`](dataset-decision.md) explains why PIE is not a conflict-label-compatible fallback.
- [`dataset-expansion-plan.md`](dataset-expansion-plan.md) specifies the supplemental annotation route and five-type evidence gap.
- [`risk-register.md`](risk-register.md) records privacy, data-use, and evaluation risks.

**Update this card** when permission-cleared footage is added, event annotations are created, the split changes for a documented pre-test reason, camera projection is validated, or source terms change.
