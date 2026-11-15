# LiveCross — MVP Boundary

**Purpose:** Define a feasible first version for one fixed camera scene. The MVP supports and demonstrates five requested interaction types: pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–configured fixed object, and pedestrian–configured fixed object. The DOT benchmark directly validates only the vulnerable-road-user–vehicle category, so every other category uses suitable separately annotated footage and its own results.

## MVP — required

| Feature | MVP definition | Completion evidence |
|---|---|---|
| Video input | Replay recorded footage through the same inference pipeline used by live demo. | Clips can be selected, played, paused, and reviewed at an event time. |
| Local live input | Process staged interactions from one laptop webcam; keep clip replay as a reliable fallback. | Staged scenes pass through detection, tracking, scoring, and explanation. |
| Camera and scene | One fixed camera view, one configured crossing/conflict polygon, and documented image dimensions. | Scene settings persist locally and render consistently at different display sizes. |
| Road-user detection | Use a documented pretrained YOLO-family detector candidate for people and motor vehicles; include bicycles if supported. Keep weights fixed for MVP. | Record model/version, weight source, license, and class mapping; display class, box, confidence, and timestamp. |
| Tracking | Assign temporary within-clip IDs and maintain motion trails for people and vehicles. | Track breaks, false detections, and ID switches are recorded in the failure review. |
| Fixed hazards | Allow the reviewer to configure fixed-object points/regions such as a tree or light pole. | Each obstacle has a stable scene ID and geometry; it is visibly drawn in the overlay. |
| Typed interaction generation | Generate moving pairs for pedestrian–vehicle, vehicle–vehicle, and pedestrian–pedestrian; compare vehicle paths with configured fixed-object regions. Store the pair type and all actor/object IDs. | Each type is exercised on a recorded or staged clip and creates a reviewable candidate event. |
| Pair-aware rule baseline | Estimate path proximity and time of closest approach for moving pairs; for vehicle–object, test whether the projected vehicle path intersects the configured hazard region. Treat uncalibrated values as image-plane estimates. | Every score is reproducible from stored tracks, geometry, timestamps, and thresholds. |
| Interaction classifier | Train a linear SVM on manually reviewed motion/visibility features with pair type included. Use per-type thresholds or per-type models only if the annotation audit shows the shared model is unsuitable. | Compare to the deterministic rule baseline; record per-type training and evaluation counts. |
| Hard-negative experiment | Review safe false-positive interactions from training clips, then mine selected hard negatives without using held-out clips. Preserve category labels. | Compare before/after mining using the same held-out clips; report false-alert change and recall by type. |
| XAI event | Show the clip/time, pair type, paths or obstacle region, triggered rule factors, SVM feature contributions, and an uncertain/review state. | Every displayed explanation traces to measured features or a named rule. |
| Local event log | Store event ID, interval, pair type, involved tracks/object ID, score, reasons, source, and review status locally. | Selecting an event opens its clip moment and evidence. |
| Responsive interface | Provide a local browser review screen for phone and desktop widths. | Event review is usable at both sizes; inference remains local. |
| Category-specific evaluation | Evaluate each pair type separately. Use DOT labels plus manual event intervals for pedestrian/bicyclist–vehicle; use a separate permission-cleared, manually annotated clip set for the other categories. | Report counts, event precision/recall/F1 when sample size permits, false alerts per annotated minute, delay when labels permit, FPS, and failure examples for each category. Mark sparse categories exploratory. |

## Data and annotation boundary

- **Pedestrian/bicyclist–vehicle:** DOT Stage 1B is the primary benchmark. Its run-level conflict label is not an event label, so event intervals and actor-pair identities must be manually reviewed before event-level scoring.
- **Vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object:** Create a small, documented supplemental annotation set from suitable recorded footage and safe staged clips. Keep its source, consent/permission status, split, and annotation rules distinct from DOT.
- Use complete source clips/runs for train/development/test separation. Do not use held-out clips for threshold tuning or hard-negative mining.
- Support all five categories in the demo even if some category-level metrics must be reported as exploratory. Do not imply that DOT validates unsupported categories.

## Stretch — only after all five MVP paths work

| Feature | Add only when | Boundary |
|---|---|---|
| CNN interaction comparator | Each category has enough event-level labels and the rule/SVM comparison is complete. | Optional scientific comparison; not added just to increase model count. |
| Camera calibration | A defensible calibration procedure and matching scene geometry are available. | Only then report physical distances or TTC units. |
| Automatic fixed-object detection | Configurable geometry and vehicle path scoring are stable. | Adds a new perception task; does not replace manual hazard configuration in MVP. |
| Multi-camera fusion, city mapping, native phone capture | The single-camera MVP is complete and time remains. | Outside the course MVP. |

## Out of scope

- Certified driver/public warnings, traffic-signal control, or emergency dispatch.
- Claims that a crash will occur, or judgments of fault or intent.
- Reliable physical speed, distance, or collision probability without validation.
- Identity recognition, cross-session identity tracking, cloud upload, or long-term storage of raw footage.
- Pooling all categories into one headline score that hides per-type failures.

## Completion gate

The MVP is complete when all five typed paths can produce reviewable events on recorded or staged clips; the rule baseline and linear SVM have been compared on eligible labeled data; hard-negative mining is evaluated without split leakage; event explanations, uncertainty, and local logging work; and the responsive interface handles both clip replay and a staged webcam feed. Category-specific evidence and limitations must be reported separately. Clip replay remains the reliable demonstration path if webcam capture fails.

## Approval and feasibility gates

1. The student reports that the instructor approved LiveCross as a custom topic and approved solo work. Record that decision in the registration/project log if requested.
2. Audit annotation coverage before freezing per-category acceptance targets. The five-run DOT sample is a pipeline-feasibility pilot, not enough by itself for strong claims.
3. If a pair type lacks sufficient independent labeled clips, keep the feature in the working demo and report its metrics as exploratory rather than dropping it or borrowing another category’s labels.
