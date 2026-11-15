# LiveCross

**An explainable computer-vision prototype for reviewing potential conflicts at a fixed road crossing.**

> **Status:** Project proposal and data-feasibility stage. Per the student, the instructor approved LiveCross as a custom topic and approved working alone. The analysis pipeline and web demo are not implemented yet.

## Problem and intended use

Reviewers may need to replay crossing footage repeatedly to find moments when road users or vehicles approach the same crossing area at nearly the same time, or when a road-user path appears to intersect a fixed hazard. LiveCross is planned as a local video-review tool that flags candidate pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object interactions, displays the motion evidence, and lets a human reviewer inspect the event.

It is a **safety-analysis prototype**, not a driver warning or a claim that a collision will occur. DOT labels support only vulnerable-road-user–vehicle evaluation. The other categories stay in the MVP as distinct candidate-detection paths and will use a separately documented, manually annotated clip set; metrics and claims will be reported per category and marked exploratory when sample counts are insufficient.

## Objectives

- Process a recorded clip and a staged local webcam feed through one fixed-camera pipeline.
- Detect and track people, bicycles when supported, and vehicles; represent fixed hazards as configured scene geometry.
- Compare a transparent motion-rule baseline with a trained interaction-level classifier.
- Study whether reviewed hard-negative mining reduces false alerts while preserving conflict recall.
- Explain each candidate using track paths, timing, proximity features, the decision factors, and uncertainty.
- Present and review events in a responsive local web interface.

## Proposed approach

1. **Video preparation:** decode frames, keep the camera’s frame-timestamp CSV aligned, resize consistently, and record the scene and crossing polygon.
2. **Road-user detection:** start with a pretrained YOLO-family detector; compare its classes and license to the dataset and course constraints before locking a checkpoint.
3. **Tracking:** associate detections into temporary within-clip tracks and record track quality and ID switches.
4. **Typed interactions:** compare predicted paths for moving pairs (pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian) and compare vehicle/pedestrian paths with configured fixed-hazard regions. Use pair-specific conflict geometry and retain pair type in every record.
5. **Experiments:** compare a deterministic rule baseline and a linear SVM on manually reviewed interaction windows across the five interaction types. Mine false-positive safe windows only from training clips; keep source clips/runs separated for evaluation and report per-type counts and metrics.
6. **Explainability:** show the video tracks and rule factors; expose the linear SVM’s signed feature contributions for each decision. Keep an explicit uncertain state.
7. **Demo:** review uploaded clips first and add one staged local webcam feed when replay works reliably.

The learned interaction classifier and the pretrained detector have different jobs. The pretrained detector is not the project’s sole contribution: the team will implement and evaluate the motion features, event logic, hard-negative mining, and explanations. A CNN risk comparator is optional and only considered if annotation volume and time justify it.

## Dataset

**Primary benchmark:** [U.S. DOT Intersection Safety Challenge Stage 1B Validation Data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4).

- The official five-run validation sample is downloaded locally (3,540,625,371 bytes) and excluded from Git.
- It contains visual-camera MP4s and per-frame timestamp CSVs; a selected Run 1003 Visual Camera 7 clip was opened and decoded successfully at 1280×720.
- The sample’s validation labels are conflict/no-conflict **per run**, not event intervals. The five-run sample has two conflict runs and three non-conflict runs, so it is for pipeline feasibility, not a strong final evaluation by itself.
- The full validation dataset is listed as 41 runs (about 30 GB). Inspect its label balance before deciding the final evaluation set. The 1,104-run training set is unlabeled and about 1 TB; it is not needed to start this prototype.
- DOT conflict labels cover vulnerable-road-user/vehicle scenarios only. The other interaction types need separate video annotations and evaluation; never present those results as DOT-validated.

See [data/README.md](data/README.md) for download and local organization instructions and [dataset access notes](docs/dataset-access.md) for the inspected sample, terms, and citation.
The sample’s current source, label, and limitation summary is in the [data card](docs/data-card.md).
The [dataset expansion plan](docs/dataset-expansion-plan.md) records what evidence is still needed for the five interaction types and how each data source will be used.
The [dataset/fallback decision](docs/dataset-decision.md) explains why DOT remains the video source, why PIE is not a label-compatible fallback for this scope, and which manual labels are required before event-level training.

Supplementary data have their own [terms/schema/label audit](docs/supplemental-data-audit.md). Recreate the local inventories for TGSIM, ROCO, and a representative Waterloo database with:

```powershell
python scripts/audit_supplemental_data.py
```

The audit writes `results/audits/supplemental-dataset-audit.json`. It does not train a model or treat trajectory-derived candidates as source conflict ground truth. Waterloo redistribution terms remain unresolved; keep those media files out of Git.

