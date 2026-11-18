# LiveCross — Acceptance Targets & Evaluation Protocol

**Version:** 2.1
**Status:** Target definitions are documented before model/test evaluation; targets are not results. Per-category feasibility remains pending label review.

## 1. Evaluation scope and evidence limits

The intended evaluation reports pedestrian–vehicle and vehicle–vehicle separately, using whole source recordings for split assignment. The DOT split assigns 16 public training-sample runs to train, 4 to development, and all 41 official validation runs to test. It is source-run-disjoint. A context gallery was generated across all splits, including test; the repository does not record whether test sheets were visually reviewed. Therefore, describe the DOT test as not used for model/threshold tuning in the current pilot, but do not claim a completely unseen or content-blind test set. No model predictions or test event labels are present in the current annotation pilot.

**Current data limits:** DOT labels are run/scenario-level, not event-level. The 10-run compact DOT subset is only a candidate video test pool until project event windows are adjudicated. DOT does not provide native vehicle–vehicle event labels. ROCO has source-labeled vehicle–vehicle trajectories but no RGB video and must be evaluated as a separate trajectory-only comparator. Waterloo is excluded from public evaluation until reuse terms are resolved.

## 2. Predeclared acceptance targets

These thresholds are intended project goals, not evidence of achieved performance. If a target is infeasible on development data, document and version a justified change before inspecting test predictions.

| ID | Metric | Target | Measurement |
|---|---|---|---|
| T1 | Event precision | $≥ 0.70$ | TP / (TP + FP), reported separately for each category. |
| T2 | Event recall | $≥ 0.70$ | TP / (TP + FN), against adjudicated event windows, separately per category. |
| T3 | False-alert rate | $≤ 0.5$ alerts/min | False alerts per annotated non-conflict video minute, per category. |
| T4 | Hard-negative mining impact | $≥ 20%$ relative FP reduction, recall drop $≤ 5$ percentage points | Compare fixed baseline and mined model on the same evaluation set; mine only from training sequences. |
| T5 | Alert delay | Median $≤ 1.5$ s | From earliest annotation-supported observable conflict cue to first alert. Define the cue consistently before evaluation. |
| T6 | End-to-end throughput | $≥ 15$ FPS | Decode, detection, tracking, risk logic, and rendering at 720p; report hardware and timing method. |
| T7 | Demo startup | $≤ 15$ s | From launch command to usable first playback screen, measured on documented hardware. |

No target is currently measured. T1–T5 require sufficient adjudicated event and non-conflict annotations; T6–T7 require an implemented application. If a category fails its sample minimum, mark its metrics exploratory or not estimable rather than treating an absent denominator as success.

## 3. Event matching

A predicted event matches a ground-truth event only when sequence and pair category match and temporal intersection-over-union is at least 0.30, or the overlap covers at least 50% of the shorter interval. Match each ground-truth event at most once. Count duplicate predictions as false positives unless a documented merge rule combines them. Freeze the exact implementation and any merge tolerance before test evaluation.

## 4. Reporting

- Report counts and denominators alongside rates, separately for each category and source.
- Keep ROCO trajectory results separate from video detection/tracking results.
- Report the transparent rule baseline and learned model only when the training labels support them.
- Include false-positive and false-negative examples, uncertainty, camera/domain limits, and all unmet targets.
- Do not claim collision prediction, safety improvement, or deployable warning performance from this prototype.
