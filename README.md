# LiveCross

**An explainable computer-vision prototype for reviewing potential road conflicts at a fixed crossing.**

> **Status (18 November 2026):** Phase 0 specifications are documented and scope-frozen. Phase 1 data inventory and audits are substantially documented, but **Phase 1 is not complete**: event ground truth is still an unadjudicated pilot, and vehicle–vehicle video events have not been labeled. See [`docs/phase0-phase1-freeze.md`](docs/phase0-phase1-freeze.md) for itemized status and remaining actions. Do not treat the current annotations as training or evaluation ground truth.

---

## 1. Problem and Scope

Road-safety teams and civil reviewers frequently examine recorded traffic video to identify high-risk moments when moving actors converge on a shared roadway zone. LiveCross is an inspectable computer vision tool designed to process fixed-camera intersection video and flag reviewable candidate events across two core high-risk interaction types:

1. **Pedestrian–Vehicle Conflicts** (Vision Zero vulnerable road user safety).
2. **Vehicle–Vehicle Conflicts** (Intersection turning and crossing encounters).

*Scope boundary:* Pedestrian–pedestrian and fixed-object interactions are out of scope for this MVP. The intended categories are pedestrian–vehicle and vehicle–vehicle. Their event-level evidence is still being assembled and reviewed; the project does not yet claim validated conflict detection or end-to-end evaluation.

---

## 2. Core Methodological Pipeline

```
[Fixed Camera Video]
        │
        ▼
[1. Perception]  ─── Pretrained YOLO (Pedestrians, Cars, Trucks, Buses, Bicycles)
        │
        ▼
[2. Tracking]    ─── Multi-Object Tracking (IoU/ByteTrack association + trajectory history)
        │
        ▼
[3. Geometry]    ─── User-configured Conflict Polygon (Crosswalk / Junction Zone)
        │
        ▼
[4. Risk Model]  ─── Transparent Baseline Rule + Trained Linear SVM:
                     • Time-to-Zone (TTZ) delta calculation
                     • Spatial proximity & trajectory convergence vectors
                     • Signature Hard-Negative Mining loop on training sequences
        │
        ▼
[5. Explainable] ─── Inspectable Event Cards (Plain-language reasons, XAI signed weights)
        │
        ▼
[6. Dashboard]   ─── Streamlit Review Dashboard (Replay scrubber, alert timeline, risk badge)
```

---

## 3. Dataset sources and their current roles

The project repository records the following dataset roles. Raw-data paths are local and Git-ignored; availability on another checkout depends on separate downloads:

| Interaction Category | Primary Dataset | Modality | Local Storage | Ground Truth Reference |
|---|---|---|---|---|
| **Pedestrian–Vehicle video** | **U.S. DOT ISC Stage 1B** | Fixed roadside camera, VisualCamera7 | 10 complete runs selected for review; source archives hold train/dev and test partitions | DOT labels are run/scenario-level only. Event windows in `data/annotations/v1/events.csv` remain drafts pending continuous-video adjudication. |
| **Vehicle–Vehicle video** | **DOT training-sample footage, pending manual annotation** | Fixed intersection video | Training/development runs are available locally | No DOT vehicle–vehicle conflict event labels exist yet; annotate from continuous train/dev video before supervised use. |
| **Vehicle–Vehicle trajectory comparator** | **ROCO** | Vehicle trajectories, 2.5 Hz; no RGB video | `data/raw/roco/ROCO.zip` | 101 source-labeled events support a separate trajectory-only analysis, not video detection/tracking evaluation. |
| **Exploratory perception reference** | **TUMTraf-Accid3nD** | Roadside highway images and labels | Small verified sample | Perception reference only; highway accident domain is not LiveCross intersection conflict ground truth. |

Waterloo footage is excluded from the public project benchmark because reuse terms remain unresolved. Do not use or redistribute it unless written permission or authoritative terms are obtained.

---

## 4. Phase 0 & Phase 1 Completion Record

- [x] **00.1–00.5 Project Definition:** Target user, fixed crossing scene, 2 core interaction types, event vocabulary, draft acceptance targets, and risk boundaries are recorded in the linked project documents.
- [x] **00.2 MVP Boundary:** Core matrix, inputs, outputs, and dataset boundaries frozen in [`docs/mvp-scope.md`](docs/mvp-scope.md).
- [x] **00.3 Event Vocabulary:** Operational definitions, three-state review labels, and source label mappings frozen in [`docs/event-vocabulary.md`](docs/event-vocabulary.md).
- [x] **00.4 Acceptance Targets:** Proposed targets and measurement rules are recorded in [`docs/acceptance-targets.md`](docs/acceptance-targets.md); they are not measured or claimed achieved.
- [x] **00.5 Risk Register:** Privacy, surrogate safety limits, domain shift, and non-warning guardrails recorded in [`docs/risk-register.md`](docs/risk-register.md).
- [x] **01.1–01.3 Dataset Gate & Audit:** DOT Stage 1B validation sample, full archive, and timing CSV irregularities audited and documented in [`docs/dataset-access.md`](docs/dataset-access.md) and [`docs/projection-audit.md`](docs/projection-audit.md).
- [x] **01.1–01.9 Data review artifacts:** Source/access, inventory, split, subset, gallery, data card, and supplementary audits are documented. Some candidate footage remains excluded or exploratory, as recorded in the audits.
- [ ] **01.10 Event labels:** Incomplete. Current labels are unadjudicated drafts; there are zero vehicle–vehicle event rows. Review [`docs/phase0-phase1-freeze.md`](docs/phase0-phase1-freeze.md) for exact student actions.

---

## 5. Repository Structure

```text
LiveCross/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md
│   ├── manifests/
│   │   ├── compact-subset.csv
│   │   └── splits.csv
│   └── annotations/
│       └── v1/events.csv
├── docs/
│   ├── project-brief.md
│   ├── mvp-scope.md
│   ├── event-vocabulary.md
│   ├── acceptance-targets.md
│   ├── data-card.md
│   ├── dataset-decision.md
│   ├── candidate-dataset-audit.md
│   └── risk-register.md
├── scripts/
│   ├── audit_sample_data.py
│   ├── audit_supplemental_data.py
│   ├── audit_candidate_datasets.py
│   ├── create_sequence_split.py
│   └── build_compact_subset_manifest.py
├── results/
│   └── audits/
│       ├── dot-sample-audit.json
│       ├── supplemental-dataset-audit.json
│       ├── candidate-dataset-audit.json
│       └── sequence-split-audit.json
├── src/
│   ├── detector.py          # YOLO perception
│   ├── tracker.py           # Multi-object association
│   ├── geometry.py          # Conflict zones & path features
│   ├── risk.py              # Rule baseline + linear SVM
│   ├── mining.py            # Hard-negative mining loop
│   ├── explain.py           # XAI factor attribution
│   └── app.py               # Streamlit review UI
└── models/
    └── README.md
```

---

## 6. Setup and Usage

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run dataset audit scripts
python scripts/audit_sample_data.py
python scripts/audit_supplemental_data.py
python scripts/audit_candidate_datasets.py

# 3. Launch review application (Phase 8 deliverable)
streamlit run src/app.py
```
