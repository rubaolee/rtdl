from __future__ import annotations

import argparse
import json

from examples.benchmark_apps._support._repo_bootstrap import ensure_repo_src_on_path

ensure_repo_src_on_path()

from rtdsl._example_support.benchmark_harness_compat import run_archived_harness


def _payload() -> dict[str, object]:
    return {
        "status": "ok",
        "paper_entry": "RT-BarnesHut",
        "current_app": "examples/benchmark_apps/barnes_hut/v4_app.py",
        "learn_first": "examples/tutorial_programs/aggregate_frontier_rows.py",
        "scope_note": "examples/paper_reproduction/paper_reproduction_scope.md",
        "default_behavior": "explain_current_route",
        "run_harness": "python examples/paper_reproduction/rt_barneshut.py --run-harness -- --help",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Explain or run the RT-BarnesHut paper-oriented RTDL route.")
    parser.add_argument("--json", action="store_true", help="Print the route description as JSON.")
    parser.add_argument("--run-harness", action="store_true", help="Forward remaining arguments to the full benchmark runner.")
    parser.add_argument("harness_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.run_harness:
        return run_archived_harness("barnes_hut", args.harness_args)

    payload = _payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("RT-BarnesHut paper-oriented route")
        print(f"  current app: {payload['current_app']}")
        print(f"  learn first: {payload['learn_first']}")
        print(f"  scope note: {payload['scope_note']}")
        print(f"  full runner: {payload['run_harness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
