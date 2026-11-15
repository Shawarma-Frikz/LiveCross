# Compact subset selection

**Status:** Selected and assigned to the held-out test partition; event annotations are pending.
**Source:** DOT Intersection Safety Challenge Stage 1B full validation archive, 41 complete source runs.

## Selection decision

Use a compact, source-label-balanced candidate pool of **10 complete runs** from the downloaded DOT validation archive, reading only the full `VisualCamera7` video and its paired timestamp CSV for each run. These 10 runs are assigned to the held-out test partition in [`data/manifests/splits.csv`](../data/manifests/splits.csv); do not use them for model training, threshold tuning, or hard-negative mining.

The selected view is a consistent fixed roadside view across these runs: all 10 VisualCamera7 MP4s are 1280×720 and report 30 FPS. Each camera stream is retained in full; no temporal crop or adjacent-frame split is made. Midpoint frames were reviewed to check that the scene remains visible and to stratify daylight/low-light examples. Their exact frame index and verbatim source timestamp are saved in the manifest so the visual judgment can be repeated. The timestamp CSV does not specify a timezone; the manifest does not assign one. The light assessment is a qualitative description of one reviewed midpoint per run, not a source annotation or a claim about the whole recording.

| DOT source label (run-level) | Selected complete runs | Midpoint appearance | Run count | Total supplied-timestamp span |
|---|---|---|---:|---:|
| `conflict` | Run_1290, Run_359, Run_315, Run_1023, Run_856 | 3 daylight, 2 low-light | 5 | 236.583 s |
| `no conflict` | Run_179, Run_761, Run_410, Run_48, Run_965 | 3 daylight, 2 low-light | 5 | 204.840 s |
| **Total** | **10 complete camera sequences** | **6 daylight, 4 low-light** | **10** | **441.422 s (about 7 min 21 s)** |

The selected VisualCamera7 MP4 payloads total **344,268,302 bytes** (about 328.4 MiB uncompressed). The source ZIP itself is 28,642,566,098 bytes. The source-pool label balance is 12 conflict / 29 no-conflict runs; the selected 5/5 balance is deliberate for a compact pilot and is **not representative of the full validation prevalence**.

## What the labels mean here

`conflict` and `no conflict` in this manifest are the DOT's **run/scenario-level labels**. They do not identify event start/end times, actor pairs, or a per-camera event label. In particular:

- Do not copy a run label onto every frame or detected pair in its video.
- Do not claim that these 10 runs already contain five types of labeled interaction. DOT source labels cover its documented VRU–vehicle scenarios only.
- The selected pool is a source-video candidate set for later manual event review. Event-level model training and metrics remain blocked until those human labels are created using [`manual-annotation-protocol.md`](manual-annotation-protocol.md).
- The prior calibration audit did not approve the projected DOT 3D boxes as RGB ground truth for the selected camera/run. Use reviewed 2D event annotations for image-space evaluation unless a new overlay is independently validated.
- The balanced subset and visual light strata were selected intentionally; report their sampling design and do not use them to estimate natural conflict prevalence or generalize across all DOT runs.

## Reproducible inventory

The row-level manifest is [`data/manifests/compact-subset.csv`](../data/manifests/compact-subset.csv); the aggregate machine-readable report is [`results/audits/compact-subset-audit.json`](../results/audits/compact-subset-audit.json). Recreate both from the repository root:

```powershell
python scripts/build_compact_subset_manifest.py
```

The manifest builder reads the existing `data/raw/validation-full.zip`, verifies the 41-run source-label inventory, selected-run label values, presence of VisualCamera7 video/timestamp pairs, video metadata and midpoint decodability, monotonic timestamps, and frame-count/timestamp-row equality. It writes metadata only; it does not annotate events or create the global train/development/test split. When `data/manifests/splits.csv` exists, it records each selected run's assigned split. After regenerating the global split, run the builder once more to synchronize that column.

The selected 10 complete MP4/timestamp pairs are now extracted locally under `data/raw/selected-validation/<Run_ID>/` for review and annotation. Recreate that ignored local copy with `python scripts/extract_compact_subset.py`. The script extracts only those 20 archive members, checks the source video sizes against the manifest, and reads each selected member fully so ZIP CRC errors are detected. It does not alter or expand the source archive, annotate events, or assign splits. The extracted source video payload is 344,268,302 bytes (about 328.4 MiB), plus the timestamp CSVs.

The global sequence split is in [`data/manifests/splits.csv`](../data/manifests/splits.csv), with its reproducible policy and source counts in [`results/audits/sequence-split-audit.json`](../results/audits/sequence-split-audit.json). The remaining data action is to create project-reviewed event annotations; the DOT run labels are not event labels.
