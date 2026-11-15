# LiveCross — Inspection Gallery

**Purpose:** Let a reviewer inspect representative, timestamped frames from each source run in the frozen DOT split without manually opening the large ZIP archives.

## Rebuild the local gallery

From the repository root, with the downloaded archives, `data/manifests/splits.csv`, OpenCV, and NumPy available, run:

```powershell
python scripts/build_inspection_gallery.py
```

Open `data/processed/inspection-gallery/index.html`. The local page links to one contact sheet per split, the 305-row frame manifest, and a JSON audit. It includes five frames at 10%, 30%, 50%, 70%, and 90% of every complete source run: 16 train, 4 development, and 41 held-out test runs. The script uses the same timestamp row as the sampled video frame, records the source timestamp verbatim, and checks that frame counts match timestamp rows.

## Read the labels correctly

- Test-sheet `conflict` and `no conflict` are DOT **run-level** source labels. They are not frame labels, event intervals, or actor-pair judgments. Each row is explicitly marked “run-level only.”
- Training and development clips come from unlabeled DOT training samples. They are shown as unlabeled.
- Event-level conflict/non-conflict, difficult/occluded, uncertain, and actor-track annotations are not present in the current source records. The gallery does not invent these labels; its manifest marks the frame samples as context only. Add event-specific examples after the manual annotation task, using the frozen run split.
- A DOT 3D-box projection was not approved as RGB ground truth for this selected view, so the gallery does not draw boxes or tracks.

The 10-run compact subset appears within the test contact sheet. The contact sheets and frame crops remain under Git-ignored `data/processed/inspection-gallery/` because they are derived source imagery; review dataset terms and privacy before sharing them. The generator, instructions, and split-aware metadata are tracked in the repository.
