# LiveCross — Data Readiness & Annotation Plan

**Version:** 2.1
**Status:** Inventory and candidate audits are documented; event-level data readiness is incomplete.

## Frozen project scope

LiveCross currently targets only **pedestrian–vehicle** and **vehicle–vehicle** interactions in fixed-camera intersection video. Other pair types are out of scope. See [`mvp-scope.md`](mvp-scope.md).

## Current source roles

| Source | Role | Limitation / next gate |
|---|---|---|
| DOT ISC Stage 1B | Fixed-camera video for train/development review and a held-out candidate pool | Source conflict labels are run-level, not event-level or pairwise. Continuous video annotation is required for both target categories. |
| ROCO | Separate vehicle–vehicle trajectory-only comparator | No RGB video; never combine its metrics with LiveCross video metrics. |
| TUMTraf-Accid3nD sample | Exploratory roadside object-perception reference | Highway accident domain, not an intersection conflict benchmark. |
| Waterloo Intersection | Not selected for the public deliverable | Reuse terms unresolved; obtain authoritative written terms before use or publication. Its route intersection records are not event ground truth. |
| TGSIM | Trajectory-feature exploration | No RGB video or source conflict event labels. |

## Required event-label work

1. Use only permission-cleared continuous source video. Preserve complete source recordings within one split.
2. Review the pedestrian–vehicle draft windows and either correct/adjudicate them or retain them as uncertain/excluded.
3. Annotate vehicle–vehicle pairs separately from DOT run-level labels. Record positive, observable non-conflict, uncertain, and excluded cases using [`manual-annotation-protocol.md`](manual-annotation-protocol.md).
4. Save exact frame indices and source timestamps, source/run identifiers, actor IDs where defensible, annotation version, reviewer, and uncertainty reason. Do not infer events from contact sheets alone.
5. Keep test event labels sealed until annotation rules and model/threshold choices are fixed. Because test context sheets were generated and gallery-view status is unknown, disclose this exposure limitation; do not call the test set fully unseen.
6. Run `python scripts/summarize_event_annotations.py` after annotation changes. Current pilot minimum: 20 adjudicated potential-conflict and 20 adjudicated non-conflict windows per category across at least five source runs. If this is not feasible, revise the target before test predictions are viewed and explicitly label that category exploratory.

## Data handling

Raw archives and derived imagery remain in Git-ignored locations. Keep citations, access dates, license/terms, archive inventories, and hashes where available. Do not publicly share Waterloo material or derived media unless reuse is cleared. Never represent a dataset as downloaded or verified based only on an audit plan.

## Current status

No additional raw data acquisition is required to continue the **annotation pilot** using the already downloaded DOT training samples. The available evidence does not yet establish enough event ground truth for either category. The phase remains incomplete until the review work and its reproducible summary are finished.
