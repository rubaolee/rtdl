from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    catalog_rows = []
    for row in rtdl_v4.measured_operator_catalog_v4():
        catalog_rows.append(
            {
                "operator_surface": row["api_surface"],
                "generic_primitive": row["generic_primitive"],
                "continuation_class": row["continuation_class"],
                "partners": row["measured_partners"],
            }
        )
    payload = {
        "status": "ok",
        "concept": "a V4 operator request maps to a generic primitive, partner scope, and continuation class",
        "catalog_rows": catalog_rows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
