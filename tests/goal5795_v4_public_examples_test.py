from __future__ import annotations

import ast
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = (
    ROOT / "examples" / "current" / "v4_public_bounded_relation.py",
    ROOT / "examples" / "current" / "v4_public_triangle_reduction.py",
    ROOT / "examples" / "current" / "v4_public_stable_sort.py",
)


class Goal5795PublicExamplesTest(unittest.TestCase):
    def test_examples_import_rtdl_only_through_public_v4(self):
        banned_text = (
            "_load_optix_library", "rtdsl.optix_runtime",
            "rtdsl.v4_bounded_", "rtdsl.v4_triangle_",
            "prepare_bounded_relation_callback",
            "prepare_triangle_reduction_callback",
            "open_v4_callback_provider", "ctypes.CDLL",
        )
        for path in EXAMPLES:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            rtdsl_imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    rtdsl_imports.extend(
                        alias.name for alias in node.names
                        if alias.name == "rtdsl" or alias.name.startswith("rtdsl."))
                elif isinstance(node, ast.ImportFrom) and node.module \
                        and (node.module == "rtdsl" or node.module.startswith("rtdsl.")):
                    rtdsl_imports.append(node.module)
            self.assertEqual(rtdsl_imports, ["rtdsl.v4"], path.name)
            for token in banned_text:
                self.assertNotIn(token, source, f"{path.name}: {token}")

    def test_diagnostic_fixtures_encode_declared_answers(self):
        bounded = runpy.run_path(str(EXAMPLES[0]), run_name="goal5795_bounded")
        self.assertEqual(bounded["EXPECTED_ROWS"], ((100, 10), (101, 20)))

        triangle = runpy.run_path(str(EXAMPLES[1]), run_name="goal5795_triangle")
        self.assertEqual(triangle["EXPECTED_PER_RAY"], (3, 2, 0, 1))
        self.assertEqual(triangle["WEIGHTS"], (1, 3, 5, 7))
        self.assertEqual(
            sum(count * weight for count, weight in zip(
                triangle["EXPECTED_PER_RAY"], triangle["WEIGHTS"])),
            triangle["EXPECTED_WEIGHTED_SUM"],
        )
        counts = []
        for origin, direction, tmax in triangle["QUERIES"]:
            hits = 0
            for indices in triangle["TRIANGLES"]:
                a, b, c = (triangle["VERTICES"][index] for index in indices)
                # These diagnostic triangles are parallel to XY and every ray
                # is +Z, so this is an independent fixture check rather than a
                # call through any RTDL semantic or runtime route.
                t = (a[2] - origin[2]) / direction[2]
                x = origin[0] + direction[0] * t
                y = origin[1] + direction[1] * t
                dx = x - a[0]
                dy = y - a[1]
                inside = dx >= 0.0 and dy >= 0.0 and dx + dy <= 1.0
                if 0.0 <= t <= tmax and inside:
                    hits += 1
            counts.append(hits)
        self.assertEqual(tuple(counts), triangle["EXPECTED_PER_RAY"])

        sorting = runpy.run_path(str(EXAMPLES[2]), run_name="goal5830_sorting")
        encoding = sorting["encode_stable_sort"](
            (2, 1, 2, 0),
            indexed_order=(2, 0, 3, 1),
            source_order=(3, 2, 1, 0),
        )
        rows = sorting["geometry_relation_reference"](encoding)
        self.assertEqual(
            rows,
            sorting["predecessor_relation_oracle"]((2, 1, 2, 0)),
        )
        self.assertEqual(
            sorting["stable_sort_from_relation"](
                (2, 1, 2, 0), rows).sorted_records,
            ((0, 3), (1, 1), (2, 0), (2, 2)),
        )


if __name__ == "__main__":
    unittest.main()
