# LiveCross dataset-alignment decision

**Decision date:** 15 November 2026  
**Decision:** Keep DOT Stage 1B as LiveCross's primary video source; do not switch the project to PIE. This decision is conditional on creating a project-reviewed event annotation set before training or reporting event-level metrics. The downloaded DOT labels alone do **not** support that event-level target.

## Exact target being supervised

LiveCross is a **potential-conflict review tool**, not a crash predictor. Its event model is intended to classify a time-bounded, typed interaction window as:

- `conflict_candidate`: human reviewers judge the observed/predicted paths and timing to meet the project's operational conflict criteria;
- `non_conflict_interaction`: a comparable interaction that reviewers judge not to meet those criteria;
- `uncertain`: the video, tracking, or geometry is insufficient to decide.

The typed categories remain pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object. Fixed hazards are manually configured scene regions. A `conflict_candidate` is not an observed collision, a probability of injury, or a statement that a crash would have occurred.

These labels are **project-created human annotations** attached to source video. They are not present as event-level pair labels in the DOT source files. Keep the source's raw label, each human review label, and model output in separate fields. Apply the annotation protocol and uncertainty state in [`event-vocabulary.md`](event-vocabulary.md) and [`manual-annotation-protocol.md`](manual-annotation-protocol.md).

## Candidate comparison

| Candidate | What the source actually labels/provides | Fit to the defined target | Decision |
|---|---|---|---|
| **DOT ISC Stage 1B** | Fixed-intersection multi-sensor video, frame timestamps, 3D actor boxes, and conflict/no-conflict labels at run/scenario level. The audited RGB projection is not approved as image-space ground truth for the selected run/camera. | Best available source for the project's fixed-camera video setting. Its native labels are too coarse for event/pair supervision, so a separate reviewed event set is mandatory; retain native run labels only for a separate coarse report/stratification. | **Primary video source, with manual event labels.** Do not train event models from run labels or claim image-space box metrics from the failed projection. |
| **PIE** | Over six hours of 30 FPS, 1920×1080 Toronto dash-camera footage, pedestrian/vehicle/infrastructure boxes, per-frame pedestrian behavior, and human-study crossing-intention annotations. The dataset authors describe the task as pedestrian intention estimation and trajectory prediction. | Strong fit for **pedestrian crossing-intention prediction**. It does not provide pairwise near-miss/collision-event labels for the five LiveCross interaction types. It also changes the camera viewpoint from a fixed roadside view to an ego-vehicle dash camera. | **Do not switch for the current project.** Use PIE only if the project is explicitly re-scoped to pedestrian crossing anticipation; that would be a different project objective. |
| **ROCO** | Event-level vehicle-conflict labels and 2.5 Hz vehicle trajectories in the released sample, but no RGB video. | Useful for a separate trajectory-only vehicle-conflict analysis, not for the visual event model or pedestrian/fixed-object types. | Supplementary trajectory analysis only; keep separate from video metrics. |
| **Waterloo Intersection** | Overhead videos paired with agent-ID/trajectory databases. Route conflict points are geometric path intersections, not labeled conflict events. The publisher page and direct ZIP links provide no explicit reuse license. | Could be visually relevant, but neither its event labels nor reuse permission currently meet the requirement for a core public benchmark. | Exclude from core evaluation and public artifacts unless terms are confirmed and events are independently annotated. |
| **TGSIM Foggy Bottom** | Road-user trajectories at mostly 0.1-second intervals, with no RGB video and no source conflict-event labels. | Useful for motion-feature and candidate-generation experiments, but not visual supervision. | Motion-analysis supplement only; derived conflict thresholds must be called surrogate labels. |

