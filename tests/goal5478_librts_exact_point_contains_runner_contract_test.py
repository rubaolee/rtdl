from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "run_exact_point_contains_count_gate.py"
SPEC = importlib.util.spec_from_file_location("librts_goal5478_runner", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5478LibrtsExactPointContainsRunnerContractTest(unittest.TestCase):
    def test_wkt_frontdoor_handles_polygon_spacing_and_scientific_values(self):
        self.assertEqual(
            MODULE.geometry_wkt_mbr(
                "POLYGON ((-1e1 2, 3 4.5, 8 -2, -10 2))"
            ),
            (-10.0, -2.0, 8.0, 4.5),
        )
        self.assertEqual(MODULE.point_wkt_xy("POINT (1.25 -3e-1)"), (1.25, -0.3))

    def test_wkt_frontdoor_expands_multipolygon_into_author_index_records(self):
        self.assertEqual(
            MODULE.geometry_wkt_mbrs(
                "MULTIPOLYGON (((0 0, 2 0, 0 1, 0 0)), ((10 10, 12 10, 10 11, 10 10)))"
            ),
            ((0.0, 0.0, 2.0, 1.0), (10.0, 10.0, 12.0, 11.0)),
        )

    def test_author_output_parser_keeps_internal_denominator_separate(self):
        parsed = MODULE.parse_author_output(
            "Loaded polygons 12234\nLoaded queries 100000\n"
            "Loading Time 0.4224 ms\nGeoms 12234\nQueries 100000\n"
            "Query Time 0.0544 ms\nResults 136475\n"
        )
        self.assertEqual(parsed["result_count"], 136475)
        self.assertEqual(parsed["geometry_count"], 12234)
        self.assertAlmostEqual(parsed["query_ms_internal"], 0.0544)

    def test_exact_gate_rejects_unverified_or_outside_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            extracted = root / "extracted"
            extracted.mkdir()
            geometry = extracted / "geom.wkt"
            query = extracted / "query.wkt"
            geometry.write_text("POLYGON((0 0,1 0,1 1,0 0))\n")
            query.write_text("POINT(0.5 0.5)\n")
            archive = {"claim_boundary": {"archive_verified": True}}
            extraction = {
                "claim_boundary": {"archive_extracted": True},
                "extraction": {"final_path": str(extracted)},
            }
            self.assertEqual(
                MODULE.validate_exact_input_evidence(
                    archive_result=archive,
                    extraction_result=extraction,
                    geometry_path=geometry,
                    query_path=query,
                ),
                extracted.resolve(),
            )
            with self.assertRaises(ValueError):
                MODULE.validate_exact_input_evidence(
                    archive_result={"claim_boundary": {"archive_verified": False}},
                    extraction_result=extraction,
                    geometry_path=geometry,
                    query_path=query,
                )
            outside = root / "outside.wkt"
            outside.write_text("POINT(0 0)\n")
            with self.assertRaises(ValueError):
                MODULE.validate_exact_input_evidence(
                    archive_result=archive,
                    extraction_result=extraction,
                    geometry_path=geometry,
                    query_path=outside,
                )


if __name__ == "__main__":
    unittest.main()
