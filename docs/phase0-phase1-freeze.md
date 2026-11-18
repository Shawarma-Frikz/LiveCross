# LiveCross — Phase 0 and Phase 1 Status Record

**Reviewed:** 18 November 2026
**Frozen scope:** Pedestrian–vehicle and vehicle–vehicle only
**Overall verdict:** Phase 0 is scope-frozen. Phase 1 is **closed on the documented exploratory fallback**: local archives are inventoried and extracted, the split and annotation provenance are recorded, both categories below their pilot minimums are explicitly designated exploratory, and no held-out event labels or model predictions were used. This is a clean phase exit, not a claim that the pilot is sufficient for training or primary metrics.

## Phase 0 — Scope, specification, and ethics

| ID | Deliverable | Status | Evidence / qualification |
|---|---|---|---|
| 00.0 | Course-topic approval | Reported approved | The student has reported instructor approval for this custom topic and solo work. Submit any required registration form separately. |
| 00.1 | Project brief | Complete | [`project-brief.md`](project-brief.md) defines user, scene, input, output, scope, and non-goals. |
| 00.2 | MVP boundary | Complete as a scope decision | [`mvp-scope.md`](mvp-scope.md) limits the project to two categories. Planned functionality is not implemented yet. |
| 00.3 | Event vocabulary | Complete for qualitative annotation pilot | [`event-vocabulary.md`](event-vocabulary.md) distinguishes conflict candidate, non-conflict, uncertain, source labels, and modality limits. Numeric model thresholds are not set. |
| 00.4 | Acceptance targets | Specified, not measured | [`acceptance-targets.md`](acceptance-targets.md) records proposed metrics and targets. Feasibility depends on annotation volume; none is an achieved result. |
| 00.5 | Risks and ethics | Complete as planning artifact | [`risk-register.md`](risk-register.md) records safety, privacy, licensing, domain, and evaluation risks. |

**Phase 0 assessment:** The project specification and its two-category scope are documented and frozen for implementation. This does not mean the system or evaluation is complete. The approval item is based on the student's report; any formal course submission remains the student's action.

## Phase 1 — Data access, inventory, split, and annotation pilot

| ID | Deliverable | Status | Evidence / qualification |
|---|---|---|---|
| 01.1 | Read data access and terms | Audit record complete | [`dataset-access.md`](dataset-access.md); local download manifest is ignored/raw and must be present to reproduce archive checks. |
| 01.2 | Complete sample inventory | Audit and local archive extraction complete | [`data/README.md`](../data/README.md), [`projection-audit.md`](projection-audit.md), [`dot-sample-audit.json`](../results/audits/dot-sample-audit.json), and [`raw-archive-extraction.json`](../results/audits/raw-archive-extraction.json). All locally available ZIPs were CRC-checked; the separate ~1 TB DOT full training archive is not downloaded. Selected-camera RGB projections are not approved as image-space ground truth. |
| 01.3 | Inspect label semantics | Complete | [`event-vocabulary.md`](event-vocabulary.md): DOT conflict/no-conflict is run/scenario-level, not an event or actor-pair label. |
| 01.4 | Decide dataset alignment | Complete as a source-role decision | [`dataset-decision.md`](dataset-decision.md): DOT is the fixed-camera video source requiring project annotation; ROCO is trajectory-only; Waterloo is excluded pending reuse terms. Neither category has ready video event ground truth. |
| 01.5 | Choose compact subset | Manifest and audit complete | [`compact-subset-selection.md`](compact-subset-selection.md), manifest and audit. The 10 selected DOT runs are test candidates; they do not provide event-level labels. |
| 01.6 | Create sequence split | Reproducible run-level split complete, with exposure caveat | [`splits.csv`](../data/manifests/splits.csv), [`sequence-split-audit.json`](../results/audits/sequence-split-audit.json): 16 train, 4 development, 41 test runs. Contact sheets were generated for all splits, including test; viewing is not logged. Do not describe test as blind or wholly unseen. |
| 01.7 | Build inspection gallery | Context gallery artifact complete | [`inspection-gallery.md`](inspection-gallery.md). Gallery images are context samples, not exhaustive review or event annotations. |
| 01.8 | Document data card | Complete as documentation | [`data-card.md`](data-card.md) must retain source-specific modality, label, terms, and sampling limitations. |
| 01.9 | Audit supplemental data/schema/terms | Audits complete; use restrictions remain | [`supplemental-data-audit.md`](supplemental-data-audit.md), [`candidate-dataset-audit.md`](candidate-dataset-audit.md), and JSON audit results. Waterloo remains excluded pending permission. ROCO supports a separate trajectory-only analysis. |
| 01.10 | Create project event-label set | **Complete on exploratory fallback** | [`events.csv`](../data/annotations/v1/events.csv) has three student-adjudicated pedestrian–vehicle potential-conflict windows, one pedestrian–vehicle non-conflict window, and one uncertain vehicle–vehicle window. Three rows disclose student-directed adoption of assistant proposals without separate student playback. [`annotation-summary-v1.json`](../results/annotation-summary-v1.json) shows neither category meets its sample gate; both are explicitly exploratory. No test event labels were added. |

