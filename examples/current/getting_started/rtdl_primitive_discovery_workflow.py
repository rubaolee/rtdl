from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def run_workflow() -> dict[str, object]:
    primitive_matches = rt.find_primitive(
        intent="nearest",
        shape="fixed_radius",
        dim="3d",
        output="grouped",
    )
    recipe_matches = rt.find_recipe(
        intent="nearest",
        shape="fixed_radius",
        dim="3d",
        output="grouped",
    )
    plans = rt.plan_continuation(
        intent="nearest",
        shape="fixed_radius",
        dim="3d",
        output="grouped",
        partner="numba",
    )

    if not primitive_matches or not recipe_matches or not plans:
        raise SystemExit("primitive discovery workflow returned no matches")

    plan = plans[0]
    return {
        "app": "primitive_discovery_workflow",
        "status": "metadata_preview",
        "primitive_match": {
            "id": primitive_matches[0].node_id,
            "title": primitive_matches[0].title,
            "status": primitive_matches[0].status,
            "matched_on": primitive_matches[0].matched_on,
        },
        "recipe_match": {
            "id": recipe_matches[0].recipe_id,
            "title": recipe_matches[0].title,
            "status": recipe_matches[0].status,
            "primitive_ids": recipe_matches[0].primitive_ids,
        },
        "advisory_plan": {
            "recipe_id": plan.recipe_id,
            "recommendation": plan.recommendation,
            "selected_partner": plan.selected_partner,
            "executes": plan.executes,
            "automatic_partner_selection_allowed": plan.automatic_partner_selection_allowed,
            "non_stable_step_ids": plan.non_stable_step_ids,
            "primitive_steps": tuple(
                {
                    "primitive_id": step.primitive_id,
                    "primitive_status": step.primitive_status,
                    "phase": step.phase,
                    "role": step.role,
                    "partner_ops": step.partner_ops,
                }
                for step in plan.primitive_steps
            ),
            "partner_options": tuple(
                {
                    "operation": option.operation,
                    "partner": option.partner,
                    "status": option.status,
                    "supported": option.supported,
                }
                for option in plan.partner_options
            ),
            "warnings": plan.warnings,
        },
        "note": "This preview shows how RTDL describes a primitive before you run a backend.",
    }


def summarize_workflow(payload: dict[str, object]) -> dict[str, object]:
    primitive = payload["primitive_match"]
    recipe = payload["recipe_match"]
    plan = payload["advisory_plan"]
    assert isinstance(primitive, dict)
    assert isinstance(recipe, dict)
    assert isinstance(plan, dict)
    return {
        "app": payload["app"],
        "mode": "metadata preview",
        "primitive": primitive["title"],
        "recipe": recipe["title"],
        "recommendation": plan["recommendation"],
        "next_step": "choose an explicit backend and partner when you are ready to execute the route",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview RTDL primitive and recipe metadata.")
    parser.add_argument("--json", action="store_true", help="Print the full metadata payload.")
    args = parser.parse_args(argv)
    payload = run_workflow()
    output = payload if args.json else summarize_workflow(payload)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
