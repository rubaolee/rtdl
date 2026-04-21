from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_sales_risk_screening
from examples import rtdl_v0_7_db_app_demo


BACKENDS = ("auto", "cpu_python_reference", "cpu_reference", "cpu", "embree", "optix", "vulkan")
SCENARIOS = ("regional_dashboard", "sales_risk", "all")


def _sales_backend(backend: str) -> str:
    if backend in {"auto", "cpu_reference"}:
        return "cpu_python_reference"
    return backend


def run_app(backend: str, scenario: str = "all") -> dict[str, Any]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")

    sections: dict[str, Any] = {}
    if scenario in {"regional_dashboard", "all"}:
        sections["regional_dashboard"] = rtdl_v0_7_db_app_demo.run_app(backend)
    if scenario in {"sales_risk", "all"}:
        sections["sales_risk"] = rtdl_sales_risk_screening.run_case(_sales_backend(backend))

    return {
        "app": "database_analytics",
        "requested_backend": backend,
        "scenario": scenario,
        "sections": sections,
        "data_flow": [
            "application-owned denormalized rows",
            "bounded RTDL DB kernels",
            "scan and grouped aggregate rows",
            "Python-owned dashboard or risk-summary JSON",
        ],
        "unifies": [
            "examples/rtdl_v0_7_db_app_demo.py",
            "examples/rtdl_sales_risk_screening.py",
        ],
        "honesty_boundary": "Unified app over bounded v0.7 DB kernels; not SQL, indexes, joins, transactions, query planning, or a DBMS.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Unified RTDL database analytics app over bounded v0.7 DB kernels."
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=BACKENDS,
    )
    parser.add_argument(
        "--scenario",
        default="all",
        choices=SCENARIOS,
        help="Run one DB app scenario or the complete unified app.",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, args.scenario), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
