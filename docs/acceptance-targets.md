# LiveCross — Acceptance Targets

**Status:** Initial targets recorded before any held-out test results are viewed.  
**Dataset metadata and five-run sample inspected:** U.S. DOT Intersection Safety Challenge Stage 1B, 14 November 2026. The public sample is adequate for an engineering pilot, not for strong final performance claims. Inspect the public 41-run validation asset and complete annotation dictionary before freezing the final protocol. The four-category evidence plan is in [`dataset-expansion-plan.md`](dataset-expansion-plan.md).

## Dataset facts that affect evaluation

The official DOT pages describe separate training and validation assets. Training has 1,104 runs, is unlabeled, is approximately 1 TB in full, and only a subset is downloadable as public sample ZIPs; the full set requires a data request. Validation has 41 runs, is approximately 30 GB in full, and includes a five-run sample; the downloaded ZIP is 3,540,625,371 bytes. Its ground truth includes 3D road-user boxes per timestamp and a **run-level** conflict/no-conflict label. The inspected five-run label file contains two conflict and three non-conflict runs. DOT describes scenarios involving vulnerable road users (pedestrians/bicyclists) and vehicles. That supports the primary VRU–vehicle benchmark only; it does not establish reference labels for vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object interactions. The sample includes visual camera MP4s with frame-timestamp CSVs.

Therefore:

- The run-level labels can support a run-level conflict/no-conflict measure.
- The MVP includes all four pair types. DOT-backed evaluation applies only to VRU–vehicle; vehicle–vehicle, pedestrian–pedestrian, and vehicle–fixed-object need a separate permission-cleared, manually annotated set and category-specific evaluation.
- They do not, by themselves, provide event start/end times. Event-level precision/recall and alert delay need a separately documented manual event annotation set.
- Do not treat the unlabeled training runs as supervised conflict labels, and do not report event-level metrics against run labels.
- If inspection of the five-run sample cannot support the minimum event set below, keep event-level results exploratory and record the limitation; do not weaken thresholds after looking at test results.

Sources: [DOT training data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Training-Da/vq7s-mv3v), [DOT validation data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4), and [DOT open-data story](https://data.transportation.gov/stories/s/U-S-DOT-Intersection-Safety-Challenge-Stage-1B-Sys/smqb-i5sx/).

## Evaluation set and split gate

Before training or viewing test-set results:

1. Inspect the full validation sample/metadata and confirm camera MP4s, timestamp CSVs, run labels, 3D-box contents, and frame-to-time behavior. A representative MP4/CSV has already been verified; its timestamps span about 73 seconds for 1,968 frames while the MP4 reports 30 FPS.
2. Create manual event intervals only for the subset used for event-level evaluation. Record reviewer, run, time bounds, involved tracks when identifiable, label, and uncertainty reason.
3. Apply the minimum separately to each pair type: at least **20 conflict and 20 non-conflict interaction windows across at least five distinct source clips/runs**, with source clips/runs held out from tuning. The current DOT sample has only two conflict and three non-conflict run labels and does not meet this event-window target. If a category cannot meet it with permission-cleared footage, report its event metrics as exploratory and show counts and failure cases; do not pool categories to hide sparse evidence.
4. Assign complete runs to train/development/test before tuning thresholds. Keep the test-run IDs sealed from hard-negative mining and model selection.
5. Freeze this target sheet and the event-matching rule before opening test predictions.

## Primary acceptance targets

| ID | Measure | Target | How it will be measured |
|---|---|---:|---|
| A1 | Event precision, per pair type | **≥ 0.70** where the category meets its sample-size gate | True positive event matches divided by all predicted events on held-out source clips/runs; report each category separately. |
| A2 | Event recall, per pair type | **≥ 0.70** where the category meets its sample-size gate | True positive event matches divided by all manually annotated conflict events on held-out source clips/runs; report each category separately. |
| A3 | False-alert rate, per pair type | **≤ 0.5 per minute** of annotated non-conflict footage, where sample permits | Count unmatched predicted events only over non-conflict duration; report category and duration denominator. |
| A4 | Hard-negative mining effect, per pair type | **≥ 20% relative reduction** in false-alert rate versus the unmined baseline, with recall loss **≤ 5 percentage points**, where measurable | Compare rule/classifier before and after mining on identical held-out clips and matching rule. Mine only training negatives. If baseline rate is zero or a category is too sparse, mark not measurable/exploratory. |
| A5 | Event detection delay, per pair type | Median **≤ 2.0 seconds** from first annotated observable conflict evidence, where labels permit | Evaluate only matched held-out events; report category, full distribution, and missed events. |
| A6 | End-to-end processing speed | **≥ 5 processed FPS** at the chosen MVP image size on the named demo computer | Include decode, detection, tracking, scoring, and rendering; report hardware, input size, and whether CPU/GPU was used. |
| A7 | Demo readiness | Browser demo ready within **60 seconds** of launch in **3 of 3 cold starts** | Measure from the documented start command to the first usable replay screen; keep webcam startup as a separate result. |

### Event-matching rule

For event-level scores, a prediction matches a reference event when it is in the same source clip/run, has the same pair type, and its time interval overlaps the reference interval by at least **50% of the shorter interval**. If the data permits reliable actor identity, require the same actor pair (or same vehicle and fixed-hazard ID) too. Count each reference event and each predicted event at most once; unmatched predictions are false alerts and unmatched references are misses. Review this rule against each sample annotation format before locking the test protocol.

## Secondary reporting targets

- Report run-level conflict/no-conflict balanced accuracy and per-class precision/recall when the official run labels are available; do not substitute this for event-level metrics.
- Report counts and denominators for every metric, not only percentages.
- Break out results by day/night or other conditions only when the number of held-out runs supports a meaningful comparison; otherwise mark them descriptive.
- Include representative true positives, false positives, false negatives, and uncertain/occluded cases.

## Freeze rule

These are project acceptance thresholds, not a claim that the model already meets them. After inspecting the sample and documenting annotation feasibility, any change must be recorded here **before** test predictions or test metrics are viewed, with the reason and the date. Once test results have been viewed, preserve these targets for the reported evaluation and explain any unmet target rather than changing it retrospectively.
