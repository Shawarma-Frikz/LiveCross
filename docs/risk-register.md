# LiveCross — Risk and Ethics Register

**Version:** 2.0 (Refined Scope: 2 Core Interaction Types)
**Purpose:** Keep the project useful for safety review while being honest about evidence, privacy, and prototype limits. Owners are accountable project roles; one person holds all roles in a solo project.

## Risk register

| ID | Risk | Likelihood / impact | Owner | Prevention and response |
|---|---|---|---|---|
| R1 | A potential-conflict flag is mistaken for proof that a crash will happen, or a missed flag is treated as proof that a scene is safe. | Medium / High | Project lead | Label outputs “candidate for review”; state that this is not a certified warning system; keep a human reviewer in the loop; show uncertainty and document false positives/negatives. Never trigger a vehicle, traffic signal, or emergency response. |
| R2 | Video reveals a person’s face, license plate, or other identifying detail. | Medium / High | Data steward + demo lead | Do not identify or track identity across sessions. Keep raw footage local and out of Git/cloud storage. Use only data permitted for the project. Obtain consent for staged webcam participants; blur identifying details before sharing screenshots or clips. |
| R3 | Dataset terms, attribution, or redistribution limits are misunderstood. | Medium / High | Data steward | Read terms and metadata before use; cite sources and record access dates. Waterloo's publisher page provides no explicit reuse license, so it is strictly excluded from core public project data pending confirmed terms. Respect ROCO's CC BY-SA 4.0 terms. Do not commit or redistribute raw archives. |
| R4 | Model behavior does not generalize beyond the controlled camera, actor pairs, and sampled conditions. | High / High | Evaluation lead | Describe the DOT scene accurately: one controlled U.S. intersection, scripted vulnerable-road-user/vehicle scenarios, multiple sensors, and limited runs. Scope is strictly bounded to pedestrian–vehicle and vehicle–vehicle interactions; pedestrian–pedestrian and fixed-obstacle types are explicitly out of scope due to verified external dataset gaps (JRDB, DoTA). |
| R5 | False alarms or missed events arise from occlusion, lighting, detector misses, or track-ID switches. | High / High | Perception lead | Add an “uncertain—review” state when evidence is weak; record track quality; evaluate event precision/recall and false alerts per video duration; inspect and report failures. Do not force uncertain examples into the safe class. |
| R6 | Run-level source labels are mistaken for event start/end annotations, or manually labeled events leak into evaluation. | Medium / High | Data steward + evaluation lead | Keep raw source labels separate from LiveCross labels. Preserve the ROCO local CSV parsing caveat and source schema. Add event intervals only with provenance and reviewer notes; assistant first-pass labels require student adjudication before training or primary metrics. Split by complete run before tuning; use training runs for hard-negative mining; keep test event labels sealed from model/threshold selection. |
| R7 | Live camera demonstration films people who did not agree to participate or creates a real traffic hazard. | Low / High | Demo lead | Stage the demonstration indoors or in a controlled private area with consenting participants and toy/controlled vehicle motion. Do not test beside active traffic or place anyone in danger. Provide a clear stop control and replay fallback. |
| R8 | The browser demo stores or exposes raw footage, event clips, or credentials unexpectedly. | Low / High | Demo lead | Process locally for the course MVP; store only necessary event metadata by default; keep data/model paths and secrets out of the repository; add raw data and generated video to `.gitignore`; inspect repository contents before publishing. |
| R9 | Dataset coverage or model speed is insufficient, causing pressure to weaken evaluation or overstate live performance. | Medium / Medium | Project lead + implementation lead | The 10-run compact validation subset is held out in test. Acknowledge that student-adjudicated event ground truth is still pending and currently exploratory. Retain clip replay as the presentation fallback. Report actual FPS, hardware, and data coverage. Do not change frozen acceptance targets after viewing test results. |

## Ethical and product guardrails

- LiveCross supports **human review of video**. It does not issue safety commands or replace a qualified safety assessment.
- The system reasons about tracked motion and configured zones only. It does not infer intent, identity, fault, age, or other personal traits.
- A conflict score is evidence for review, not a probability of injury unless separately calibrated and validated—which is outside this project.
- Show an explicit uncertain state when the camera view, labels, or tracks do not support a reliable conclusion.
- Limit demo footage to the agreed purpose and audience; remove or blur identifying details before public sharing.
- Discuss the dataset’s controlled setting and limited sample size when presenting results.

## Role ownership

- **Project lead:** scope, instructor approval, claims, and final risk review.
- **Data steward:** dataset terms, annotation provenance, privacy handling, and split records.
- **Perception lead:** detector/tracker limitations and uncertainty handling.
- **Evaluation lead:** metric definitions, leakage prevention, and failure analysis.
- **Demo lead:** webcam consent, local storage, access controls, and replay fallback.

Revisit this register when the dataset is selected, when webcam input is added, and before sharing a public demo or repository release.
