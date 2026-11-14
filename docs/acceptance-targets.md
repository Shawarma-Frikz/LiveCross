# LiveCross — Acceptance Targets

**Status:** Initial targets recorded before any held-out test results are viewed.  
**Dataset metadata inspected:** U.S. DOT Intersection Safety Challenge Stage 1B, 14 November 2026. The downloadable sample archive has not yet been inspected locally; confirm data coverage and label mapping at task 01.2 before freezing the final test protocol.

## Dataset facts that affect evaluation

The official DOT pages describe separate training and validation assets. Training has 1,104 runs, is unlabeled, is approximately 1 TB in full, and only a subset is downloadable as public sample ZIPs; the full set requires a data request. Validation has 41 runs, is approximately 30 GB in full, and includes a five-run, approximately 3 GB sample. Its ground truth includes 3D road-user boxes per timestamp and a **run-level** conflict/no-conflict label. DOT describes scenarios involving vulnerable road users (pedestrians/bicyclists) and vehicles. That supports the primary VRU–vehicle benchmark only; it does not establish reference labels for vehicle–vehicle, pedestrian–pedestrian, or vehicle–fixed-object interactions. The official data story says visual camera MP4s have frame-timestamp CSVs.

Therefore:

- The run-level labels can support a run-level conflict/no-conflict measure.
- The additional pair types need a separate permission-cleared annotation set; report them separately and mark them exploratory until the sample supports meaningful evaluation.
- They do not, by themselves, provide event start/end times. Event-level precision/recall and alert delay need a separately documented manual event annotation set.
- Do not treat the unlabeled training runs as supervised conflict labels, and do not report event-level metrics against run labels.
- If inspection of the five-run sample cannot support the minimum event set below, keep event-level results exploratory and record the limitation; do not weaken thresholds after looking at test results.

Sources: [DOT training data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Training-Da/vq7s-mv3v), [DOT validation data](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4), and [DOT open-data story](https://data.transportation.gov/stories/s/U-S-DOT-Intersection-Safety-Challenge-Stage-1B-Sys/smqb-i5sx/).

## Evaluation set and split gate

Before training or viewing test-set results:

1. Inspect the DOT validation sample and confirm its camera MP4s, timestamp CSVs, run labels, and 3D-box contents.
2. Create manual event intervals only for the subset used for event-level evaluation. Record reviewer, run, time bounds, involved tracks when identifiable, label, and uncertainty reason.
3. Require at least **20 conflict and 20 non-conflict interaction windows across at least five distinct runs**, with complete runs held out from tuning. If the available sample cannot meet this minimum, report event metrics as exploratory and evaluate run-level labels separately.
4. Assign complete runs to train/development/test before tuning thresholds. Keep the test-run IDs sealed from hard-negative mining and model selection.
5. Freeze this target sheet and the event-matching rule before opening test predictions.

## Primary acceptance targets

| ID | Measure | Target | How it will be measured |
|---|---|---:|---|
| A1 | Event precision | **≥ 0.70** | True positive event matches divided by all predicted events on held-out runs. |
| A2 | Event recall | **≥ 0.70** | True positive event matches divided by all manually annotated conflict events on held-out runs. |
| A3 | False-alert rate | **≤ 0.5 per minute** of annotated non-conflict footage | Count unmatched predicted events only over non-conflict duration; report the duration denominator. |
| A4 | Hard-negative mining effect | **≥ 20% relative reduction** in false-alert rate versus the unmined baseline, with recall loss **≤ 5 percentage points** | Compare rule/classifier before and after mining on the exact same held-out runs and event-matching rule. If baseline false-alert rate is zero, report mining effect as not measurable rather than claiming improvement. |
| A5 | Event detection delay | Median **≤ 2.0 seconds** from first annotated observable conflict evidence to first matching alert | Evaluate only matched held-out events; also report the full distribution and missed events. |
| A6 | End-to-end processing speed | **≥ 5 processed FPS** at the chosen MVP image size on the named demo computer | Include decode, detection, tracking, scoring, and rendering; report hardware, input size, and whether CPU/GPU was used. |
| A7 | Demo readiness | Browser demo ready within **60 seconds** of launch in **3 of 3 cold starts** | Measure from the documented start command to the first usable replay screen; keep webcam startup as a separate result. |

### Event-matching rule

For event-level scores, a prediction matches a reference event when it is in the same run, has the same pair type, and its time interval overlaps the reference interval by at least **50% of the shorter interval**. If the data permits reliable actor identity, require the same actor pair (or same vehicle and fixed-hazard ID) too. Count each reference event and each predicted event at most once; unmatched predictions are false alerts and unmatched references are misses. Review this rule against each sample annotation format before locking the test protocol.

## Secondary reporting targets

- Report run-level conflict/no-conflict balanced accuracy and per-class precision/recall when the official run labels are available; do not substitute this for event-level metrics.
- Report counts and denominators for every metric, not only percentages.
- Break out results by day/night or other conditions only when the number of held-out runs supports a meaningful comparison; otherwise mark them descriptive.
- Include representative true positives, false positives, false negatives, and uncertain/occluded cases.

## Freeze rule

These are project acceptance thresholds, not a claim that the model already meets them. After inspecting the sample and documenting annotation feasibility, any change must be recorded here **before** test predictions or test metrics are viewed, with the reason and the date. Once test results have been viewed, preserve these targets for the reported evaluation and explain any unmet target rather than changing it retrospectively.
