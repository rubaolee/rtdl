#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRELUDE_H = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
DEFAULT_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal870_native_pair_row_emitter_abi_packet_2026-04-23.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal870_native_pair_row_emitter_abi_packet_2026-04-23.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(prelude_h: str, api_cpp: str) -> dict[str, Any]:
    symbol = "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded"
    declaration_present = symbol in prelude_h
    definition_present = symbol in api_cpp
    contract_fields_present = all(
        needle in api_cpp
        for needle in (
            "size_t output_capacity",
            "size_t* emitted_count_out",
            "uint32_t* overflowed_out",
        )
    )
    explicit_not_implemented = "native bounded segment_polygon_anyhit_rows emitter is not implemented yet" in api_cpp
    public_rows_still_host_indexed = "run_seg_poly_anyhit_rows_optix_host_indexed(" in api_cpp
    return {
        "goal": "Goal870 native pair-row emitter ABI packet",
        "date": "2026-04-23",
        "symbol": symbol,
        "recommended_status": "abi_scaffold_added",
        "evidence": {
            "declaration_present": declaration_present,
            "definition_present": definition_present,
            "contract_fields_present": contract_fields_present,
            "explicit_not_implemented_error_present": explicit_not_implemented,
            "public_rows_path_still_host_indexed": public_rows_still_host_indexed,
        },
        "boundary": (
            "This goal adds only the bounded ABI scaffold for a future native pair-row emitter. "
            "The public rows path still uses the host-indexed helper, and no readiness promotion follows from this scaffold alone."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    ev = packet["evidence"]
    return "\n".join(
        [
            "# Goal870 Native Pair-Row Emitter ABI Packet",
            "",
            f"- symbol: `{packet['symbol']}`",
            f"- recommended status: `{packet['recommended_status']}`",
            "",
            "## Evidence",
            "",
            f"- declaration present: `{ev['declaration_present']}`",
            f"- definition present: `{ev['definition_present']}`",
            f"- contract fields present: `{ev['contract_fields_present']}`",
            f"- explicit not-implemented error present: `{ev['explicit_not_implemented_error_present']}`",
            f"- public rows path still host-indexed: `{ev['public_rows_path_still_host_indexed']}`",
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a packet proving the native pair-row emitter ABI scaffold exists.")
    parser.add_argument("--prelude-h", type=Path, default=DEFAULT_PRELUDE_H)
    parser.add_argument("--api-cpp", type=Path, default=DEFAULT_API_CPP)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    packet = build_packet(_read_text(args.prelude_h), _read_text(args.api_cpp))
    packet["sources"] = {"prelude_h": str(args.prelude_h), "api_cpp": str(args.api_cpp)}
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "recommended_status": packet["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
