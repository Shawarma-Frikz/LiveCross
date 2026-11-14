# LiveCross — Project Brief

**Status:** Draft for course-project approval  
**Project type:** Explainable computer-vision prototype for road-safety review

## Problem statement

Road-safety teams often review video after a concern has been reported. Finding the moments when a pedestrian and a vehicle may have approached the same crossing area at nearly the same time can take careful, repeated viewing. LiveCross will analyze a fixed-camera video, identify pedestrian–vehicle interactions that meet a transparent potential-conflict rule, and bring those moments forward for a person to review.

The project asks: **Can a course-sized computer-vision pipeline find and explain candidate pedestrian–vehicle conflicts in a defined crossing scene, while reducing false alerts from safe interactions?**

## Intended user and use

The primary user is a **campus, municipal, or road-safety reviewer** examining a particular crossing or walkway. LiveCross is intended to help that reviewer locate and understand candidate events in recorded footage. A live camera view is a demonstration mode; the core result remains a reviewable event with its source time and visual evidence.

## Scene and input

- **Scene:** One fixed, stable camera view containing a visible crossing or marked conflict zone.
- **Input:** A recorded video clip first, followed by one staged local laptop-webcam feed through the same pipeline.
- **Road users:** Pedestrians and motor vehicles, with bicycles included only if the selected data supports them reliably.
- **Initial conditions:** Begin with a small, documented set of usable sequences. Record frame rate, resolution, lighting, occlusion, camera view, and annotation coverage.

## Output

For each candidate event, LiveCross will show:

- the event time range and the people/vehicle tracks involved;
- the configured crossing/conflict zone and recent motion trails;
- the measured factors that triggered the flag, such as estimated zone-entry timing and path proximity;
- an uncertainty/review state when tracking, visibility, or geometry is insufficient.

Distances and time-to-collision values derived from image coordinates will be labelled **image-plane estimates** unless camera calibration supports physical measurements.

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

The preferred dataset is the **U.S. DOT Intersection Safety Challenge Stage 1B**, subject to confirming video access and annotation semantics. If the usable data only supports pedestrian crossing intention (for example, PIE), the task and claims will be revised to crossing anticipation plus explicitly defined conflict proxies. Dataset choice and the final project topic require confirmation against the instructor’s requirements. The provisional event definitions and pending label-mapping template are in [`event-vocabulary.md`](event-vocabulary.md).

Initial measurable evaluation thresholds and the DOT label-level limitation are recorded in [`acceptance-targets.md`](acceptance-targets.md); confirm sample contents before freezing the final test protocol.
