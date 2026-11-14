# LiveCross — Event Vocabulary

**Status:** Provisional operational definitions. These define how LiveCross will describe its own observations; they do not assign meanings to any dataset labels.

## Core terms

| Term | Working definition | Annotation / modeling rule |
|---|---|---|
| **Actor** | A moving tracked road user or a configured fixed scene hazard. | Moving actors have temporary track IDs; fixed hazards have scene-config IDs and no motion track. |
| **Pair type** | The typed combination under review: pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object. | All four are MVP categories. Store pair type for every event; only VRU–vehicle has DOT benchmark labels, while the others require separate annotations and evaluation. |
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

## Dataset label mapping — pending annotation-guide review

No dataset labels are mapped to the LiveCross vocabulary yet. Complete this table only after reading the selected dataset’s annotation guide and inspecting examples. Keep the dataset’s original label string unchanged.

| Dataset / version | Raw label or field | Annotation level (frame / event / scenario) | Proposed LiveCross term | Evidence from guide / example | Decision |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | Guide not reviewed | Pending |

### Mapping decision checklist

- Identify the official definition, timestamp semantics, and annotation unit for each raw label.
- Inspect examples from each label, including edge cases and any missing/uncertain tags.
- Confirm whether a label describes crossing behavior, interaction, potential conflict, or an observed collision; do not infer a stronger meaning.
- Record the chosen mapping and excluded labels in the data card before creating training labels.
- If no official label matches conflict/non-conflict, revise the task statement or create a separate, explicitly manual-review annotation set. Do not silently relabel the source data.

## Event record fields

Each reviewed event should retain, when available: `event_id`, `sequence_id`, `source_label`, `livecross_label`, `review_label`, `review_reason`, `pair_type`, `start_time`, `end_time`, `actor_a_track_id`, `actor_b_track_id`, `fixed_hazard_id`, `track_quality`, `conflict_score`, `triggered_factors`, `uncertainty_reason`, and `mapping_version`. A fixed hazard has a scene-config ID rather than a track ID.