## Traceable sample audit

Recreate the machine-checkable inventory, frame decode/timestamp comparison, run-label counts, and selected-run GT summary with:

```powershell
python scripts/audit_sample_data.py
```

The script reads existing files under the Git-ignored `data/raw/` directory and writes `results/audits/dot-sample-audit.json`. It downloads nothing. Human label interpretation and the camera-projection decision remain documented separately in `docs/event-vocabulary.md` and `docs/projection-audit.md`.

To download the planned public datasets into the ignored `data/raw/` folder, run:

```powershell
python scripts/fetch_project_data.py
```

The fetch script downloads the 41-run DOT validation archive, both public DOT training-sample archives, the camera-calibration archive, and the FHWA TGSIM Foggy Bottom trajectory CSV. Ensure at least 60 GB is free for the downloads and about 100 GB if you plan to extract them too. The approximately 1 TB DOT training archive is unlabeled and is not part of the required download.

## Planned milestones

1. Keep the reported instructor approval of LiveCross and solo work in the course registration/project record if requested.
2. Audit the sample’s data dictionary, class coverage, timestamps, and labels; decide whether full validation is needed. Re-run `scripts/audit_sample_data.py` to reproduce the inventory and raw counts.
3. Build a reproducible video reader, scene configuration, detection, and tracking pipeline.
4. Define and manually review interaction windows for all five interaction types; freeze source-clip/run-separated train/development/test splits.
5. Implement rule scoring, interaction features, the linear SVM, and training-only hard-negative mining.
6. Add explanations, uncertainty, event log, and responsive desktop/phone review screens.
7. Evaluate, analyze failure cases, rehearse the live demo, and prepare the report and slides.

## Technologies

Python 3.10+, OpenCV, NumPy, Pandas, Matplotlib, PyTorch/torchvision, scikit-learn, Ultralytics (candidate YOLO implementation), and Streamlit. Versions and model weights must be recorded after environment setup and license review.

## Fit with the Computer Vision module

The planned work applies video/image representation and preprocessing (OpenCV/NumPy), classical feature engineering and SVM classification, and pretrained YOLO object detection. The main assessed contribution is the run-separated rule-versus-SVM experiment and hard-negative-mining ablation, not simply calling a pretrained detector. A custom CNN is optional and will be attempted only if labels and time support a fair experiment.

## Repository structure

```text
LiveCross/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── README.md
├── notebooks/
│   └── README.md
├── src/
│   └── README.md
├── models/
│   └── README.md
├── results/
│   ├── README.md
│   └── audits/
│       ├── dot-sample-audit.json
│       └── supplemental-dataset-audit.json
└── docs/
    ├── references.md
    ├── professor-guide-alignment.md
    └── ...
```

## Setup and planned launch

The app entry point will be added during implementation. These are the planned local commands; the launch command is not usable until `src/app.py` exists.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run src/app.py
```

## Project owner

Solo project, approved by the instructor according to the student. Add the owner’s full name and technical responsibilities to the registration form and retain a record of the solo-work approval if requested.

| Owner | Responsibility |
|---|---|
| Full name to be entered | Data, perception, interaction modeling, hard-negative experiment, explainability, interface, evaluation, and report |

## GitHub repository

Repository remote: [github.com/Shawarma-Frikz/LiveCross](https://github.com/Shawarma-Frikz/LiveCross). Confirm the repository is public during evaluation or explicitly grant the instructor access if it is private.

## Current limitations

- The five-run sample is too small for strong performance claims and has only run-level conflict labels.
- Event-level reference intervals must be annotated for every evaluated pair type.
- All five interaction types are in the MVP; the four non-VRU–vehicle types require separate, suitable annotations and category-specific evaluation. Treat results as exploratory if a category has too few examples.
- No model is trained, and no UI or launch command is implemented yet.

## Documentation

- [Project brief](docs/project-brief.md)
- [MVP boundary](docs/mvp-scope.md)
- [Event vocabulary](docs/event-vocabulary.md)
- [Manual annotation protocol](docs/manual-annotation-protocol.md)
- [Acceptance targets](docs/acceptance-targets.md)
- [Dataset access and terms](docs/dataset-access.md)
- [Dataset and fallback decision](docs/dataset-decision.md)
- [DOT data card](docs/data-card.md)
- [Supplemental dataset audit](docs/supplemental-data-audit.md)
- [Professor-guide alignment and submission checklist](docs/professor-guide-alignment.md)
- [Risk and ethics register](docs/risk-register.md)
- [References](docs/references.md)
