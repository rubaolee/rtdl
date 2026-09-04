#!/usr/bin/env python3
"""Build or verify the frozen Goal5843 preregistration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5843_post_r1_baseline.contracts import (
    PREREGISTRATION_PATH,
    build_preregistration,
)
from experiments.goal5843_post_r1_baseline.runtime import create_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / PREREGISTRATION_PATH


def _verify_predecessor(relative: str, expected: str) -> None:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if value.get("authority_sha256") != expected:
        raise RuntimeError(f"predecessor authority mismatch: {relative}")


def build() -> dict[str, object]:
    _verify_predecessor(
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "GOAL5842_FINAL_INTERNAL_AUTHORITY.json",
        "5c8044d9204df6b5d622142aecab8fcd25990e2ca1a19c7c5055ef4e16a31e43",
    )
    _verify_predecessor(
        "history/internal_docs/goal5842r1_public_reuse_scalar_fastpath_20260903/"
        "GOAL5842R1_INTERNAL_AUTHORITY.json",
        "7897058f51dedc3b6b5c652b5c3d69418610919557f9ee9a9c70214a5f184248",
    )
    return build_preregistration(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.verify_stored:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != value:
            raise RuntimeError("stored Goal5843 preregistration differs from rebuild")
    else:
        create_json(args.output, value)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
