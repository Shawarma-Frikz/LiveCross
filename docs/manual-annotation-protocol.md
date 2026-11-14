# Manual Interaction Annotation Protocol

**Purpose:** Provide consistent event labels for interaction categories not fully labeled in the DOT benchmark, and event boundaries for DOT runs whose labels are only run-level. This protocol is provisional until the complete DOT annotation guide and sample coverage are inspected.

## Labels

Use three statuses:

- **Potential conflict:** The visible motion/path evidence meets the category rule below within the configured analysis window. This is a safety-review label, not proof of a near miss or collision.
- **Non-conflict interaction:** The same actor/object pair is observable and relevant to the scene, but its paths do not meet the category conflict rule during the full review window.
- **Uncertain:** Occlusion, timing mismatch, missing actor/object identity, or weak evidence prevents a reliable decision. Exclude from binary training and primary metrics unless adjudicated later.

Do not label an event positive merely because LiveCross flagged it. Annotate from the source clip without viewing model scores where practical. Keep the raw DOT run label separate from the manual event label.

## Category rules

| Pair type | What to annotate | Positive evidence | Negative example |
|---|---|---|---|
| Pedestrian–vehicle | A pedestrian/bicyclist track and a vehicle track approaching or using the same crossing/conflict area. | Their observed or projected paths overlap in the configured zone within the frozen temporal/proximity rule. | Both actors are observable, but their paths/timing remain separated through the window. |
| Vehicle–vehicle | Two distinct vehicle tracks using the same intersection/conflict area. | Their paths overlap in space and time within the same frozen rule. | Both tracks are observable, but their paths/timing do not converge within the window. |
| Pedestrian–pedestrian | Two distinct pedestrian tracks whose paths approach or cross in the analyzed area. | Their paths approach/cross within the frozen spatial/temporal rule. | Both tracks are observable but remain separated or pass without meeting the rule. |
| Vehicle–fixed-object | A vehicle track and a configured static obstacle with a stable scene ID and footprint/buffer polygon. | The vehicle’s predicted/observed path intersects that configured footprint/buffer within the analysis window. | The vehicle is visible near the object but its path remains outside the configured hazard region. |

Freeze the actual time, distance/proximity, and persistence thresholds after video/dictionary inspection and before held-out predictions are reviewed. If calibration is absent, record geometry in image coordinates and call it a proxy.

## Annotation record

Store one event per continuous interaction interval with at least:

`event_id`, `source_dataset`, `source_clip`, `source_run`, `split`, `pair_type`, `actor_a_class`, `actor_a_track_id`, `actor_b_class`, `actor_b_track_id`, `fixed_hazard_id`, `start_timestamp`, `end_timestamp`, `status`, `confidence`, `uncertainty_reason`, `annotation_notes`, `annotator_id`, `annotation_version`, and `source_label`.

For a fixed object, `fixed_hazard_id` and the saved scene geometry replace a second moving track ID. Preserve the original frame index and timestamp string; do not derive event time from nominal FPS when a frame-time CSV exists.

## Review and split controls

1. Confirm the clip is permitted for project use and document its source.
2. Review the full window around each candidate, not only the frame that triggered the rule.
3. Save conflict, non-conflict, or uncertain before reading model predictions whenever practical.
4. Have a second person review a subset if available; if solo review is used, record that there was no independent annotator and discuss this limitation.
5. Group all excerpts from the same source run/recording in one train/development/test split.
6. Mine hard negatives from training clips only. A reviewer must verify each mined safe example before adding it to classifier training.
7. Report every pair type separately. Do not pool categories into a single score that conceals a category with inadequate labels.
