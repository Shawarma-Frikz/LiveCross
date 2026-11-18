# LiveCross — Project Brief

**Status:** Approved for implementation (Scope Refined: 2 Core Interaction Categories)
**Project type:** Explainable computer-vision prototype for road-safety review

## Problem statement

Road-safety teams and civil engineers often review fixed-camera traffic video after a concern or near-miss has been reported. Identifying the exact moments when road users converge on a shared conflict area—and understanding whether their paths pose a collision risk—demands repetitive, time-consuming manual inspection.

LiveCross analyzes fixed-camera intersection video to automatically detect, track, and bring forward reviewable interaction candidates for two primary high-risk traffic categories:
1. **Pedestrian–Vehicle conflicts** (the core vulnerable road user / Vision Zero safety priority).
2. **Vehicle–Vehicle conflicts** (junction turning and crossing collisions).

The project asks: **Can an explainable, course-scale computer vision pipeline reliably detect and explain potential crossing conflicts from fixed-camera video, and can hard-negative mining reduce false alarms while preserving critical event recall?**

## Intended user and use

The primary user is a **campus, municipal, or road-safety reviewer** monitoring a designated crossing or intersection. LiveCross processes recorded video footage to locate, timestamp, and explain candidate conflict events. A live camera feed is supported as a real-time demonstration mode; the core analytical deliverable remains a reviewable event log supported by visual and temporal evidence.

## Scene and input

- **Scene:** One fixed, calibrated or uncalibrated camera view observing an intersection or designated crosswalk conflict zone.
- **Input:** Recorded intersection video streams (offline review mode) and local webcam capture (staged live demo mode).
- **Actors:**
  - *Pedestrians:* Foot-travelers crossing roadway boundaries.
  - *Vehicles:* Passenger cars, vans, trucks, and buses.
- **Core Interaction Scope:**
  - **Category 1 (Pedestrian–Vehicle):** Moving pedestrian and vehicle whose reviewed or predicted trajectories may converge on a marked crosswalk or roadway conflict zone. Numeric timing and proximity cutoffs are not frozen yet.
  - **Category 2 (Vehicle–Vehicle):** Two moving vehicles approaching an intersecting trajectory or junction zone with potentially converging arrival times. Numeric cutoffs are not frozen yet.
- **Explicit Scope Boundary (Non-MVP Extensions):**
  Pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object interactions are explicitly documented as out-of-scope for the core MVP benchmark. Extensive audits of external candidates (JRDB, DoTA, TUMTraf) demonstrated that public datasets for these either present critical domain shifts (moving robot campus corridors, moving dashcams with 94.1% split leakage) or lack true conflict annotations. In accordance with the course guideline (*« Privilégiez la qualité à la complexité »*), the project concentrates exclusively on rigorous evaluation of the two vital vehicle-interaction types.

## Output and explainability

For each flagged event, LiveCross presents an **inspectable event card**:
- Start timestamp, peak risk timestamp, and end timestamp.
- Interacting actor track IDs and class categories.
- Visual overlay showing actor bounding boxes, motion history trails, and the designated conflict polygon.
- Surrogate safety metrics: estimated Time-to-Zone ($TTZ$), Post-Encroachment Time ($PET$) proxy, and minimum spatial distance.
- Plain-language explanation derived directly from decision logic and linear model contributions (e.g. *"Vehicle #3 and Pedestrian #7 predicted to enter crosswalk 0.8s apart; spatial proximity below safety margin"*).
- Explicit uncertainty flag (`uncertain_view`) triggered when occlusion, track fragmentation, or low detection confidence prevents confident assessment.

## Project goals and milestones

1. **Reproducible Pipeline:** Build a modular Python pipeline for video ingestion, object detection, multi-object tracking, and trajectory feature extraction.
2. **Transparent Risk Reasoning:** Implement an interpretable rule-based baseline and train an interaction-level linear SVM classifier on motion features.
3. **Hard-Negative Mining:** Run the signature mining loop on training clips to collect high-risk non-conflict interactions (e.g. staggered crossings, pedestrian walking parallel to vehicle, stopped cars) and demonstrate a measurable reduction in false alarms per video hour.
4. **Explainable AI (XAI):** Show that every alert is supported by verified mathematical factors and decision boundaries, rather than uninterpretable heatmaps.
5. **Interactive Review Dashboard:** Provide an accessible Streamlit web application supporting clip replay, interactive timeline scrubbing, and live alert inspection.

## Non-goals and ethical guardrails

- LiveCross is a **retrospective safety-review prototype**, not an in-vehicle collision avoidance system, traffic signal controller, or automated enforcement tool.
- It does **not** claim to predict unavoidable crashes, assign legal fault, or infer human psychological intent.
- Distances and times derived from uncalibrated 2D video are explicitly designated as **image-plane proxies**; metric units are reported only when validated camera calibration is established.
- Video privacy: raw recordings are stored locally and excluded from version control; no facial recognition or license plate identification is performed.
