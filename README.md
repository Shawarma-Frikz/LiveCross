# LiveCross

**An explainable computer-vision prototype for reviewing pedestrian–vehicle interactions at a crossing.**

> **Project status:** Scope and planning. The detection pipeline and web application have not been implemented yet.

## What LiveCross is intended to do

LiveCross will analyze video from one fixed crossing and bring potentially conflicting pedestrian–vehicle interactions forward for human review. The first version is planned to support both recorded clips and a staged local laptop-webcam demo through the same pipeline.

The planned system will:

- detect pedestrians and motor vehicles, then track them across frames;
- compare their motion with a manually defined crossing/conflict zone;
- flag candidate events using transparent conflict-scoring logic;
- explain each flag with track paths, timing, proximity factors, and uncertainty;
- record events locally in a responsive browser interface;
- study whether hard-negative mining reduces false alerts from safe interactions.

LiveCross is a course/research prototype for **safety analysis and event review**. It is not a certified warning system and will not determine intent, fault, or that a crash will occur.

## Project documents

- [Project brief](docs/project-brief.md) — problem, intended user, scene, input/output, goals, and limitations.
- [MVP boundary](docs/mvp-scope.md) — features assigned to MVP, stretch, or out of scope.
- [Event vocabulary](docs/event-vocabulary.md) — provisional operational definitions and the dataset-label mapping template.
- [Acceptance targets](docs/acceptance-targets.md) — initial thresholds, evaluation protocol, and dataset-dependent caveats.
- [Risk and ethics register](docs/risk-register.md) — project risks, impact, mitigation, role owners, and use guardrails.

## Planned data and methods

The preferred dataset is the U.S. DOT Intersection Safety Challenge Stage 1B, pending confirmation that its video and annotations support the project’s conflict task. PIE is a fallback for pedestrian crossing behavior; it does not directly label near-miss events, so the task and claims would need to change if PIE is used.

The planned tools include OpenCV, PyTorch/torchvision, scikit-learn, and Streamlit. The exact model, package versions, dataset split, and run instructions will be recorded once implementation begins.

## Current development stage

The next work is to validate dataset access and label meanings, then build the video/data pipeline. There is no app launch command or trained LiveCross model yet.
