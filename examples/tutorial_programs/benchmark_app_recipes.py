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
    input_shape: str
    call_pattern: str
    why: str
    plan: rt.V4OperatorPlan


@dataclass(frozen=True)
class AppRecipe:
    app: str
    idea: str
    steps: tuple[RecipeStep, ...]


def choose_operator(
    name: str,
    request: str,
    partner: str,
    input_shape: str,
    call_pattern: str,
    why: str,
) -> RecipeStep:
    """Choose a V4 operator the same way an application author would."""

    plan = rt.plan_operator_request_v4(request, partner=partner)
    return RecipeStep(
        name=name,
        request=request,
        partner=partner,
        input_shape=input_shape,
        call_pattern=call_pattern,
        why=why,
        plan=plan,
    )


def build_rtdbscan_recipe() -> AppRecipe:
    neighbors = choose_operator(
        "Find radius neighbors",
        "fixed_radius",
        "torch",
        "points: float32[n, 2], radius: float",
        "prepare_fixed_radius_count_threshold_2d_device_arrays_v4(...)",
        "RTDBSCAN first needs the local neighborhood relation for each point.",
    )
    components = choose_operator(
        "Merge density components",
        "component_union",
        "numba",
        "edge lists or neighbor columns from the radius pass",
        "v4_fixed_radius_graph_component_union_3d_device_arrays",
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
        "query points and grouped reference points: float32[n, 2]",
        "prepare_point_group_nearest_witness_2d_device_arrays_v4(...)",
        "The nearest-witness relation gives the candidate each query point should keep.",
    )
    ranked = choose_operator(
        "Summarize ranked candidates",
        "ranked_summary",
        "rtdl_native",
        "candidate scores per query group",
        "run_fixed_radius_ranked_summary_3d_prepared_runner_v4(...)",
        "The planner returns the current bounded status for this route.",
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
        "rays: float32[m, 2], triangles: float32[t, 3, 2]",
        "prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(...)",
        "Triangle counting lowers graph relations to compact ray/triangle hit decisions.",
    )
    grouped_counts = choose_operator(
        "Count hits by primitive group",
        "grouped_i64",
        "torch",
        "primitive ids and group ids from the hit pass",
        "prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4(...)",
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
        "motion segments as rays, obstacles as triangle primitives",
        "prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(...)",
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
        "ray table and primitive table columns",
        "prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(...)",
        "RayDB-style queries start from a relation of rays that hit primitives.",
    )
    weighted = choose_operator(
        "Compute weighted summary",
        "weighted_sum",
        "torch",
        "hit relation plus per-primitive or per-row weights",
        "prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4(...)",
        "Many query plans need a weighted aggregate over the hit relation.",
    )
    grouped = choose_operator(
        "Group device columns",
        "grouped_sum",
        "cupy",
        "row offsets plus value columns already on the device",
        "prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')",
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
        "AABB min/max columns and query boxes or points",
        "prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4(...)",
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
        "candidate AABB columns for shape pairs",
        "prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4(...)",
        "Contact starts by finding candidate primitive pairs cheaply.",
    )
    closest = choose_operator(
        "Refine closest hit by group",
        "closest_hit_argmin",
        "torch",
        "candidate ray/primitive groups with distances",
        "prepare_closest_hit_grouped_argmin_3d_device_arrays_v4(...)",
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
        "left/right AABB relation columns",
        "prepare_shape_pair_relation_active_count_2d_prepared_left_executor_v4(...)",
        "The join begins with a broadphase relation over spatial bounds.",
    )
    hits = choose_operator(
        "Refine with ray/triangle hits",
        "any_hit",
        "torch",
        "candidate rows lowered to ray/triangle predicates",
        "prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(...)",
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
        "body positions and aggregate cell columns",
        "prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4(...)",
        "Barnes-Hut first decides which aggregate cells each body should use.",
    )
    grouped = choose_operator(
        "Apply weighted vector continuation",
        "grouped_sum",
        "cupy",
        "frontier row offsets plus cell mass/vector columns",
        "prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')",
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
        "two point sets and a threshold radius",
        "prepare_fixed_radius_count_threshold_2d_device_arrays_v4(...)",
        "A threshold route answers whether a point set is within a distance bound.",
    )
    witness = choose_operator(
        "Ask exact nearest witness",
        "point_group_nearest",
        "torch",
        "query points, candidate points, and group offsets",
        "prepare_point_group_nearest_witness_2d_device_arrays_v4(...)",
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
                f"     input: {step.input_shape}",
                f"     call: {step.call_pattern}",
                f"     status: {step.plan.status}",
                f"     surface: {surface}",
                f"     why: {step.why}",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    print("RTDL V4 benchmark app recipes")
    print("Use these as planner-level starting points before opening the full app source.\n")
    for recipe in benchmark_app_recipes():
        print(render_recipe(recipe))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
