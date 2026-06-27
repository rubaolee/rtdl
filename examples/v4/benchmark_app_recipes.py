from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rt


@dataclass(frozen=True)
class RecipeStep:
    name: str
    request: str
    partner: str
    why: str
    plan: rt.V4OperatorPlan


@dataclass(frozen=True)
class AppRecipe:
    app: str
    idea: str
    steps: tuple[RecipeStep, ...]


def choose_operator(name: str, request: str, partner: str, why: str) -> RecipeStep:
    """Choose a V4 operator the same way an application author would."""

    plan = rt.plan_operator_request_v4(request, partner=partner)
    return RecipeStep(name=name, request=request, partner=partner, why=why, plan=plan)


def build_rtdbscan_recipe() -> AppRecipe:
    neighbors = choose_operator(
        "Find radius neighbors",
        "fixed_radius",
        "torch",
        "RTDBSCAN first needs the local neighborhood relation for each point.",
    )
    components = choose_operator(
        "Merge density components",
        "component_union",
        "numba",
        "After the neighbor relation exists, the continuation merges connected components.",
    )
    return AppRecipe(
        app="RTDBSCAN",
        idea="Build a fixed-radius neighbor relation, then merge reachable dense components.",
        steps=(neighbors, components),
    )


def build_rtnn_recipe() -> AppRecipe:
    nearest = choose_operator(
        "Find nearest witness",
        "point_group_nearest",
        "torch",
        "The nearest-witness relation gives the candidate each query point should keep.",
    )
    ranked = choose_operator(
        "Summarize ranked candidates",
        "ranked_summary",
        "rtdl_native",
        "This route is intentionally deferred in V4.0, so the planner tells the user that.",
    )
    return AppRecipe(
        app="RTNN",
        idea="Ask for nearest witnesses, then summarize or rank the candidate set.",
        steps=(nearest, ranked),
    )


def build_triangle_counting_recipe() -> AppRecipe:
    hits = choose_operator(
        "Create hit flags",
        "any_hit",
        "torch",
        "Triangle counting lowers graph relations to compact ray/triangle hit decisions.",
    )
    grouped_counts = choose_operator(
        "Count hits by primitive group",
        "grouped_i64",
        "torch",
        "The grouped reduction keeps the summary compact instead of materializing every row.",
    )
    return AppRecipe(
        app="Triangle counting",
        idea="Turn graph structure into ray/triangle evidence, then reduce by group.",
        steps=(hits, grouped_counts),
    )


def build_robot_collision_recipe() -> AppRecipe:
    collision = choose_operator(
        "Check path-obstacle intersection",
        "any_hit",
        "torch",
        "Collision decisions are ray/triangle any-hit questions with app geometry around them.",
    )
    return AppRecipe(
        app="Robot collision",
        idea="Ask whether each motion segment hits an obstacle primitive.",
        steps=(collision,),
    )


def build_raydb_recipe() -> AppRecipe:
    hits = choose_operator(
        "Build hit relation",
        "any_hit",
        "torch",
        "RayDB-style queries start from a relation of rays that hit primitives.",
    )
    weighted = choose_operator(
        "Compute weighted summary",
        "weighted_sum",
        "torch",
        "Many query plans need a weighted aggregate over the hit relation.",
    )
    grouped = choose_operator(
        "Group device columns",
        "grouped_sum",
        "cupy",
        "CuPy is an explicit partner for grouped continuation when the user chooses it.",
    )
    return AppRecipe(
        app="RayDB-style",
        idea="Build hit rows, then choose a compact summary instead of pulling every row home.",
        steps=(hits, weighted, grouped),
    )


def build_librts_recipe() -> AppRecipe:
    aabb = choose_operator(
        "Run AABB index operations",
        "aabb_index_query",
        "rtdl_native",
        "The spatial index app asks point, box, and overlap questions against AABB data.",
    )
    return AppRecipe(
        app="LibRTS spatial index",
        idea="Use a prepared AABB-style index for spatial predicates.",
        steps=(aabb,),
    )


def build_contact_manifold_recipe() -> AppRecipe:
    broadphase = choose_operator(
        "Find broadphase candidates",
        "aabb_index_query",
        "rtdl_native",
        "Contact starts by finding candidate primitive pairs cheaply.",
    )
    closest = choose_operator(
        "Refine closest hit by group",
        "closest_hit_argmin",
        "torch",
        "The refinement keeps the closest witness per group for later contact logic.",
    )
    return AppRecipe(
        app="Contact manifold",
        idea="Separate candidate discovery from exact contact refinement.",
        steps=(broadphase, closest),
    )


def build_spatial_rayjoin_recipe() -> AppRecipe:
    candidates = choose_operator(
        "Find candidate shape pairs",
        "aabb_index_query",
        "rtdl_native",
        "The join begins with a broadphase relation over spatial bounds.",
    )
    hits = choose_operator(
        "Refine with ray/triangle hits",
        "any_hit",
        "torch",
        "A hit predicate can refine candidate pairs without changing the app-level join meaning.",
    )
    return AppRecipe(
        app="Spatial RayJoin",
        idea="Build candidate pairs, then refine the relation with RT predicates.",
        steps=(candidates, hits),
    )


def build_barnes_hut_recipe() -> AppRecipe:
    frontier = choose_operator(
        "Build aggregate frontier",
        "aggregate_frontier",
        "rtdl_native",
        "Barnes-Hut first decides which aggregate cells each body should use.",
    )
    grouped = choose_operator(
        "Apply weighted vector continuation",
        "grouped_sum",
        "cupy",
        "The continuation consumes the frontier with an explicit partner chosen by the user.",
    )
    return AppRecipe(
        app="Barnes-Hut",
        idea="Keep the aggregate frontier compact, then apply a weighted continuation.",
        steps=(frontier, grouped),
    )


def build_hausdorff_recipe() -> AppRecipe:
    threshold = choose_operator(
        "Ask threshold decision",
        "fixed_radius",
        "torch",
        "A threshold route answers whether a point set is within a distance bound.",
    )
    witness = choose_operator(
        "Ask exact nearest witness",
        "point_group_nearest",
        "torch",
        "The witness route returns richer exact nearest-neighbor evidence.",
    )
    return AppRecipe(
        app="Hausdorff XHD",
        idea="Choose between threshold decisions and exact nearest-witness evidence.",
        steps=(threshold, witness),
    )


def benchmark_app_recipes() -> tuple[AppRecipe, ...]:
    return (
        build_rtdbscan_recipe(),
        build_rtnn_recipe(),
        build_triangle_counting_recipe(),
        build_robot_collision_recipe(),
        build_raydb_recipe(),
        build_librts_recipe(),
        build_contact_manifold_recipe(),
        build_spatial_rayjoin_recipe(),
        build_barnes_hut_recipe(),
        build_hausdorff_recipe(),
    )


def render_recipe(recipe: AppRecipe) -> str:
    lines = [recipe.app, f"  idea: {recipe.idea}"]
    for index, step in enumerate(recipe.steps, 1):
        surface = step.plan.api_surface or "<no V4.0 release surface>"
        lines.extend(
            [
                f"  {index}. {step.name}",
                f"     request: {step.request}",
                f"     partner: {step.partner}",
                f"     status: {step.plan.status}",
                f"     surface: {surface}",
                f"     why: {step.why}",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    print("RTDL V4 benchmark app recipes")
    print("Use these as planner-level starting points before opening the full harness.\n")
    for recipe in benchmark_app_recipes():
        print(render_recipe(recipe))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
