from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = ROOT / "examples" / "tutorial_programs"


KERNEL_FIRST_FILES = {
    "aabb_spatial_index_predicates.py",
    "bounded_witness_collection.py",
    "component_union_from_radius.py",
    "continuation_grouped_sum.py",
    "fixed_radius_neighbors.py",
    "hello_world.py",
    "nearest_neighbor.py",
    "point_in_polygon.py",
    "ray_triangle_hits.py",
    "sorting_rows.py",
    "spatial_join_lsi.py",
}

RELATION_FIRST_FILES = {
    "aggregate_frontier_rows.py",
    "contact_manifold_lowering.py",
    "hausdorff_distance_recipe.py",
    "measure_phases.py",
    "partner_choices.py",
    "ranked_summary_neighbors.py",
    "raydb_table_to_ray.py",
    "rayjoin_topology_intro.py",
    "robot_collision_lowering.py",
    "triangle_counting_graph_lowering.py",
}

OPERATOR_COMPANION_FILES = {
    "aabb_index_all_ops_count.py",
    "benchmark_app_recipes.py",
    "closest_hit_grouped_argmin_torch_device_arrays.py",
    "custom_predicate_early_exit_planning.py",
    "fixed_radius_torch_device_arrays.py",
    "operator_callback_planning.py",
    "point_group_nearest_witness_torch_device_arrays.py",
    "primitive_grouped_i64_reduction_torch_device_arrays.py",
    "ray_triangle_any_hit_flags_torch_device_arrays.py",
    "ray_triangle_any_hit_weighted_sum_torch_device_arrays.py",
    "v4_frontdoor_quickstart.py",
}

CONCEPT_MAP_FILES = {"operator_primitives.py"}


class V4Goal4800KernelFirstTutorialClassificationTest(unittest.TestCase):
    def read_program(self, name: str) -> str:
        return (PROGRAMS / name).read_text(encoding="utf-8")

    def test_every_tutorial_program_is_classified(self) -> None:
        expected = (
            KERNEL_FIRST_FILES
            | RELATION_FIRST_FILES
            | OPERATOR_COMPANION_FILES
            | CONCEPT_MAP_FILES
        )
        actual = {path.name for path in PROGRAMS.glob("*.py") if path.name != "__init__.py"}
        self.assertEqual(expected, actual)

    def test_kernel_first_files_contain_real_kernel_decorators(self) -> None:
        for name in sorted(KERNEL_FIRST_FILES):
            with self.subTest(name=name):
                text = self.read_program(name)
                self.assertIn("@rt.kernel", text)

    def test_relation_first_files_explain_kernel_programming_method(self) -> None:
        for name in sorted(RELATION_FIRST_FILES):
            with self.subTest(name=name):
                text = self.read_program(name)
                self.assertIn("core_tutorial_program_relation_first", text)
                self.assertIn("kernel_programming_method", text)

    def test_operator_companions_are_not_first_lessons(self) -> None:
        for name in sorted(OPERATOR_COMPANION_FILES):
            with self.subTest(name=name):
                text = self.read_program(name)
                self.assertIn("operator_companion_after_kernel_first_lesson", text)
                self.assertIn("not_first_lesson", text)
                self.assertIn("kernel_first_requirement", text)

    def test_concept_map_is_not_misrepresented_as_execution_program(self) -> None:
        text = self.read_program("operator_primitives.py")
        self.assertIn("core_concept_map_not_execution_program", text)
        self.assertIn("not_a_kernel_execution_example", text)

    def test_public_entrypoint_order_keeps_frontdoor_after_kernel_lessons(self) -> None:
        checked_files = [
            ROOT / "README.md",
            ROOT / "examples" / "README.md",
            ROOT / "examples" / "tutorial_programs" / "README.md",
            ROOT / "docs" / "public_documentation_map.md",
            ROOT / "docs" / "learn" / "source_tree_doctor.md",
        ]
        for path in checked_files:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                sorting = text.find("sorting_rows.py")
                frontdoor = text.find("v4_frontdoor_quickstart.py")
                self.assertNotEqual(sorting, -1)
                self.assertNotEqual(frontdoor, -1)
                self.assertLess(sorting, frontdoor)


if __name__ == "__main__":
    unittest.main()
