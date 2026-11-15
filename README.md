# LiveCross

**An explainable computer-vision prototype for reviewing potential conflicts at a fixed road crossing.**

> **Status:** Project proposal and data-feasibility stage. Per the student, the instructor approved LiveCross as a custom topic and approved working alone. The analysis pipeline and web demo are not implemented yet.

## Problem and intended use

Reviewers may need to replay crossing footage repeatedly to find moments when road users or vehicles approach the same crossing area at nearly the same time, or when a road-user path appears to intersect a fixed hazard. LiveCross is planned as a local video-review tool that flags candidate pedestrian–vehicle, vehicle–vehicle, pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object interactions, displays the motion evidence, and lets a human reviewer inspect the event.

It is a **safety-analysis prototype**, not a driver warning or a claim that a collision will occur. DOT's native labels support only run-level reporting for vulnerable-road-user–vehicle scenarios; they are not event-level labels. The other categories stay in the MVP as distinct candidate-detection paths and will use a separately documented, manually annotated clip set; metrics and claims will be reported per category and marked exploratory when sample counts are insufficient.

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

The learned interaction classifier and the pretrained detector have different jobs. The pretrained detector is not the project’s sole contribution: the project will implement and evaluate the motion features, event logic, hard-negative mining, and explanations. A CNN risk comparator is optional and only considered if annotation volume and time justify it.

## Dataset

**Primary benchmark:** [U.S. DOT Intersection Safety Challenge Stage 1B Validation Data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4).

- The official five-run validation sample is downloaded locally (3,540,625,371 bytes) and excluded from Git.
- It contains visual-camera MP4s and per-frame timestamp CSVs; a selected Run 1003 Visual Camera 7 clip was opened and decoded successfully at 1280×720.
- The sample’s validation labels are conflict/no-conflict **per run**, not event intervals. The five-run sample has two conflict runs and three non-conflict runs, so it is for pipeline feasibility, not a strong final evaluation by itself.
- The downloaded full validation archive contains 41 runs (28,642,566,098 bytes; about 26.7 GiB) and is reserved as LiveCross's held-out test partition. Its source labels are 12 conflict and 29 no-conflict runs, at run level only. The two public unlabeled training samples contain 20 additional runs, split into 16 train and 4 development runs.
- The split is recorded once per complete source run in `data/manifests/splits.csv`, using seed 42 for the training/development assignments. Class stratification is impossible for the unlabeled training samples; all compact-subset runs remain in test. The DOT source labels are known run-level labels and must not be used to tune event-level predictions.
- DOT conflict labels cover vulnerable-road-user/vehicle scenarios only. The other interaction types need separate video annotations and evaluation; never present those results as DOT-validated.

See [data/README.md](data/README.md) for download and local organization instructions and [dataset access notes](docs/dataset-access.md) for the inspected sample, terms, and citation.
The current source inventory, label boundaries, split policy, privacy handling, and data limitations are summarized in the [data card](docs/data-card.md).
The [dataset expansion plan](docs/dataset-expansion-plan.md) records what evidence is still needed for the five interaction types and how each data source will be used.
The [dataset-alignment decision](docs/dataset-decision.md) explains why DOT remains the video source, why PIE does not match this project's conflict-event target, and the manual annotation route required before event-level training.
The [event-label pilot](docs/event-label-set-v1.md) includes a versioned draft table, uncertainty/exclusion records, a reproducible summary, and test-excluded train/development review sheets. It is **not yet project ground truth**: assistant first-pass labels require student frame-level adjudication; all five categories remain exploratory and no test event labels are included.
The compact 10-run validation candidate pool is documented in [compact-subset-selection.md](docs/compact-subset-selection.md), with a reproducible run/camera/duration manifest. Whole-run assignments are recorded in [splits.csv](data/manifests/splits.csv) and can be regenerated with `python scripts/create_sequence_split.py`.
Generate the timestamped, local inspection gallery across all three splits with `python scripts/build_inspection_gallery.py`; see [inspection-gallery.md](docs/inspection-gallery.md) for the label-scope limits and output location.

