# LiveCross — Event Vocabulary

**Status:** Operational definitions with DOT Stage 1B sample mappings recorded below. Mappings preserve the source level and do not turn run labels into event labels.

## Core terms

| Term | Working definition | Annotation / modeling rule |
|---|---|---|
| **Actor** | A moving tracked road user or a configured fixed scene hazard. | Moving actors have temporary track IDs; fixed hazards have scene-config IDs and no motion track. |
| **Pair type** | The typed combination under review: pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object. | All five are MVP categories. DOT supplies only a run-level VRU–vehicle conflict label, not event/pair labels; all other categories require separate annotations and evaluation. |
| **Interaction** | A time-bounded episode in which two actors are relevant to the same configured conflict area or have sufficiently close predicted paths in the same analysis window. | An interaction is a candidate pair for review. It is not automatically dangerous or a near miss. |
| **Conflict candidate** | An interaction for which the current motion rule or learned filter estimates that two moving actors may occupy overlapping space at close times, or a moving vehicle may approach/intersect a configured fixed-hazard region. | This is LiveCross’s model output, not ground truth that a near miss or crash occurred. Store the score, rule conditions, actor IDs, and time range. |
| **Non-conflict interaction** | A comparable interaction that the dataset annotation guide or documented human review identifies as non-conflicting/safe for the project’s defined task. | Do not label an example negative solely because LiveCross did not alert. Preserve the source of the negative label. |
| **Uncertain** | The available video or annotation does not support a reliable conflict/non-conflict decision. | Keep it as a separate review state; exclude it from binary training/evaluation unless it is later adjudicated under a documented rule. |
| **Occluded** | A road user or relevant part of the path is hidden or truncated enough to weaken the interaction evidence. | Record as an uncertainty reason. Occlusion alone does not prove either conflict or non-conflict. |
| **Event start** | The earliest timestamp in a continuous interaction interval that meets the configured event rule after any persistence/smoothing requirement. | The exact persistence duration and time-window values are configuration decisions for the risk-scoring tasks; they are not fixed here. |
| **Event end** | The last timestamp in that continuous qualifying interval before the interaction no longer meets the configured rule. | Retain the source sequence and frame/time bounds so the interval can be replayed. |
| **Duplicate event** | Two event records for the same sequence and same actor pair whose time intervals overlap or fall within the configured merge gap. | Merge for display into one event with a combined interval; preserve the raw prediction windows for audit and metric calculation. The merge gap is a later configuration decision. |

## Labeling principles

1. **Keep observation, model output, and reference label separate.** Store the raw dataset label, LiveCross prediction, and any human review label in separate fields.
2. **Do not equate crossing intention with conflict.** A person intending to cross is not necessarily in conflict with a vehicle; a conflict candidate is not proof of a near miss.
3. **Use three states when evidence is incomplete.** A binary task may use conflict/non-conflict only after source labels are understood; ambiguous samples remain uncertain or excluded.
4. **Record provenance.** Every reference label must point to an official annotation field or a documented manual-review decision, including reviewer and reason where applicable.
5. **Do not force occluded or poorly tracked samples into the negative class.** Track quality affects whether the example can be judged.

## Dataset label mapping — DOT ISC Stage 1B Validation Sample

The DOT metadata PDF and data dictionary were inspected, and the sample label file plus representative positive/negative run footage were reviewed. Preserve the raw source strings and never infer finer labels than the source provides.

| Dataset / version | Original field/value | Annotation level | LiveCross mapping | Evidence and example | Usable for MVP? |
|---|---|---|---|---|---|
| DOT ISC Stage 1B Validation Data Sample | `Conflict_No_Conflict_Label = conflict` | Run/scenario | `source_run_conflict_positive` (DOT-defined potential conflict run) | Metadata §4.3.2 says run conflict GT is based on TTC when two road users have a path intersection point. Sample positives: `Run_1023`, `Run_1290`. A representative midpoint from `VisualCamera3_Run_1023.mp4` was inspected. The metadata does not provide the TTC cutoff, event interval, or actor-pair ID in this label file. | **Yes, at run level only** for source-label reporting/stratification and candidate review. **No** as a timestamped event or actor-pair training/evaluation target. It does not prove an impact occurred. |
| DOT ISC Stage 1B Validation Data Sample | `Conflict_No_Conflict_Label = no conflict` | Run/scenario | `source_run_conflict_negative` (DOT-defined non-conflict run) | Same metadata definition. Sample negatives: `Run_1003`, `Run_108`, `Run_850`. A representative midpoint from `VisualCamera4_Run_1003.mp4` was inspected. The footage contains scene activity, but a frame alone cannot verify the full-run label. | **Yes, at run level only.** It is not a negative label for every frame, actor pair, or interaction in that run. |
| DOT ISC Stage 1B Validation Data Sample | `Run_<id>_GT.csv`: `Time` plus `<subclass>_{xctr,yctr,zctr,xlen,ylen,zlen,xrot,yrot,zrot}` | Timestamped object state / 3D box | `source_actor_3d_box` with original subclass and timestamp | Metadata §§4.2–4.3 defines 18 road-user subclasses and says GT boxes are in the LiDAR 2 frame; one row records visible actors at a time. Run_1003 includes `Passenger_Vehicle`, `VRU_Child`, and `VRU_Adult_Using_Walker`. | Useful as source 3D annotation. **Not currently usable as 2D RGB boxes** for Run_1003 / Visual Camera 7 because the projection audit did not show reliable alignment. Not a conflict/event label. |
| DOT ISC Stage 1B Validation Data Sample | Empty/missing subclass columns at a timestamp | Missing object observation | `not_observed_in_source_gt` | The GT schema has no documented conflict meaning for an empty class block. | Do not map to non-conflict; it may mean no visible annotated actor of that subclass at that timestamp. |
| DOT ISC Stage 1B Validation Data Sample | No explicit uncertain/ambiguous value in the run-label CSV | Not provided by source | `uncertain` only when assigned by documented human review | The inspected sample label file contains only `conflict` and `no conflict`; no third state or ambiguous examples are provided. | Keep human uncertainty separate from the raw DOT label. Occluded, poorly aligned, or unclear footage must not be forced into either binary class. |

### Mapping boundary

The DOT source label can support a **run-level VRU–vehicle scenario target** consistent with the metadata description. It cannot supervise LiveCross’s event start/end times, identify which actor pair caused a run label, provide per-frame conflict/non-conflict tags, or validate vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, or pedestrian–fixed-object interactions. Do not expand a run label across every frame. Use separately reviewed event annotations for event-level model training and metrics; preserve `source_label`, `review_label`, and model prediction in separate fields.

### Mapping decision checklist

- [x] Record the official definition and annotation unit for each available raw label.
- [x] Inspect positive and negative sample run labels and representative footage; source provides no uncertain/ambiguous value to inspect.
- [x] Distinguish run-level potential-conflict labels from event-level labels and observed collisions.
- [x] Record mapped and excluded labels in this vocabulary and the data card before creating training labels.
- [x] Keep event-level targets as a separate, explicitly reviewed annotation set; do not silently relabel source runs.

## Event record fields

Each reviewed event should retain, when available: `event_id`, `sequence_id`, `source_label`, `livecross_label`, `review_label`, `review_reason`, `pair_type`, `start_time`, `end_time`, `actor_a_track_id`, `actor_b_track_id`, `fixed_hazard_id`, `track_quality`, `conflict_score`, `triggered_factors`, `uncertainty_reason`, and `mapping_version`. A fixed hazard has a scene-config ID rather than a track ID.
