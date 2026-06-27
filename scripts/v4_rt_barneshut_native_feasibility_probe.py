from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS,
    inspect_v4_rt_barneshut_native_feasibility,
    validate_v4_rt_barneshut_native_feasibility,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe V4 native RT-BarnesHut author-route feasibility."
    )
    parser.add_argument("--source-root", default=str(ROOT))
    parser.add_argument("--optix-lib", default=None)
    parser.add_argument("--goal", default="Goal4762")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    feasibility = inspect_v4_rt_barneshut_native_feasibility(args.source_root)
    validate_v4_rt_barneshut_native_feasibility(feasibility)
    payload = feasibility.as_dict()
    payload["goal"] = args.goal
    if feasibility.missing_native_author_symbols:
        payload["status_summary"] = (
            "native route unavailable; existing 2D aggregate-tree route is not author-equivalent"
        )
    elif feasibility.claim_boundary.get("native_v4_checksum_route_available"):
        payload["status_summary"] = (
            "native author-semantics ABI checksum route is available through a host fallback; "
            "RT-core/native-operator performance remains unauthorized"
        )
    else:
        payload["status_summary"] = "native symbols present but require runtime validation"
    if args.optix_lib:
        library = Path(args.optix_lib)
        export_check: dict[str, object] = {
            "library": str(library),
            "exists": library.exists(),
            "loaded": False,
            "exported_symbols": {},
            "missing_exported_symbols": list(V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS),
        }
        if library.exists():
            loaded = ctypes.CDLL(str(library))
            exported = {
                symbol: hasattr(loaded, symbol)
                for symbol in V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS
            }
            export_check.update(
                {
                    "loaded": True,
                    "exported_symbols": exported,
                    "missing_exported_symbols": [
                        symbol for symbol, present in exported.items() if not present
                    ],
                }
            )
        payload["native_library_export_check"] = export_check

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