Supplementary data have their own [terms/schema/label audit](docs/supplemental-data-audit.md). Recreate the local inventories for TGSIM, ROCO, and a representative Waterloo database with:

```powershell
python scripts/audit_supplemental_data.py
```

The audit writes `results/audits/supplemental-dataset-audit.json`. It does not train a model or treat trajectory-derived candidates as source conflict ground truth. Waterloo redistribution terms remain unresolved; keep those media files out of Git.

Rebuild the selected DOT run/camera inventory and timestamp-duration manifest (requires the local `data/raw/validation-full.zip`):

```powershell
python scripts/build_compact_subset_manifest.py
```

This verifies the selected videos and timestamp rows and writes `data/manifests/compact-subset.csv` plus `results/audits/compact-subset-audit.json`. It does not create event labels. Regenerate the run-level split separately with `python scripts/create_sequence_split.py`.

To rebuild the test-excluded training and development annotation contact sheets, run `python scripts/build_annotation_review_pack.py --splits train validation`; to refresh split/category counts after an annotation-table change, run `python scripts/summarize_event_annotations.py`. See [`docs/event-label-set-v1.md`](docs/event-label-set-v1.md). Contact sheets are candidate-finding aids; ground-truth labels require continuous-video student review. The review-pack script rejects test runs; no test event labels are in the current table.

To regenerate the subset and split metadata in order, run `python scripts/build_compact_subset_manifest.py`, `python scripts/create_sequence_split.py`, then `python scripts/build_compact_subset_manifest.py` again so the subset manifest records its test assignment.

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

The fetch script downloads the 41-run DOT validation archive, both public DOT training-sample archives, the camera-calibration archive, and the FHWA TGSIM Foggy Bottom trajectory CSV. Ensure at least 60 GB is free for the downloads. Full-archive extraction is not required: the selected 10-run RGB subset uses about 328.4 MiB of video plus small timestamp CSVs and can be extracted with `python scripts/extract_compact_subset.py`. The approximately 1 TB DOT training archive is unlabeled and is not part of the required download.

## Planned milestones

1. Keep the reported instructor approval of LiveCross and solo work in the course registration/project record if requested.
2. Audit the DOT sample, full validation set, label semantics, and supplementary data; select the compact pool and freeze the whole-run split. Re-run the audit and split scripts to reproduce these records.
3. Build a reproducible video reader, scene configuration, detection, and tracking pipeline.
4. Define and manually review interaction windows for all five interaction types using the frozen source-run split; keep event annotations and model results out of the test partition until final evaluation. The source-run split is already recorded in `data/manifests/splits.csv`.
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
│   ├── README.md
│   └── manifests/
│       ├── compact-subset.csv
│       └── splits.csv
├── notebooks/
│   └── README.md
├── scripts/
│   ├── audit_sample_data.py
│   ├── audit_supplemental_data.py
│   ├── build_compact_subset_manifest.py
│   ├── create_sequence_split.py
│   ├── extract_compact_subset.py
│   ├── fetch_project_data.py
│   └── build_inspection_gallery.py
├── src/
│   └── README.md
├── models/
│   └── README.md
├── results/
│   ├── README.md
│   └── audits/
│       ├── dot-sample-audit.json
│       ├── supplemental-dataset-audit.json
│       ├── compact-subset-audit.json
│       └── sequence-split-audit.json
└── docs/
    ├── references.md
    ├── professor-guide-alignment.md
    ├── dataset-decision.md
    ├── compact-subset-selection.md
    ├── inspection-gallery.md
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
- The local inspection gallery samples every source run, but its frames are contextual samples, not event annotations; difficult/uncertain event examples remain unavailable until manual labeling.
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
- [Dataset-alignment decision](docs/dataset-decision.md)
- [Compact subset selection](docs/compact-subset-selection.md)
- [DOT data card](docs/data-card.md)
- [Supplemental dataset audit](docs/supplemental-data-audit.md)
- [Professor-guide alignment and submission checklist](docs/professor-guide-alignment.md)
- [Risk and ethics register](docs/risk-register.md)
- [References](docs/references.md)
