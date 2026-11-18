# LiveCross — Event Vocabulary & Mapping

**Version:** 2.1 (two-category scope)
**Status:** Qualitative annotation vocabulary frozen for pilot; numeric detector/scoring thresholds are not yet established.

## 1. Terms

| Term | Meaning in this project |
|---|---|
| **Actor** | A visible moving road user represented by a source or temporary within-sequence ID. Temporary IDs are not official ground truth IDs. |
| **Pair type** | One of `pedestrian_vehicle` or `vehicle_vehicle`. Other pair types are out of scope. |
| **Potential conflict** | A reviewed interaction where observed or cautiously projected motion supports a plausible shared-space conflict under the project protocol. This is a safety-review label, not a collision finding. |
| **Non-conflict interaction** | An observable, relevant actor pair reviewed over the full window where evidence supports that the project conflict condition is absent. Missing visibility is not a negative. |
| **Uncertain** | Evidence is insufficient because of occlusion, timing/identity ambiguity, weak motion evidence, or tracking failure. Do not include in binary training or primary metrics unless later adjudicated. |
| **Excluded** | A window cannot be assessed or is outside the protocol. Exclusion is not a negative label. |
| **Event interval** | The source-time interval supported by continuous review. Store exact source timestamps and frame indices where available; no arbitrary minimum duration is frozen. |
| **Candidate alert** | A system-generated review suggestion. It is not ground truth and must not determine annotation labels. |

Numeric time/distance cutoffs, persistence, alert merging, and matching implementation remain to be specified using training/development evidence before held-out evaluation. Uncalibrated geometry must be reported as image-plane proxy only.

## 2. Source label mappings and limits

### DOT ISC Stage 1B

`Conflict_No_Conflict_Label` is a **run/scenario-level** source field. Preserve it as source metadata. It does not identify event timing, actor identities, or vehicle–vehicle event labels and must not be copied to frame/pair/event records. The two current pedestrian–vehicle table rows are assistant drafts pending student continuous-video review. No vehicle–vehicle video event records exist yet.

### ROCO

ROCO provides source-labeled vehicle conflict **trajectory** windows and vehicle IDs at 2.5 Hz. Preserve the source severity/reason/pair semantics as supplied. ROCO has no RGB video; it can support a separately reported trajectory-only comparator, not LiveCross visual detection/tracking or image-space explanations.

### Waterloo

Local video and track/context files were inventoried, but reuse terms are unresolved. Exclude Waterloo from the public benchmark and deliverables until authoritative permission/terms are recorded. Its route-level geometric intersections are not observed conflict events.

## 3. Annotation record

Use the versioned table schema in `data/annotations/v1/events.csv`, including source, split, category, actor IDs when defensible, source frames/timestamps, status, uncertainty, annotator, annotation version, and review stage. Solo annotation must be identified truthfully; do not imply independent agreement.

## 4. Ground-truth readiness

The present annotation table is a pilot, **not ground truth ready for model training or evaluation**. See [`event-label-set-v1.md`](event-label-set-v1.md), [`manual-annotation-protocol.md`](manual-annotation-protocol.md), and [`phase0-phase1-freeze.md`](phase0-phase1-freeze.md) for review requirements and current status.
