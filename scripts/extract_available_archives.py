"""Safely extract every downloaded ZIP under the ignored raw-data directory.

Existing complete DOT training-sample extractions at data/raw/Run_*/ are
reused. Other archives are extracted into source-specific subdirectories so
similarly named files from different datasets cannot overwrite one another.
Reading each member to EOF makes zipfile verify its CRC before it is accepted.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import stat
import zipfile
import zlib
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results" / "audits" / "raw-archive-extraction.json"
CHUNK = 8 * 1024 * 1024


def archive_destination(archive: pathlib.Path) -> pathlib.Path:
    relative_parent = archive.parent.relative_to(RAW)
    return RAW / "extracted" / relative_parent / archive.stem


def is_safe_member(member: str) -> pathlib.PurePosixPath:
    path = pathlib.PurePosixPath(member)
    if "\\" in member or "\x00" in member:
        raise ValueError(f"Unsafe archive member path: {member!r}")
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"Unsafe archive member path: {member!r}")
    if path.parts and ":" in path.parts[0]:
        raise ValueError(f"Drive-qualified archive member path: {member!r}")
    return path


def crc32_file(path: pathlib.Path) -> int:
    checksum = 0
    with path.open("rb") as stream:
        while block := stream.read(CHUNK):
            checksum = zlib.crc32(block, checksum)
    return checksum & 0xFFFFFFFF


def existing_training_sample_is_complete(archive: pathlib.Path, infos: list[zipfile.ZipInfo]) -> bool:
    if archive.parent != RAW or not archive.name.startswith("training-sample-"):
        return False
    for info in infos:
        if info.is_dir():
            continue
        member = is_safe_member(info.filename)
        target = RAW.joinpath(*member.parts)
        if (
            not target.is_file()
            or target.stat().st_size != info.file_size
            or crc32_file(target) != info.CRC
        ):
            return False
    return True


def extract_archive(archive: pathlib.Path) -> dict[str, object]:
    with zipfile.ZipFile(archive) as zipped:
        infos = zipped.infolist()
        total_size = sum(info.file_size for info in infos if not info.is_dir())
        destination = archive_destination(archive)
        existing_complete = existing_training_sample_is_complete(archive, infos)
        if existing_complete:
            return {
                "archive": archive.relative_to(ROOT).as_posix(),
                "archive_bytes": archive.stat().st_size,
                "members": len(infos),
                "expanded_bytes": total_size,
                "destination": "data/raw/Run_* (pre-existing complete extraction)",
                "action": "reused_existing_extraction",
                "files_crc_verified": sum(1 for info in infos if not info.is_dir()),
                "crc_verified": True,
            }

        drive = shutil.disk_usage(RAW)
        needed = total_size
        if destination.exists():
            # A previous interrupted extraction may be resumed. Count only
            # members whose exact-size file is not already present.
            needed = 0
            for info in infos:
                if info.is_dir():
                    continue
                member = is_safe_member(info.filename)
                target = destination.joinpath(*member.parts)
                if not target.is_file() or target.stat().st_size != info.file_size:
                    needed += info.file_size
        if drive.free < needed + 2 * 1024**3:
            raise OSError(
                f"Insufficient free space for {archive.name}: need about "
                f"{needed:,} additional bytes plus 2 GiB safety margin; "
                f"have {drive.free:,} bytes"
            )

        destination.mkdir(parents=True, exist_ok=True)
        written = 0
        accepted = 0
        next_progress = 512 * 1024**2
        for info in infos:
            if info.is_dir():
                continue
            member = is_safe_member(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise ValueError(f"Refusing symlink in archive: {archive.name}:{info.filename}")
            target = destination.joinpath(*member.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if (
                target.is_file()
                and target.stat().st_size == info.file_size
                and crc32_file(target) == info.CRC
            ):
                accepted += 1
                written += info.file_size
                continue
            temporary = target.with_name(target.name + ".livecross-extracting")
            try:
                if temporary.exists():
                    temporary.unlink()
                with zipped.open(info, "r") as source, temporary.open("wb") as output:
                    while True:
                        block = source.read(CHUNK)
                        if not block:
                            break
                        output.write(block)
                        written += len(block)
                        if written >= next_progress:
                            print(
                                f"  {archive.name}: {written / 1024**3:.2f} / "
                                f"{total_size / 1024**3:.2f} GiB extracted",
                                flush=True,
                            )
                            next_progress += 512 * 1024**2
                if temporary.stat().st_size != info.file_size:
                    raise OSError(f"Size mismatch after extracting {info.filename}")
                os.replace(temporary, target)
                accepted += 1
            finally:
                if temporary.exists():
                    temporary.unlink()
        return {
            "archive": archive.relative_to(ROOT).as_posix(),
            "archive_bytes": archive.stat().st_size,
            "members": len(infos),
            "expanded_bytes": total_size,
            "destination": destination.relative_to(ROOT).as_posix(),
            "action": "extracted_or_resumed",
            "files_crc_verified": accepted,
            "crc_verified": True,
        }


def main() -> None:
    archives = sorted(RAW.rglob("*.zip"))
    if not archives:
        raise FileNotFoundError(f"No ZIP archives found under {RAW}")
    inventory = []
    for archive in archives:
        print(f"Processing {archive.relative_to(ROOT).as_posix()} ...", flush=True)
        record = extract_archive(archive)
        inventory.append(record)
        print(
            f"  {record['action']}: {record['expanded_bytes']:,} expanded bytes; "
            f"destination={record['destination']}",
            flush=True,
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "archives_found": len(archives),
        "all_archives_crc_verified": all(row["crc_verified"] for row in inventory),
        "total_expanded_bytes": sum(int(row["expanded_bytes"]) for row in inventory),
        "archives": inventory,
        "limitations": [
            "This covers ZIP archives already present locally; the separately described 1,104-run DOT full training archive (~1 TB) is not downloaded.",
            "Extraction does not make a dataset permitted for redistribution or suitable for LiveCross labels.",
            "No extracted test footage is annotated or used for model/threshold decisions.",
        ],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
