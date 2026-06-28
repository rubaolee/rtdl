from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


REQUESTS = (
    ("fixed_radius", ("torch", "cupy")),
    ("grouped_sum", ("cupy", "torch")),
    ("component_union", ("numba", "torch")),
    ("aabb_index_query", ("rtdl_native", "cupy")),
    ("custom_predicate_early_exit", ("numba", "torch")),
)


def main() -> int:
    rows = []
    for operator, partners in REQUESTS:
        for partner in partners:
            kwargs = {}
            if operator == "custom_predicate_early_exit" and partner == "numba":
                kwargs = {
                    "callback_shape": "pure_boolean_numba_cabi_device_function",
                    "numba_device_function": True,
                }
            plan = rtdl_v4.plan_operator_request_v4(operator, partner=partner, **kwargs)
            rows.append(
                {
                    "operator": operator,
                    "partner": partner,
                    "status": plan.status,
                    "surface": plan.api_surface,
                    "generic_primitive": plan.generic_primitive,
                }
            )

    payload = {
        "status": "ok",
        "concept": "partner choice is explicit; unsupported or unmeasured combinations are visible at planning time",
        "rows": rows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
