# LiveCross — Data Card

**Version:** 2.1
**Reviewed:** 18 November 2026
**Purpose:** Document source data and its limits for the two in-scope categories: pedestrian–vehicle and vehicle–vehicle.

## Summary

LiveCross currently has a fixed-camera DOT video source with run-level scenario labels, plus trajectory-only supplements. A small manually curated pair-level RGB event pilot exists, but it is not sufficient or diverse enough for supervised training or primary metrics in both target categories. Raw data remain local and excluded from Git. See [`dataset-access.md`](dataset-access.md) for access, terms, citations, and archive details; [`dataset-decision.md`](dataset-decision.md) for source roles.

## DOT ISC Stage 1B

### Collection and modality

- Controlled intersection testbed footage from the U.S. DOT Intersection Safety Challenge.
- Selected view: VisualCamera7, fixed roadside RGB, 1280×720, nominal 30 FPS. Timestamp CSVs have irregular intervals; one audit measured approximately 26.9 Hz for its inspected stream. Use source timestamps, not nominal frame-rate-derived time, where available.
- The raw archives contain multiple sensor modalities; the RGB workflow uses the selected camera and matching timestamps.

### Local inventory and split

- Validation archive: 41 complete runs, assigned to the held-out `test` partition by the repository's run-level split manifest.
- Public training samples: 20 runs total; 16 assigned to `train`, 4 to `validation`/development.
- Compact subset: 10 complete VisualCamera7 test runs, deliberately balanced 5/5 by DOT run-level source label and sampled for visual conditions. This design is not prevalence-representative.
- Inspection contact sheets were generated for runs in all splits, including test. Whether a person viewed each test sheet is not logged; therefore the test data cannot be described as fully unseen or content-blind.
- All 10 ZIP archives currently present locally have been CRC-checked and extracted/reused under `data/raw/`; see [`raw-archive-extraction.json`](../results/audits/raw-archive-extraction.json). The extractions total 71,469,554,117 bytes (about 66.6 GiB). The separately described ~1 TB official full training archive is not downloaded.

Recreate inventories and splits using the scripts listed in [`phase0-phase1-freeze.md`](phase0-phase1-freeze.md). Results depend on locally present raw archives.

### Labels and annotation status

- DOT's `conflict` / `no conflict` labels apply at run/scenario level, not to individual events, frames, or actor pairs.
- The audited VisualCamera7 3D-label projection is not approved as RGB image-space ground truth.
- The project table contains three student-adjudicated pedestrian–vehicle potential-conflict windows, one pedestrian–vehicle non-conflict window, and one uncertain vehicle–vehicle window. Three rows were explicitly adopted from assistant proposals without separate student playback; this is disclosed in their notes and the review log.
- Both categories remain exploratory and fail their predeclared sample gates. Do not present the pilot as sufficient for supervised training or primary evaluation; retain the assistant-assisted and solo-review limitations in reporting.

### Biases and limitations

The DOT data represent a controlled test facility and a limited set of scenarios, a single selected camera view, and a small number of public training runs. The run-level label imbalance and deliberately balanced compact subset must be reported accurately. Generalization to natural roads, other cameras, weather, geographies, and road-user behavior is not established.

## ROCO vehicle-conflict trajectories

- Local archive: `data/raw/roco/ROCO.zip`; the supplemental audit records the archive inventory and a CSV parsing quirk.
- The source describes 101 labeled vehicle–vehicle conflict trajectory events sampled at 2.5 Hz, including severity and interacting trajectory IDs.
- **No RGB video is included.** ROCO supports only a separately reported trajectory-method comparison. It cannot validate LiveCross video detection, tracking, visual event localization, or image explanations.
- Follow the upstream attribution and CC BY-SA/additional dataset terms before distributing adaptations.

## Other audited sources

- **Waterloo Intersection:** local video/track archives were inventoried; publisher reuse terms remain unresolved. Excluded from public demo, benchmark, and publication pending authoritative permission. Route intersection points are not pair-level conflict labels.
- **TGSIM:** trajectory data, not RGB video or source conflict labels; exploratory motion-feature use only.
- **TUMTraf-Accid3nD:** small roadside highway perception sample; useful only as an exploratory vehicle-perception reference, not an urban intersection conflict benchmark.
- **DoTA and JRDB:** not selected for primary evaluation due to the documented perspective, split, access, and/or semantic mismatch in [`candidate-dataset-audit.md`](candidate-dataset-audit.md).

## Privacy, rights, and safe use

Keep raw data and generated frames local under ignored directories. Preserve source citation and terms. Do not include identifiable footage in public artifacts without permission and privacy review. LiveCross is a retrospective research/course prototype, not a certified collision warning system; it does not determine fault or claim that a crash was inevitable or prevented.
