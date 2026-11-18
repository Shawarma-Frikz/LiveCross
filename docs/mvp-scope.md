# LiveCross — MVP Boundary & Scope Specification

**Version:** 2.1
**Status:** The two-category project scope is frozen. Phase 1 is closed on the documented exploratory fallback; the event-label pilot is still too small for supervised event training or primary metrics. See [`phase0-phase1-freeze.md`](phase0-phase1-freeze.md).

## 1. Scope

LiveCross is a course-scale, explainable computer-vision prototype for reviewing potential traffic conflicts in fixed-camera intersection video. It targets exactly:

1. **Pedestrian–vehicle** interactions.
2. **Vehicle–vehicle** interactions.

These are the intended analysis categories, not categories with already-validated event-level benchmarks. DOT supplies fixed-camera video and documented scenario-level labels for its own scenarios, but no event times or native pairwise conflict labels. ROCO supplies labeled vehicle–vehicle trajectories but no RGB video. Waterloo is excluded from the public benchmark until reuse terms are confirmed. The current versioned event-label set is a small exploratory draft.

Pedestrian–pedestrian, vehicle–fixed-object, and pedestrian–fixed-object interactions are out of scope for this version.

## 2. Functional plan and status

| Module | Planned MVP behavior | Current status |
|---|---|---|
| Video ingestion | Read recorded MP4/AVI, preserve frame indexing and source timestamps where available; support webcam only as staged demo input. | Not implemented. DOT video/timestamp inventory audited. |
| Object perception | Detect pedestrians and road vehicles with a compact pretrained detector. | Not implemented or benchmarked. |
| Multi-object tracking | Associate detections over time and preserve track histories. | Not implemented or benchmarked. |
| Scene configuration | Define a crossing/junction region in normalized image coordinates. | Not implemented. |
| Candidate generation | Form pedestrian–vehicle and vehicle–vehicle track pairs. | Not implemented. |
| Risk reasoning | Compare a transparent trajectory/zone baseline with a learned model only if enough reviewed labels exist. Distances without calibration are image-plane proxies. | Not implemented; no thresholds are yet claimed as validated. |
| Hard-negative mining | Mine and review safe but visually confusing pairs from training data only. | Not implemented; requires adjudicated training labels. |
| Explanations | Show track IDs, paths, relevant timing/proximity factors, and uncertainty. | Not implemented. |
| Review interface | Provide replay, timeline, event inspection, and responsive layout. | Not implemented. |

## 3. Dataset roles and ground-truth status

| Category | Video source | Additional evidence | Current event-label status |
|---|---|---|---|
| Pedestrian–vehicle | DOT ISC Stage 1B VisualCamera7 | DOT run-level scenario label only; not event ground truth | Three adjudicated potential-conflict windows and one non-conflict window; two are direct student video reviews and two are assistant-assisted adoptions. Exploratory only. |
| Vehicle–vehicle | DOT training/development video | ROCO provides a separate trajectory-only comparison (101 source event records), not RGB/video evaluation | One assistant-assisted uncertain window; no binary video label. Exploratory only. |

Do not use DOT run-level labels as frame or actor-pair labels. Do not report ROCO trajectory scores as visual model scores. Do not use Waterloo in a public artifact unless reuse is cleared. See [`dataset-decision.md`](dataset-decision.md) and [`supplemental-data-audit.md`](supplemental-data-audit.md).

## 4. Evaluation principles

- Keep complete source recordings in one split and keep training, development, and test evidence separate.
- Freeze annotation and matching rules before evaluating predictions on held-out data.
- Report precision, recall, false-alert rate, delay, throughput, sample counts, and failure cases per category only when labels and denominators support them.
- If a category does not meet the predeclared annotation minimum, report it as exploratory; do not present a target metric as achieved.
- Compare a transparent baseline and an interaction-level model only after sufficient adjudicated training data exists.

## 5. Non-goals and safeguards

- No collision-prevention, driver-warning, traffic-control, fault-assignment, or inevitability claims.
- No metric distance claim without validated camera calibration.
- No face recognition or license-plate OCR.
- No deliberate dangerous collision staging. Any future demonstrations must use safe, controlled recording conditions.
