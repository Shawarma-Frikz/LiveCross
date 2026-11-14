# LiveCross — MVP Boundary

**Purpose:** Freeze what the first course-ready version will include, what can be added only after it works, and what the project will not attempt. This scope is for one fixed camera view and one crossing scene. The product concept supports several pair types, but evaluation claims must follow annotation coverage.

## MVP — required for the first complete demo

| Feature | MVP definition | Completion evidence |
|---|---|---|
| Video input | Replay an annotated/recorded clip through the same inference pipeline used by the demo. | A clip can be selected, played, paused, and reviewed at a flagged time. |
| Local live input | Process a staged interaction from one laptop webcam. Keep clip replay as a fallback for presentation day. | A staged scene flows through detection, tracking, scoring, and explanation without retraining. |
| Camera/scene scope | One fixed camera and one manually configured crossing/conflict polygon. | Polygon and camera settings persist in a local config file. |
| Road-user detection | Detect people and motor vehicles with a documented pretrained CNN detector; keep the model fixed for the MVP. | The overlay and saved detections show class, box, confidence, and frame/time. |
| Configured fixed hazards | Let the reviewer mark fixed obstacle regions/points (for example, a tree or light pole) on the scene image. | Saved scene config contains each obstacle ID, type, and geometry; automatic recognition is unnecessary for MVP. |
| Tracking | Assign temporary track IDs and maintain short motion trails. | Pedestrian and vehicle tracks remain usable across representative event clips; ID switches are recorded as a failure mode. |
| Multi-type interaction candidates | Generate pair windows for pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, and vehicle–configured-fixed-hazard. | Each event records its pair type. DOT-backed evaluation is limited to its labeled VRU–vehicle scenarios; other types use a separate manual set and remain exploratory if data are insufficient. |
| Conflict scoring | Use a transparent baseline based on predicted zone-entry timing, path proximity, and track quality. Treat image-coordinate values as proxies; fixed hazards use approach/path intersection with configured geometry. | A saved event can be recomputed from its tracks, obstacle geometry, and thresholds. |
| Hard-negative experiment | Train a linear SVM on interaction-level motion/visibility features; mine and review false-positive safe interactions from training sequences only. Keep pair type explicit. | Report the same held-out comparison before and after mining, with per-type counts and no mixing unsupported labels into the DOT benchmark. |
| Explainable event | Show the tracks, conflict zone, event time, triggered factors, and an uncertainty/review state. | A reviewer can trace every displayed reason to a stored measurement or rule. |
| Event log | Store event ID, times, involved tracks, score/state, explanation fields, source, and review status locally. | Selecting a log row reopens the corresponding video moment and explanation. |
| Responsive web interface | Provide a browser review screen that reflows for laptop and phone widths; inference runs locally for the course demo. | Core event review works without clipped content at desktop and narrow-phone widths. |
| Course evaluation | Evaluate sequence-separated data using event precision/recall/F1, false alerts per video duration, delay/lead time when labels allow, FPS, and hard-negative ablation. | Final metrics include sample counts, split policy, runtime hardware, and failure examples. |

## Stretch — only after every MVP row works

| Feature | Add only when | Boundary |
|---|---|---|
| Transfer-learning CNN risk comparator | The selected dataset has enough valid labeled event windows and the baseline is complete. | Compare against the motion-feature SVM; do not let it replace event-level evaluation. |
| HOG + SVM crop comparator | There is time for a focused classical-method comparison. | Optional experiment; not required for the live pipeline. |
| Bicycle detection | Dataset labels and detector quality support it. | Add bicycles as an extra road-user class; do not block pedestrian/vehicle MVP. |
| Broader labeled evaluation | A permission-cleared annotation set has enough examples for each additional pair type. | Report metrics separately; never transfer DOT VRU–vehicle labels to vehicle–vehicle, pedestrian–pedestrian, or fixed-hazard pairs. |
| Camera calibration | A defensible calibration procedure and suitable scene geometry are available. | Then, and only then, evaluate physical distance/TTC units. |
| Mobile-browser camera capture | The responsive review UI and laptop webcam mode are stable. | Phone support for reviewing events is MVP; using a phone as a live capture device is stretch. |
| Additional lighting/view conditions | Data is available and the single-scene pipeline is measured. | Treat each condition as a separate generalization experiment. |
| Optional clip export/privacy blur | The data terms permit derived media and time remains. | Keep originals local; redact faces/plates before sharing any demo clip. |

## Out of scope for this project

| Excluded feature | Why it is excluded |
|---|---|
| Multi-camera fusion or camera handoff | Expands calibration, synchronization, and tracking beyond the single-scene course scope. |
| GPS mapping, city-wide hotspot maps, or persistent infrastructure analytics | Requires georeferencing and a broader deployment/data pipeline. |
| Native iOS/Android packaging | The deliverable is a responsive browser prototype. |
| Automatic driver alerts, traffic-signal control, or emergency dispatch | LiveCross is a review aid, not a certified safety-control system. |
| Claims that a crash will happen, or judgments of fault or pedestrian intent | Video-derived proxies do not establish certainty, intent, or responsibility. |
| Reliable physical speed, distance, or TTC without calibration | Image-plane measurements do not have physical units. |
| Cloud upload, face recognition, identity tracking, or long-term storage of raw footage | Not needed for the course prototype and would add privacy and security obligations. |
| Production deployment or claims of preventing collisions | Requires prospective, independent safety validation beyond this project. |

## MVP completion gate

The MVP is complete when one fixed-scene clip and one staged laptop-webcam interaction can pass through the same pipeline; the interface records and explains candidate events; the hard-negative experiment is compared on held-out sequences; the responsive review works on desktop and phone widths; and the report states the measured limits. If webcam capture fails, clip replay remains the required reliable demonstration path and the failure is documented.

## Scope-change rule

Do not add stretch work until the MVP completion gate is met. If data access, labels, or compute force a change, update the brief and record which feature moved category and why before changing the implementation plan.
