# LiveCross — Project Brief

**Status:** Draft for course-project approval  
**Project type:** Explainable computer-vision prototype for road-safety review

## Problem statement

Road-safety teams often review video after a concern has been reported. Finding moments when two moving road users—or a vehicle and a fixed roadside obstacle—may have approached the same space at nearly the same time can take careful, repeated viewing. LiveCross will analyze a fixed-camera video and bring candidate interactions forward for human review. Intended pair types are pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, and vehicle–configured fixed object (for example, a tree or light pole).

The project asks: **Can a course-sized computer-vision pipeline find and explain candidate conflicts across several actor-pair types in a defined crossing scene, while reducing false alerts from safe interactions?**

## Intended user and use

The primary user is a **campus, municipal, or road-safety reviewer** examining a particular crossing or walkway. LiveCross is intended to help that reviewer locate and understand candidate events in recorded footage. A live camera view is a demonstration mode; the core result remains a reviewable event with its source time and visual evidence.

## Scene and input

- **Scene:** One fixed, stable camera view containing a visible crossing or marked conflict zone.
- **Input:** A recorded video clip first, followed by one staged local laptop-webcam feed through the same pipeline.
- **Moving actors:** Pedestrians and motor vehicles; bicycles only if the selected data and detector support them reliably.
- **Fixed hazards:** User-configured scene objects such as trees or light poles. They are static landmarks/regions, not objects expected to move or receive a tracked identity.
- **Interaction coverage:** Plan for pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, and vehicle–fixed-object candidates. Report each category separately and mark unsupported or unannotated categories as exploratory.
- **Initial conditions:** Begin with a small, documented set of usable sequences. Record frame rate, resolution, lighting, occlusion, camera view, and annotation coverage.

## Output

For each candidate event, LiveCross will show:

- the event time range, pair type, and involved track IDs or configured fixed-object ID;
- the configured crossing/conflict zone and recent motion trails;
- the measured factors that triggered the flag, such as estimated zone-entry timing and path proximity;
- an uncertainty/review state when tracking, visibility, or geometry is insufficient.

Distances and time-to-collision values derived from image coordinates will be labelled **image-plane estimates** unless camera calibration supports physical measurements. A candidate is a review flag, not a confirmed collision or a live public warning.

## Project goals

1. Build a reproducible video pipeline for detection, tracking, interaction features, and event visualization.
2. Compare a transparent rule baseline with a learned conflict filter; use verified hard negatives from training sequences to study false-alert reduction.
3. Explain each flag with the measurements and conditions that contributed to it.
4. Evaluate on sequence-separated data using event-level precision, recall, F1, false alerts per video duration, detection delay, and processing speed.
5. Deliver a responsive browser demo with clip replay and a staged local laptop-webcam mode; keep clip replay as a reliable fallback.

The complete feature-by-feature boundary is recorded in [`mvp-scope.md`](mvp-scope.md). The minimum version uses one fixed scene, a pretrained CNN detector, tracking, transparent conflict scoring, reviewed hard negatives, a local event log, and an explainable responsive review interface.

## Non-goals and limits

LiveCross will not diagnose intent, determine fault, predict that a crash will occur, issue a certified driver warning, or replace expert review. It will not claim reliable physical distances without calibration or generalize beyond the cameras and conditions evaluated. No real person will be placed in danger for the demonstration.

## Data and approval note

The preferred benchmark is the **U.S. DOT Intersection Safety Challenge Stage 1B**. Its official description covers conflict/non-conflict scenarios between vulnerable road users (such as pedestrians and bicyclists) and vehicles. It does not establish labels for vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object conflicts. Those categories require a separate manually annotated set or must remain exploratory; do not present them as validated by DOT labels. If DOT is unusable and PIE is selected, revise claims to its supported task plus explicitly defined conflict proxies. Confirm the final topic against instructor requirements. The provisional event definitions and pending label-mapping template are in [`event-vocabulary.md`](event-vocabulary.md).

Initial measurable evaluation thresholds and the DOT label-level limitation are recorded in [`acceptance-targets.md`](acceptance-targets.md); confirm sample contents before freezing the final test protocol.

Privacy, misuse, data-handling, and domain-shift risks are tracked in [`risk-register.md`](risk-register.md).
