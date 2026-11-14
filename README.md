# LiveCross

**An explainable computer-vision prototype for reviewing multiple kinds of potential conflicts at a crossing.**

> **Project status:** Scope and planning. The detection pipeline and web application have not been implemented yet.

## What LiveCross is intended to do

LiveCross will analyze video from one fixed crossing and bring potential conflicts between road users and configured obstacles forward for human review. Intended interaction types include pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, and vehicle–fixed-object (such as a tree or light pole). The first version is planned to support recorded clips and a staged local laptop-webcam demo through the same pipeline. Dataset-backed evaluation will be limited to the interaction types actually labeled by the selected data; other types require a separately annotated demonstration set.

The planned system will:

- detect and track pedestrians and motor vehicles; represent fixed hazards as configured scene objects;
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

The preferred benchmark is the U.S. DOT Intersection Safety Challenge Stage 1B. Its official description covers conflict/non-conflict scenarios between vulnerable road users (including pedestrians and bicyclists) and vehicles; it does not establish labels for vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object conflicts. Those additional interaction types need separate, clearly identified manual annotations and must not be reported as DOT-validated results. PIE is a fallback for pedestrian crossing behavior; it does not directly label near-miss events.

The planned tools include OpenCV, PyTorch/torchvision, scikit-learn, and Streamlit. The exact model, package versions, dataset split, and run instructions will be recorded once implementation begins.

## Current development stage

The next work is to validate dataset access and label meanings, then build the video/data pipeline. There is no app launch command or trained LiveCross model yet.
