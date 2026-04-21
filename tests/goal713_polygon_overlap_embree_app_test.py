from __future__ import annotations

import unittest

import rtdsl as rt
from examples import rtdl_polygon_pair_overlap_area_rows as overlap_app
from examples import rtdl_polygon_set_jaccard as jaccard_app


def _canonical(value):
    if isinstance(value, dict):
        return {
            key: _canonical(item)
            for key, item in value.items()
            if key not in {"backend", "backend_mode", "candidate_row_count"}
        }
    if isinstance(value, list) or isinstance(value, tuple):
        return sorted((_canonical(item) for item in value), key=repr)
    if isinstance(value, float):
        return round(value, 12)
    return value


class Goal713PolygonOverlapEmbreeAppTest(unittest.TestCase):
    def test_polygon_pair_overlap_embree_matches_cpu(self) -> None:
        cpu = overlap_app.run_case("cpu_python_reference")
        embree = overlap_app.run_case("embree")
        self.assertEqual(cpu["app"], "polygon_pair_overlap_area_rows")
        self.assertEqual(embree["app"], "polygon_pair_overlap_area_rows")
        self.assertEqual(embree["backend_mode"], "embree_native_assisted")
        self.assertGreater(embree["candidate_row_count"], 0)
        self.assertEqual(_canonical(cpu), _canonical(embree))

    def test_polygon_set_jaccard_embree_matches_cpu(self) -> None:
        cpu = jaccard_app.run_case("cpu_python_reference")
        embree = jaccard_app.run_case("embree")
        self.assertEqual(cpu["app"], "polygon_set_jaccard")
        self.assertEqual(embree["app"], "polygon_set_jaccard")
        self.assertEqual(embree["backend_mode"], "embree_native_assisted")
        self.assertGreater(embree["candidate_row_count"], 0)
        self.assertEqual(_canonical(cpu), _canonical(embree))

    def test_app_matrix_marks_embree_native_assisted(self) -> None:
        matrix = rt.app_engine_support_matrix()
        self.assertEqual(
            matrix["polygon_pair_overlap_area_rows"]["embree"].status,
            "direct_cli_native_assisted",
        )
        self.assertEqual(
            matrix["polygon_set_jaccard"]["embree"].status,
            "direct_cli_native_assisted",
        )


if __name__ == "__main__":
    unittest.main()
