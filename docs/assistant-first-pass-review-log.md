# Assistant first-pass review log

**Purpose:** Preserve the provenance and evidence behind assistant-proposed annotation candidates and the student's subsequent decision.

**Review method:** Candidate intervals were screened from the non-test DOT training footage using generated contact sheets, including focused views sampled at approximately 0.25-second intervals. No model predictions were consulted. This was a visual first pass over sampled frames, not exhaustive frame-by-frame review of each complete source video. The student must open and review each continuous source interval, then confirm, revise, or reject it before it can become an adjudicated annotation.

## Candidate records

| Event ID | Source / split | Interval | Proposed state | First-pass evidence and limitation |
|---|---|---|---|---|
| `LC-DOT-Run_889-PV-ASSIST-001` | DOT `Run_889`, train, `training-sample-1.zip` | Frames 1250–1363; source timestamps are recorded in `events.csv` | `non_conflict_interaction`, medium confidence | A pedestrian crosses the marked area while the vehicle appears to wait, then proceeds after the pedestrian clears. Confirm the continuous timing and whether this satisfies the project's eventual operational negative rule. |
| `LC-DOT-Run_942-PV-ASSIST-001` | DOT `Run_942`, train, `training-sample-2.zip` | Frames 634–777; source timestamps are recorded in `events.csv` | `potential_conflict`, low confidence | A pedestrian and turning vehicle appear to converge within the junction. Partial occlusion near closest approach limits outcome judgment. This does not assert collision, injury, or fault. |
| `LC-DOT-Run_87-VV-ASSIST-001` | DOT `Run_87`, train, `training-sample-1.zip` | Frames 732–810; source timestamps are recorded in `events.csv` | `uncertain`, low confidence | A foreground van appears stationary while another vehicle passes. The sampled evidence does not establish two active trajectories or settle whether a stationary vehicle is in scope for a vehicle–vehicle pair. Do not use as binary evidence unless the student resolves the pair rule and reviews the source interval. |

## Student decision and use

- On 18 November 2026, the student explicitly instructed that the candidate labels be adopted as student-adjudicated records. The CSV records `annotator_id=student` and `review_stage=student_adjudicated`, while each note states that the student-directed adoption relied on the assistant's sampled-frame review and that no separate student playback of these particular intervals is recorded.
- This is assistant-assisted adjudication, not an independent student visual review or independent second-annotator review. The proposal origin and method remain visible in the event IDs and notes.
- The proposed actor IDs are reviewer placeholders, not DOT source track IDs.
- Preserve `uncertain` where evidence or category scope is ambiguous. Do not convert it to a negative.
- The summary script counts the student-directed accepted binary labels toward category sample gates. This does not make the sample large enough for primary metrics; the vehicle–vehicle record remains uncertain and is not a binary label.
- The source video's timestamp table is authoritative for frame/time correspondence; `scripts/summarize_event_annotations.py` checks the recorded endpoints against it.
