"""Extract only the selected DOT camera videos and matching timestamp CSVs.

The original archive is preserved. Extracted source media stays under the
Git-ignored data/raw/selected-validation directory.
"""

from __future__ import annotations

import csv
import pathlib
import tempfile
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "raw" / "validation-full.zip"
MANIFEST = ROOT / "data" / "manifests" / "compact-subset.csv"
OUTPUT = ROOT / "data" / "raw" / "selected-validation"
CHUNK_SIZE = 8 * 1024 * 1024


def find_member(archive: zipfile.ZipFile, filename: str) -> zipfile.ZipInfo:
    matches = [
        info for info in archive.infolist()
        if pathlib.PurePosixPath(info.filename).name == filename
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one archive member named {filename!r}; found {len(matches)}")
    return matches[0]


def extract_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo, destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: pathlib.Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=f".{destination.name}.", suffix=".part", delete=False
        ) as temporary:
            temporary_path = pathlib.Path(temporary.name)
            copied = 0
            with archive.open(info) as source:
                while chunk := source.read(CHUNK_SIZE):
                    temporary.write(chunk)
                    copied += len(chunk)
        if copied != info.file_size:
            raise IOError(f"Extracted byte count mismatch for {info.filename}: {copied} != {info.file_size}")
        temporary_path.replace(destination)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def main() -> None:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(f"Missing source archive: {ARCHIVE}")
    if not MANIFEST.is_file():
        raise FileNotFoundError(f"Missing subset manifest: {MANIFEST}; build it first")

    with MANIFEST.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 10:
        raise ValueError(f"Expected the reviewed 10-run subset manifest, found {len(rows)} rows")
    run_ids = [row["source_run_id"] for row in rows]
    if len(set(run_ids)) != len(run_ids):
        raise ValueError("Subset manifest contains duplicate source run IDs")

    members: list[tuple[zipfile.ZipInfo, pathlib.Path]] = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in rows:
            run_id = row["source_run_id"]
            run_dir = OUTPUT / run_id
            video = find_member(archive, pathlib.PurePosixPath(row["source_video_path"]).name)
            timing = find_member(archive, pathlib.PurePosixPath(row["timestamp_csv_path"]).name)
            expected_video_bytes = int(row["video_uncompressed_bytes"])
            if video.file_size != expected_video_bytes:
                raise ValueError(f"Video size changed for {run_id}: {video.file_size} != {expected_video_bytes}")
            members.extend([
                (video, run_dir / pathlib.PurePosixPath(video.filename).name),
                (timing, run_dir / pathlib.PurePosixPath(timing.filename).name),
            ])

        for index, (info, destination) in enumerate(members, start=1):
            extract_member(archive, info, destination)
            print(f"Extracted {index}/{len(members)}: {destination.relative_to(ROOT)} ({info.file_size:,} bytes)")

    print(f"Done. Extracted {len(rows)} complete video/timestamp pairs to {OUTPUT.relative_to(ROOT)}.")
    print("The ZIP archive is unchanged; extracted source files are Git-ignored.")


if __name__ == "__main__":
    main()