PIE facts and terms were checked against the [official PIE dataset page](https://www.data.nvision2.eecs.yorku.ca/PIE_dataset/) and the [ICCV paper](https://openaccess.thecvf.com/content_ICCV_2019/html/Rasouli_PIE_A_Large-Scale_Dataset_and_Models_for_Pedestrian_Intention_Estimation_ICCV_2019_paper.html). The dataset page lists the videos and annotations under MIT terms. Its labeled task is pedestrian intent/action, not LiveCross's conflict-event target.

## Supervision route by interaction type

| LiveCross type | What DOT can establish | Annotation route for the LiveCross event target | Current evidence boundary |
|---|---|---|---|
| Pedestrian–vehicle (and bicyclist–vehicle where visible) | DOT's run-level conflict/no-conflict label applies to its VRU–vehicle scenario; its timestamped 3D boxes are in LiDAR coordinates and are not approved as RGB boxes for the audited camera. | Manually review permitted, complete RGB clips and assign event intervals, visible actor IDs, and conflict/non-conflict/uncertain status under the project protocol. Preserve the raw run label separately. | The selected DOT pool is only a source-labeled candidate pool. It is not event-labeled and does not meet the per-type event sample gate yet. |
| Vehicle–vehicle | No vehicle–vehicle conflict/event ground truth is supplied by the DOT run label. | Use a permission-cleared clip where two vehicle tracks are both visible; annotate their interaction and event interval manually. Use DOT footage only if inspection confirms the pair is actually present and reviewable; otherwise use the separately documented supplemental clip set. | No verified vehicle–vehicle event annotations are present yet. |
| Pedestrian–pedestrian | No pedestrian–pedestrian conflict/event ground truth is supplied by the DOT run label. | Use permission-cleared footage with two visible pedestrian tracks; annotate the pair and interval manually. Use DOT footage only if inspection confirms a suitable interaction; otherwise use the supplemental clip set. | No verified pedestrian–pedestrian event annotations are present yet. |
| Vehicle–fixed-object | No vehicle–fixed-object event ground truth is supplied by DOT. | Select permission-cleared footage with a visible static hazard; record the hazard's stable scene ID and configured image-space footprint/buffer, then manually annotate vehicle path interaction and uncertainty. Safe staged footage may use a non-hazardous stand-in. | No verified vehicle–fixed-object event annotations or calibrated physical distances are present yet. |
| Pedestrian–fixed-object | No pedestrian–fixed-object event ground truth is supplied by DOT. | Select permission-cleared footage with a visible static hazard; record the hazard's stable scene ID and configured image-space footprint/buffer, then manually annotate pedestrian path interaction and uncertainty. Safe staged footage may use a non-hazardous stand-in. | No verified pedestrian–fixed-object event annotations or calibrated physical distances are present yet. |

For every type, save source and permission/terms provenance, source clip/run, timestamps from the source stream, pair type, IDs where visible, reviewer, annotation version, and uncertainty reason. Annotate without model predictions where practical; split by complete source recording before model tuning; mine hard negatives from training recordings only. The protocol's numeric proximity, persistence, and timing thresholds are still to be configured and frozen in the later interaction-scoring/evaluation work. This decision does not claim that the needed annotation set already exists.

## Fallback decision

**No fallback now.** DOT footage is available and matches the fixed-camera review setting. Its source labels remain usable for their actual run-level meaning, but they do not provide the event-level training target. PIE would solve a different supervised task—crossing intention—and would not supply the missing pairwise conflict labels or the other four interaction categories. Switching to PIE while retaining LiveCross's current title and claims would therefore be a target mismatch, not a data-quality improvement. The [official DOT validation page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4) describes potential-conflict scenarios and run-level binary labels; the [official PIE page](https://www.data.nvision2.eecs.yorku.ca/PIE_dataset/) describes pedestrian behavior and crossing-intention annotations. Neither source provides event labels for all five LiveCross types.

This is a conditional decision, not evidence that the current files already contain enough labels. **Before fitting the event classifier or making event-level performance claims**, LiveCross must have a permission-cleared, source-separated annotation set with event times, pair type, actor/hazard IDs where visible, reviewer, uncertainty state, and train/development/test assignment by complete source clip/run. If this cannot be assembled at the minimum counts in [`acceptance-targets.md`](acceptance-targets.md), report the affected types as exploratory and do not claim successful supervised evaluation. If manual event labeling is abandoned, reopen the fallback decision and re-scope to an explicitly defined crossing-intention task using PIE.

## Consequences for project claims

1. Describe DOT as the primary **video source** and a limited run-level reference, not as native event-level ground truth.
2. Describe event-level conflict labels as created by the project under a documented human-review protocol.
3. Describe the experiment as rule/SVM learning on those reviewed event windows, with training-only hard-negative mining and per-category reporting.
4. Keep PIE, ROCO, TGSIM, and Waterloo evidence in separate tracks; do not merge incompatible labels or pool metrics across sources.
5. The project remains five-category in scope, but a category without enough permission-cleared, independent labeled clips must be marked exploratory.
