#!/usr/bin/env python3
"""Validate structural and evidence invariants in CH58x register specs."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "spec"
EVIDENCE = {
    "documented",
    "source-correlated",
    "binary-observed",
    "hardware-observed",
    "inferred",
}
ACCESS = {"read-only", "write-only", "read-write", "write-one-to-clear"}


def fail(path: Path, message: str) -> None:
    raise ValueError(f"{path.relative_to(ROOT)}: {message}")


def validate(path: Path) -> None:
    block = json.loads(path.read_text())
    required = {
        "schema_version",
        "name",
        "chips",
        "base_address",
        "description",
        "sources",
        "registers",
    }
    missing = required - block.keys()
    if missing:
        fail(path, f"missing keys: {sorted(missing)}")
    if block["schema_version"] != "1.0":
        fail(path, "schema_version must be 1.0")
    int(block["base_address"], 16)

    source_ids = {source["id"] for source in block["sources"]}
    if len(source_ids) != len(block["sources"]):
        fail(path, "duplicate source id")

    occupied: set[tuple[int, int]] = set()
    names: set[str] = set()
    registers = list(block["registers"])
    for array in block.get("register_arrays", []):
        if "{n}" not in array["name"]:
            fail(path, f"register array {array['name']}: missing {{n}} placeholder")
        for index in range(array["count"]):
            registers.append(
                {
                    **array,
                    "name": array["name"].replace("{n}", str(index)),
                    "offset": array["offset"] + index * array["stride"],
                }
            )

    for register in registers:
        name = register["name"]
        width = register["width"]
        offset = register["offset"]
        if name in names:
            fail(path, f"duplicate register name {name}")
        names.add(name)
        if width not in {8, 16, 32}:
            fail(path, f"{name}: invalid width {width}")
        if offset % (width // 8):
            fail(path, f"{name}: offset is not naturally aligned")
        span = (offset, width // 8)
        if span in occupied:
            fail(path, f"{name}: duplicate register span {span}")
        occupied.add(span)
        if register["access"] not in ACCESS:
            fail(path, f"{name}: invalid access")
        if register["evidence"] not in EVIDENCE:
            fail(path, f"{name}: invalid evidence label")
        unknown_sources = set(register["sources"]) - source_ids
        if unknown_sources:
            fail(path, f"{name}: unknown sources {sorted(unknown_sources)}")

        used_bits = 0
        for field in register.get("fields", []):
            if field["evidence"] not in EVIDENCE:
                fail(path, f"{name}.{field['name']}: invalid evidence label")
            end = field["lsb"] + field["width"]
            if end > width:
                fail(path, f"{name}.{field['name']}: exceeds register width")
            mask = ((1 << field["width"]) - 1) << field["lsb"]
            if used_bits & mask:
                fail(path, f"{name}.{field['name']}: overlaps another field")
            used_bits |= mask


def main() -> int:
    paths = sorted(SPEC_DIR.glob("*.json"))
    for path in paths:
        validate(path)
    print(f"validated {len(paths)} register block(s)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
