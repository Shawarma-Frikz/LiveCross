# Supplemental dataset audit

**Audit date:** 15 November 2026
**Purpose:** Decide what the already-downloaded non-DOT datasets can support in LiveCross. This is a source/format/label audit, not a model evaluation or permission to redistribute data.

Official source pages were checked on 15 November 2026. Local counts below come from the downloaded files and are reproducible with the script; collection descriptions and reuse statements come from the linked publishers/catalog records.

The machine-readable local inventory is [`results/audits/supplemental-dataset-audit.json`](../results/audits/supplemental-dataset-audit.json). Recreate it from the repository root with:

```powershell
python scripts/audit_supplemental_data.py
```

The script uses only Python's standard library. It reads the TGSIM CSV, opens the ROCO ZIP without extracting it, and reads one representative SQLite database from the Waterloo archive. It does not copy videos into the repository or change the source archives. If a source archive is absent on another checkout, it records the expected path as unavailable and continues.

## Decision summary

| Dataset | Local audit | Appropriate LiveCross role | What it does not establish | Reuse status |
|---|---|---|---|---|
| DOT ISC Stage 1B | Primary RGB video source; details in [`data-card.md`](data-card.md) | Video pipeline and future manual annotations for the two in-scope categories | Native event-level or actor-pair conflict labels; run labels cannot be reused as event labels | Public access; follow DOT citation and source terms in [`dataset-access.md`](dataset-access.md) |
| FHWA TGSIM Foggy Bottom | 2,492,261 trajectory rows, 20,511 IDs, eight road-user types, approximately 0.1 s sampling | Motion-feature experiments and candidate-window generation; useful for pedestrian/vehicle and other dynamic-agent pairs | RGB video, source conflict labels, or any fixed-object interaction labels | DOT catalog marks it public and provides a public-domain license field; cite the data story and retain source metadata |
| ROCO sample | 101 labeled vehicle-conflict events, 8,080 trajectory-frame JSON files; publisher describes 30-second event clips sampled at 2.5 Hz | Vehicle–vehicle conflict-trajectory analysis; external event-label source for a separate trajectory-only experiment | RGB video, pedestrian conflicts, fixed-object conflicts, detector performance, or image-space XAI | Repository states CC BY-SA 4.0 plus dataset terms; preserve attribution and share-alike obligations for adapted material |
| Waterloo Intersection | 14 AVI videos paired by stem with 14 SQLite databases; representative DB includes car and pedestrian tracks; publisher describes about one hour of overhead-drone footage | Audited locally for format and content only | Public use, redistribution, demo, or conflict ground truth; `CONFLICT_POINTS` are geometric route intersections, not observed near misses or crashes | **Unresolved:** publisher page does not specify a license/reuse terms. Excluded from the public benchmark and deliverables until authoritative terms are confirmed |

These sources do not close the two-category event-ground-truth gap. Keep results separated by source and evidence type. Do not pool surrogate or route-based labels with DOT run labels or ROCO event labels.

## FHWA TGSIM Foggy Bottom

### Local file inspection

- File: `data/raw/tgsim-foggy-bottom.csv`, **342,323,446 bytes**.
- Parsed **2,492,261 rows**, **20,511 unique IDs**, 12 columns, and no blank cells in the inspected CSV.
- The audit checks the exact 12-column header against the expected source schema and checks consecutive timestamps in the raw CSV order within each ID. It finds **151 backward-time transitions and no duplicate-time transitions**; the report preserves the first five examples. These are ordering anomalies in the file traversal, not proof of invalid trajectories. Any temporal feature pipeline must explicitly group and sort by ID/time, then investigate whether repeated IDs span discontinuous sequences; the audit does not reorder or rewrite source data.
- Columns: `id`, `time`, `xloc_kf`, `yloc_kf`, `lane_kf`, `speed_kf_x`, `speed_kf_y`, `acceleration_kf_x`, `acceleration_kf_y`, `length_smoothed`, `width_smoothed`, `type_most_common`.
- Time values range from 60.2 to 7,200 seconds. The most common within-track interval is 0.1 seconds (2,470,386 intervals); larger gaps exist and must not be silently interpolated.
- Observed type-code row counts: 0/person 766,876; 1/bicycle 8,453; 2/scooter 1,739; 3/passenger car 1,581,551; 4/automated vehicle 34,020; 5/motorcycle 652; 6/bus 17,631; 7/truck 81,339. Meanings are from the official project data dictionary, not inferred from the CSV.
- The official data dictionary describes positions and dimensions in meters, speed in m/s, acceleration in m/s², and time in seconds. Verify field/coordinate semantics against the source report before building features; do not confuse these coordinates with camera image pixels.

### Suitability and limits

