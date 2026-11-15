# LiveCross — Project Brief

**Status:** Draft for implementation
**Project type:** Explainable computer-vision prototype for road-safety review

## Problem statement

Road-safety teams often review video after a concern has been reported. Finding moments when people or vehicles converge on a crossing area—or when a road-user path approaches a fixed roadside hazard—can take careful, repeated viewing. LiveCross will analyze fixed-camera video and bring five typed event candidates forward for human review: pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object.

The project asks: **Can a course-sized computer-vision pipeline find and explain several types of potential crossing conflicts, and can hard-negative mining reduce false alerts without hiding failures in less common pair types?**

## Intended user and use

The primary user is a **campus, municipal, or road-safety reviewer** examining a particular crossing or walkway. LiveCross is intended to help that reviewer locate and understand candidate events in recorded footage. A live camera view is a demonstration mode; the core result remains a reviewable event with its source time and visual evidence.

## Scene and input

- **Scene:** One fixed, stable camera view containing a visible crossing or marked conflict zone.
- **Input:** A recorded video clip first, followed by one staged local laptop-webcam feed through the same pipeline.
- **Moving actors:** Pedestrians and motor vehicles; bicycles only if the selected data and detector support them reliably.
- **Fixed hazards:** User-configured scene objects such as trees or light poles. They are static landmarks/regions, not objects expected to move or receive a tracked identity.
- **MVP interaction coverage:** Pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object (for example, an approach to a configured tree or light-pole region). Include bicyclist–vehicle within the VRU–vehicle group when detection and clip annotations support it.
- **Data boundary:** DOT is the benchmark for its documented vulnerable-road-user–vehicle scenarios. The other pair types use a separate, manually annotated clip set and are reported independently; they are not described as DOT-validated.
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
4. Evaluate each pair type separately on source-separated data using event-level precision, recall, F1, false alerts per video duration, detection delay, and processing speed. Mark sparse categories exploratory.
5. Deliver a responsive browser demo with clip replay and a staged local laptop-webcam mode; keep clip replay as a reliable fallback.

The complete feature-by-feature boundary is recorded in [`mvp-scope.md`](mvp-scope.md). The minimum version uses one fixed scene, a pretrained detector, tracking, transparent conflict scoring, a trained linear SVM interaction filter, reviewed hard negatives, a local event log, and an explainable responsive review interface.

## Non-goals and limits

LiveCross will not diagnose intent, determine fault, predict that a crash will occur, issue a certified driver warning, or replace expert review. It will not claim reliable physical distances without calibration or generalize beyond the cameras and conditions evaluated. No real person will be placed in danger for the demonstration.

## Data and approval note

The preferred video source is the **U.S. DOT Intersection Safety Challenge Stage 1B**. Its official description covers conflict/non-conflict scenarios between vulnerable road users (such as pedestrians and bicyclists) and vehicles. Its five-run sample has been inspected, but its labels are run-level; they do not directly supervise event-level pair predictions. LiveCross's event target will therefore be created by human review of permission-cleared video using the documented three-state annotation protocol. The DOT run label remains a separate, coarse source reference. The sample alone is too small for strong final claims. Inspect the public 41-run validation asset before freezing the evaluation set. Vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object require their own suitable reviewed clips. The [dataset decision](dataset-decision.md) records why PIE is not a fallback unless the project changes to pedestrian crossing-intention prediction. Per the student, the instructor approved LiveCross as a custom topic and approved solo work. Operational definitions are in [`event-vocabulary.md`](event-vocabulary.md), with the labeling process in [`manual-annotation-protocol.md`](manual-annotation-protocol.md).

Initial measurable evaluation thresholds and the DOT label-level limitation are recorded in [`acceptance-targets.md`](acceptance-targets.md); confirm sample contents before freezing the final test protocol.

Privacy, misuse, data-handling, and domain-shift risks are tracked in [`risk-register.md`](risk-register.md).
