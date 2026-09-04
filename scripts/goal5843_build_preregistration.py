#!/usr/bin/env python3
"""Build or verify the frozen Goal5843 preregistration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5843_post_r1_baseline.contracts import (
    PREREGISTRATION_PATH,
    build_preregistration,
    sha256_file,
)
from experiments.goal5843_post_r1_baseline.runtime import create_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / PREREGISTRATION_PATH
EVIDENCE = ROOT / "history/internal_docs/goal5843_post_r1_fair_baseline_20260904"


def _verify_v3_terminal_evidence() -> None:
    preregistration = EVIDENCE / "PREREGISTRATION_V3.json"
    archive = (
        EVIDENCE
        / "FORMAL_TRANSACTION_V3_TERMINAL_ARCHIVE_VERIFIER_FAILURE.tar.gz"
    )
    if sha256_file(preregistration) != (
        "af04ea3df90b00e2639d24d9d2ec9bee30aa21f98b7cbda9183050191c2182eb"
    ):
        raise RuntimeError("Goal5843 v3 preregistration custody mismatch")
    value = json.loads(preregistration.read_text(encoding="utf-8"))
    if value.get("preregistration_sha256") != (
        "90c0e00f372df6fb9ba2985c80b43fe17b3ad00be60471f8f67d398ba1dc6b9a"
    ):
        raise RuntimeError("Goal5843 v3 preregistration seal mismatch")
    if sha256_file(archive) != (
        "bf24cc9954e9f6970ea58ff6584f79bf1de32b2e5118003a06723cb8ba61f118"
    ):
        raise RuntimeError("Goal5843 v3 terminal archive custody mismatch")


def _verify_predecessor(relative: str, expected: str) -> None:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if value.get("authority_sha256") != expected:
        raise RuntimeError(f"predecessor authority mismatch: {relative}")


def build() -> dict[str, object]:
    _verify_v3_terminal_evidence()
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