The official [FHWA catalog record](https://catalog.data.gov/dataset/third-generation-simulation-data-tgsim-foggy-bottom-trajectories) describes 12 stationary 4K infrastructure cameras covering four intersections/crosswalks/segments in Foggy Bottom during sunny weekday afternoon commutes (3–5 p.m. Eastern). The downloaded local asset audited here is the trajectory CSV, not the camera video. This is motion data rather than a video dataset. It is suitable for testing trajectory calculations, checking sampling-gap handling, and proposing windows for later human review. The CSV itself contains no conflict-event labels. Any TTC/PET/distance threshold added by LiveCross would create a **project-defined surrogate target**, not an observed collision or source-annotated near miss. It cannot train or evaluate a visual detector or validate visual explanations.

### Source, terms, and citation

The [official FHWA catalog record](https://catalog.data.gov/dataset/third-generation-simulation-data-tgsim-foggy-bottom-trajectories) describes the contents, measurement conversion, and supporting region files. The [DOT TGSIM data story](https://data.transportation.gov/stories/s/Third-Generation-Simulation-Data-TGSIM-/uwv8-dpvx/) gives the recommended citation and asks users to notify ITS JPO if the data is used in publications. The catalog metadata marks it public and lists the USA.gov Public Domain Mark 1.0; retain the citation and access date rather than treating “public” alone as complete terms.

Recommended citation: U.S. Department of Transportation Federal Highway Administration. (2024). *Third Generation Simulation Data (TGSIM) Foggy Bottom Trajectories* [Dataset]. Provided by ITS DataHub through Data.transportation.gov. Accessed 2026-11-15 from https://doi.org/10.21949/1404230.

## ROCO sample

### Local file inspection

- File: `data/raw/roco/ROCO.zip`, **25,063,270 bytes**; 8,080 JSON frame files in 101 event folders. The reproducible archive inventory counts every file by extension to make the absence of image/video frame files explicit.
- `conflict_label.csv` contains **101 event rows**: 98 severity-1 near misses and 3 severity-2 traffic accidents. Reason codes: 0=53, 1=7, 2=14, 3=12, 4=15. Effect codes: 0=24, 1=47, 2=30. Definitions are in the upstream README.
- The sample JSON has a `fusion` list with track ID, confidence, latitude/longitude, UUID, category, speed, and heading; the upstream README describes categories as cars and trucks/buses/trailers.
- **CSV parsing/source-version defect:** The local physical header has five columns (`event_time`, `severity`, `reason`, `conflict trajectory pair`, `effect`), while the repository README documents six (`event_timestamp`, `severity`, `reason`, `conflict trajectory pair`, `effect`, `time offset`). All 101 local data rows have six fields because the pair tuple is unquoted and splits across two columns. A normal `DictReader` therefore shifts pair/effect interpretation. The audit script reconstructs the two pair IDs and final effect field by position, and fails if the row shape changes. The local package also lacks the README-described `time offset` field; do not infer or synthesize it.

### Suitability and limits

The official [ROCO repository](https://github.com/michigan-traffic-lab/ROCO) describes a one-week sample from a roundabout at State Street and West Ellsworth Road in Ann Arbor, with 30 seconds per event sampled at 2.5 Hz. ROCO is the strongest downloaded supplement for source-labeled **vehicle–vehicle conflict trajectories**. Its local release provides trajectory JSON and event metadata, not RGB frames, so it cannot be used to evaluate LiveCross's image detector, video tracking, or image overlays. Its labels reflect the dataset authors' conflict-event process; do not relabel them as collision certainty. The sample has only three severity-2 accident events, so do not make an accident-class performance claim from this sample.

### Source, terms, and citation

The [official ROCO repository](https://github.com/michigan-traffic-lab/ROCO) documents collection, fields, label definitions, citation, and terms. It specifies **CC BY-SA 4.0**, with additional dataset terms taking precedence where inconsistent. Attribute the source and preserve share-alike requirements for adaptations. Check the exact terms before publishing derived data or a public processed copy; keep the downloaded archive outside Git.

Recommended citation: D. Meng, O. Sayer, R. Zhang, S. Shen, H. Li, and H. X. Liu. “ROCO: A Roundabout Traffic Conflict Dataset.” Transportation Research Board Annual Meeting, 2023. [Paper](https://arxiv.org/abs/2303.00563).

## Waterloo Multi-Agent Traffic Dataset: Intersection

### Local file inspection

- `data/raw/waterloo/annotated_videos.zip`: **4,673,980,140 bytes**, 14 AVI files.
- `data/raw/waterloo/intersection_dbfiles.zip`: **610,803,071 bytes**, 14 SQLite databases.
- All 14 database/video filename stems match.
- One representative database (`intsc_data_769.db`) has 283 tracks: 249 cars, 23 pedestrians, 6 medium vehicles, 3 heavy vehicles, 1 bus, and 1 bicycle. Its trajectory table has 196,678 rows. The tables include per-agent trajectories, track metadata, traffic regions/lights, actions, and 51 route-level `CONFLICT_POINTS`.

### Suitability and limits

The [WISE Lab page](https://uwaterloo.ca/waterloo-intelligent-systems-engineering-lab/datasets/waterloo-multi-agent-traffic-dataset-intersection) describes about one hour of overhead-drone recording and ID-annotated videos paired with trajectory databases. Local inspection supports an inventory of video/database pairs, but Waterloo is **not selected for the public project benchmark or demo** while reuse terms remain unresolved. The `CONFLICT_POINTS` table identifies geometric intersections between routes; it does not say a particular pair had a near miss or collision. The trajectory tables and behavior labels are not automatically pair-level conflict ground truth.

### Access and rights decision

The publisher's dataset page links directly to the database and annotated-video ZIPs but does not state an explicit license or reuse/redistribution terms; the linked downloads contain no separate terms notice. A download link is not itself a reuse license. Until terms are confirmed with WISE Lab, treat public redistribution, sharing clips, and publication of identifiable/derived video as **not cleared**. Keep the archives out of Git. Before using Waterloo as a public project artifact, obtain and record written permission or authoritative terms, plus the dataset's requested citation if one is supplied.

## Project use gate

1. Use DOT footage for the primary visual pipeline only within its documented run-label and projection limits.
2. Use ROCO for a separate, trajectory-only vehicle conflict analysis; account for the CSV quirk and class imbalance.
3. Use TGSIM for clearly marked trajectory-feature experiments or candidate generation, never as visual/event ground truth.
4. Exclude Waterloo from public artifacts and evaluation until authoritative reuse terms are confirmed; if later cleared, verify frame/track alignment and annotate actual events separately.
5. For all four sources, keep source and annotation type attached to every result. A detector score, a heuristic surrogate, a route intersection, a run-level label, and an event-level conflict label are different evidence and must be reported separately.
