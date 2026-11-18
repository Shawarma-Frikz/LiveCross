# Professor Guide Alignment and Submission Checklist

**Version:** 2.0 (Refined Scope: 2 Core Interaction Types)
**Reviewed:** 18 November 2026
**Sources reviewed:** `Guide Prof.docx` and the separate `Dossier_Etudiant/Projet_Final/Guide_Projet_Computer_Vision.pdf` in the course materials.

## Alignment decision

LiveCross is specified as a Computer Vision project for fixed-camera video analysis of pedestrian–vehicle and vehicle–vehicle interactions. The planned system includes detection, tracking, temporal interaction analysis, an interpretable baseline, and event explanations. These are planned components, not implemented results. DOT has been downloaded and inspected locally, but its labels are run-level; the current project event annotations are unadjudicated drafts. ROCO is trajectory-only, and Waterloo is excluded from public use pending rights clarification. The project is aligned in topic and planning; event-level benchmark readiness remains incomplete.

The official final-project guide lists three topics and normally expects teams of 3–4. The student reports that the instructor has explicitly approved both LiveCross as a custom topic and solo work. On that basis, the topic and team-size exceptions are treated as approved for this plan. The project is technically aligned with Computer Vision, and its repository setup meets the `Guide Prof.docx` planning requirements. Retain a record of the instructor’s approval in the course registration/project record if requested.

## Guide Prof.docx requirements

| Requirement | Current evidence | Status / remaining action |
|---|---|---|
| Project is a Computer Vision problem | Fixed-camera video detection, tracking, and temporal interaction analysis across two core traffic interaction types (pedestrian–vehicle and vehicle–vehicle). | Met technically; the student reports instructor approval for LiveCross as a custom topic and solo work. |
| One group registration; group has no more than four; names, proposed topic, repository URL | Solo-owner section is in README; instructor approval of solo work is reported. | Add the owner’s full name; submit exactly one response through the [group registration form](https://docs.google.com/forms/d/e/1FAIpQLSeqyBKRs7Z6bG1bUUiYG58xgq4pNOn26Rx-gznIW8xMN0dEIA/viewform), including the approved topic and working repository URL. |
| Dedicated, non-empty, understandable GitHub repository | README and project docs explain scope and data. | Met as a planning repository; continue regular meaningful commits. |
| README: context/problem, objectives, solution, approaches/architecture, dataset/source/link, steps, team, technologies, install/run | Expanded project README. | Mostly met. Launch command is clearly marked planned until the app exists; fill in members and finalize versions before submission. |
| Clear code structure | Root README shows planned modules; tracked READMEs exist for data, source, notebooks, models, and results. | Structure prepared; implement actual source modules during development. |
| Dataset source, features, labels, format, organization and preprocessing | `data/README.md` describes source, sample inventory, label granularity, sample findings, and local organization. | Met for initial audit; 10-run compact validation subset held out in test; candidate expansion datasets audited. |
| No large datasets in Git; respect use terms | `data/raw/` and `data/processed/` are ignored; `docs/dataset-access.md` records portal rights, citation, sizes, and access. | Met for repository setup; retain citation and verify conditions before publishing derived footage. |
| `requirements.txt` | Python dependency list created. | Initial dependency proposal; pin exact versions after a reproducible environment setup. |
| Bibliography and source attribution | `docs/references.md` lists the dataset, methods, and software. | Started; record exact detector checkpoint, tracker, versions, licenses, and access dates as choices are made. |
| Quality over unnecessary complexity; defined, feasible contribution | Two-category fixed-camera project scope and data limitations documented. | Scope is appropriately bounded; event-level data sufficiency remains to be demonstrated. |
| Not only a pretrained model/API; real analysis or adaptation | Rule baseline versus trained linear SVM; hard-negative mining; manually reviewed event labels. | Planned, not implemented. Preserve the comparison and report its limits. |
| Experimental metrics and critical analysis | Proposed event metrics and source-run split are documented. | Not measured. Student event adjudication is pending; test gallery exposure history is unknown and disclosed in the evaluation documentation. |
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

1. Submit one group registration response with the approved topic and repository URL.
2. Complete human student adjudication of candidate event windows on continuous DOT video clips.
3. Finalize the detector/tracker, versions, feature definitions, manual-label protocol, split, and per-category acceptance targets before looking at held-out results.
