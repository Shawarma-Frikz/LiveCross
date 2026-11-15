# Professor Guide Alignment and Submission Checklist

**Reviewed:** 14 November 2026  
**Sources reviewed:** `Guide Prof.docx` and the separate `Dossier_Etudiant/Projet_Final/Guide_Projet_Computer_Vision.pdf` in the course materials.

## Alignment decision

LiveCross is a clearly defined Computer Vision project: it processes fixed-camera video, detects and tracks road users, estimates temporal interactions, trains an interaction-level SVM, compares it against a transparent rule baseline, and explains candidate events in a live/replay interface. The DOT dataset is real, publicly accessible, and has been downloaded and inspected locally. The project plan includes experiments, metrics, source citations, dependency setup, and raw-data exclusion.

The separate official final-project guide lists three topics and normally expects teams of 3–4. The student reports that the instructor has explicitly approved both LiveCross as a custom topic and solo work. On that basis, the topic and team-size exceptions are treated as approved for this plan. The project is technically aligned with Computer Vision, and its repository setup meets the `Guide Prof.docx` planning requirements. Retain a record of the instructor’s approval in the course registration/project record if requested.

## Guide Prof.docx requirements

| Requirement | Current evidence | Status / remaining action |
|---|---|---|
| Project is a Computer Vision problem | Fixed-camera video detection, tracking, and temporal interaction analysis across five interaction types. | Met technically; the student reports instructor approval for LiveCross as a custom topic and solo work. |
| One group registration; group has no more than four; names, proposed topic, repository URL | Solo-owner section is in README; instructor approval of solo work is reported. | Add the owner’s full name; submit exactly one response through the [group registration form](https://docs.google.com/forms/d/e/1FAIpQLSeqyBKRs7Z6bG1bUUiYG58xgq4pNOn26Rx-gznIW8xMN0dEIA/viewform), including the approved topic and working repository URL. |
| Dedicated, non-empty, understandable GitHub repository | README and project docs explain scope and data. | Met as a planning repository; continue regular meaningful commits. |
| README: context/problem, objectives, solution, approaches/architecture, dataset/source/link, steps, team, technologies, install/run | Expanded project README. | Mostly met. Launch command is clearly marked planned until the app exists; fill in members and finalize versions before submission. |
| Clear code structure | Root README shows planned modules; tracked READMEs exist for data, source, notebooks, models, and results. | Structure prepared; implement actual source modules during development. |
| Dataset source, features, labels, format, organization and preprocessing | `data/README.md` describes source, sample inventory, label granularity, sample findings, and local organization. | Met for initial audit; inspect complete dictionary and full validation coverage before final evaluation. |
| No large datasets in Git; respect use terms | `data/raw/` and `data/processed/` are ignored; `docs/dataset-access.md` records portal rights, citation, sizes, and access. | Met for repository setup; retain citation and verify conditions before publishing derived footage. |
| `requirements.txt` | Python dependency list created. | Initial dependency proposal; pin exact versions after a reproducible environment setup. |
| Bibliography and source attribution | `docs/references.md` lists the dataset, methods, and software. | Started; record exact detector checkpoint, tracker, versions, licenses, and access dates as choices are made. |
| Quality over unnecessary complexity; defined, feasible contribution | One fixed-camera pipeline supports four typed interactions; the benchmark and annotation source are separated by category. | Scope stays bounded to one scene and a shared perception/scoring pipeline. Use category-specific evidence and mark sparse classes exploratory; the five-run sample is feasibility evidence only. |
| Not only a pretrained model/API; real analysis or adaptation | Rule baseline versus trained linear SVM; hard-negative mining; manually reviewed event labels. | Planned, not implemented. Preserve the comparison and report its limits. |
| Experimental metrics and critical analysis | Event precision/recall/F1, false-alert rate, delay, FPS, run-separated evaluation, and failure cases are planned. | Planned; first inspect all 41 public validation runs and create event annotations before freezing final targets. |
| Reproducibility and GitHub access | Dependency file, run/data docs, ignore rules, and repo structure prepared. | Pin dependencies and document model/config after implementation; ensure instructor can access the GitHub repo. |
| Academic integrity and privacy | `docs/references.md`, `docs/risk-register.md`; raw data ignored. | Keep citations, weight licenses, annotation provenance, and contributions current; do not publish identifiable raw footage. |

## Final deliverables and team expectations

The separate course project guide expects:

- A 6–10 page technical report: context/objectives, pipeline and justified methods, experiments/results (including confusion matrix, metrics, speed, and failure analysis), plus a table of individual contributions.
- Documented reproducible code as modular scripts or a clean executed notebook, with `requirements.txt` and a one-command demo documented in README.
- PDF slides for the oral defense.
- A 20-minute defense: 12-minute presentation, 5-minute live demo, 3-minute Q&A, with speaking time shared fairly and each member prepared for individual questions.
- A 3–4 person team and one selected listed topic are the default in the separate project guide; the student reports the instructor approved solo work and a custom LiveCross topic.

These are final-stage deliverables, not artifacts that should be fabricated before experiments exist. Add them as the work matures and report measured results only.

## Next actions before project implementation

1. Add the solo project owner’s full name and submit one registration response with the approved topic and repository URL.
2. Inspect the full DOT validation set or document why the five-run sample is the maximum available; the current sample has only two conflict and three non-conflict run labels and has no event boundaries.
3. Build the supplemental annotation set for vehicle–vehicle, pedestrian–pedestrian, and vehicle–fixed-object events; keep its data source and splits distinct from DOT.
4. Read the full data dictionary and validate whether the 3D ground truth can be projected reliably into the selected camera image.
5. Finalize the detector/tracker, versions, feature definitions, manual-label protocol, split, and per-category acceptance targets before looking at held-out results.
