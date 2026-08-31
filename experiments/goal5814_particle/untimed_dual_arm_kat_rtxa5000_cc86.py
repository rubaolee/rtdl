#!/usr/bin/env python3
"""Target-native untimed Goal5814 KAT entry point for the RTX A5000 build."""

from __future__ import annotations

from experiments.goal5814_particle import untimed_dual_arm_kat as _base


TARGET_EXECUTABLE_MANIFEST_BYTES = 6_316
TARGET_EXECUTABLE_MANIFEST_SHA256 = (
    "9b0f0bfb783df30a0799c6943b7623e797ccdc4e4d213fe5500be90db6093145")


def main(argv: list[str] | None = None) -> int:
    # The existing transaction keeps its reviewed CLI and execution sequence.
    # Only its source-frozen request-external manifest authority is rebound for
    # the duration of this single target process; it is never caller supplied.
    prior = (
        _base.FORMAL_EXECUTABLE_MANIFEST_BYTES,
        _base.FORMAL_EXECUTABLE_MANIFEST_SHA256,
    )
    _base.FORMAL_EXECUTABLE_MANIFEST_BYTES = TARGET_EXECUTABLE_MANIFEST_BYTES
    _base.FORMAL_EXECUTABLE_MANIFEST_SHA256 = TARGET_EXECUTABLE_MANIFEST_SHA256
    try:
        return _base.main_exact_core_boundary(argv)
    finally:
        (
            _base.FORMAL_EXECUTABLE_MANIFEST_BYTES,
            _base.FORMAL_EXECUTABLE_MANIFEST_SHA256,
        ) = prior


if __name__ == "__main__":
    raise SystemExit(main())
