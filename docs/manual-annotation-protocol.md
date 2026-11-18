# LiveCross Manual Annotation Protocol

**Scope:** Pedestrian–vehicle and vehicle–vehicle only.
**Status:** Qualitative pilot rule defined; numeric thresholds and v1 labels are not finalized ground truth.

## Label states

- **potential_conflict:** Continuous visual evidence supports plausible shared-space conflict for the pair under review. This is a review label, not proof of collision or crash inevitability.
- **non_conflict_interaction:** The pair is visible and relevant over the full window, and reviewed evidence supports that the conflict condition is absent.
- **uncertain:** Occlusion, identity, timing, or motion evidence is too weak to decide. Exclude from binary training and primary metrics unless resolved.
- **excluded:** The window is unusable or outside scope. It is not a negative.

Do not assign labels from model alerts, proximity alone, DOT run-level labels, or ROCO trajectory labels. Review from source video without model predictions where practical.

## Pair definitions

| Pair | Review rule | Example negative |
|---|---|---|
| Pedestrian–vehicle | A visible pedestrian and vehicle approach/use a shared crossing or conflict region; review their trajectories and timing over the continuous window. | Both are observable but pass without the project-defined convergence condition. |
| Vehicle–vehicle | Two visible vehicle tracks approach/use an intersecting path or junction region; review their trajectories and timing over the continuous window. | Both are observable but remain spatially or temporally separated. |

The operational geometry, time/proximity, persistence, and alert-merge thresholds are not yet frozen. Define and version them from training/development evidence before held-out evaluation. Without valid camera calibration, express spatial quantities as image-plane proxies.

## Annotation fields and review procedure

For each event/window, record the fields in `data/annotations/v1/events.csv`: source dataset/archive/run, split, pair type, actor classes and IDs where defensible, exact source start/end frame and timestamp, status, confidence, uncertainty reason, notes, annotator, annotation version, and review stage. Keep temporary reviewer IDs clearly distinguished from source track IDs.

1. Confirm the source is permitted for project use and preserve its citation/terms.
2. Prefer reviewing the continuous source clip, not just sampled contact sheets, around the whole interaction. If the student explicitly adopts an assistant-proposed label without separate playback, record that as assistant-assisted adjudication and disclose the limitation.
3. Confirm both actors and the pair type. Record uncertain or excluded when evidence is insufficient.
4. Save the decision and exact boundaries before consulting model output where practical.
5. Keep every excerpt from a source recording in the same split. Mine negatives from training data only.
6. Since the project is solo, record the student as annotator only for work the student personally performs. Do not claim independent review or inter-rater agreement.
7. Regenerate and inspect the machine summary after each annotation update. Draft assistant rows are not training labels or evaluation ground truth.

Assistant-proposed candidate windows and their visual-review limitations are recorded separately in [`assistant-first-pass-review-log.md`](assistant-first-pass-review-log.md). Keep that provenance record with the annotation table. A student may explicitly adopt a specific proposal, but the record must say that the label is assistant-assisted and must not imply independent student visual review or a second annotator.

The generic annotation schema retains a fixed-hazard field for possible later work, but fixed-object and pedestrian–pedestrian categories are out of scope for this version.