**Phase 1 assessment:** Data inventories, local archive extraction checks, source audits, the DOT run-level split, and the annotation pilot have reproducible artifacts. Phase 1 is **closed with an exploratory annotation set** under the 01.10 fallback: categories below the minimum are explicitly designated exploratory. The pilot is insufficient for supervised training or primary event metrics; expanding it is required before model fitting.

## Category-specific evidence boundary

### Pedestrian–vehicle

DOT VisualCamera7 provides fixed-camera video, plus DOT's own run/scenario labels. It does not provide event intervals or pair IDs. Two windows are based on the student's continuous-video review; one further potential-conflict and one non-conflict window were explicitly adopted from assistant first-pass proposals. Their notes and the review log disclose that no separate student playback is recorded. These are potential-conflict safety-review labels, not confirmed collisions. The sample remains too small for primary metrics.

### Vehicle–vehicle

DOT training/development footage yielded one assistant-proposed vehicle–vehicle window, which the student explicitly adopted as `uncertain`; there is no binary vehicle–vehicle video label. ROCO has 101 source-labeled trajectory events and no RGB video; keep this as a distinct trajectory-only comparator. Waterloo video/track archives are not approved for public project use while reuse terms are unresolved. Do not describe either source as a ready vehicle–vehicle video benchmark.

## Evaluation integrity

- Keep all frames from a source recording in one split; the existing DOT split is run-disjoint.
- Test context frames exist in the generated gallery and gallery-view history is not recorded. The policy prohibits test tuning, but the project cannot claim content-blind test handling.
- Do not use DOT test run labels to tune event-level criteria.
- Use only train/development clips for annotation-rule and model development until the protocol is fixed. Keep test event labels sealed until then.
- Distinguish direct student clip review from explicit student adoption of assistant proposals; no independent second annotator is present.
- If annotation minimums prove infeasible, document a justified target revision before viewing model predictions on test; otherwise report the category as exploratory.

## Reproducibility commands

Run from the repository root. Dataset-dependent commands require the locally downloaded files described in `data/README.md`; raw archives are not committed.

```powershell
python scripts/extract_available_archives.py
python scripts/audit_sample_data.py
python scripts/audit_supplemental_data.py
python scripts/audit_candidate_datasets.py
python scripts/create_sequence_split.py
python scripts/build_compact_subset_manifest.py
python scripts/summarize_event_annotations.py
```

The current annotation summary reports the exact adjudicated and uncertain counts, assistant-assisted provenance, and exploratory category gates. Regenerating reports does not add evidence. Gallery rebuilding also reads test clips; do not do so during a blind-test protocol without revising and documenting the evaluation plan.

## Freeze decision and remaining work

- **Scope freeze:** Yes—two categories only.
- **Phase 0 specification freeze:** Yes—with course registration as an external student action if required.
- **Phase 1 freeze/completion:** Yes, on the 01.10 fallback. Both categories are explicitly exploratory because they miss the target minimum; provenance and timestamp checks pass, and no test event labels or predictions were added. Reopen annotation before claiming primary metrics or training a supervised event model.
- **Model/evaluation freeze:** Not applicable yet; implementation and test evaluation have not been completed.

Remaining work before model training or primary evaluation: increase pedestrian–vehicle coverage across more source runs and establish binary vehicle–vehicle examples from suitable train/development footage or obtain a better source. Reopen the phase's annotation activity if this expands the agreed scope; do not turn an unobservable case into a negative.
