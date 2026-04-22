import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference
from rtdsl.baseline_runner import load_representative_case
from tests._embree_support import embree_available
from tests.rtdl_sorting_test import native_oracle_available
from tests.rtdl_sorting_test import optix_available


DATASETS = (
    "authored_segment_polygon_minimal",
    "tests/fixtures/rayjoin/br_county_subset.cdb",
    "derived/br_county_subset_segment_polygon_tiled_x4",
)

PREPARED_DATASETS = (
    "authored_segment_polygon_minimal",
    "tests/fixtures/rayjoin/br_county_subset.cdb",
)


def _pack_case_inputs(case):
    return {
        "segments": rt.pack_segments(records=case.inputs["segments"]),
        "polygons": rt.pack_polygons(records=case.inputs["polygons"]),
    }


@unittest.skipUnless(embree_available(), "Embree is not installed in the current environment")
class Goal110EmbreeClosureTest(unittest.TestCase):
    def test_embree_matches_python_reference_on_goal110_datasets(self) -> None:
        for dataset in DATASETS:
            with self.subTest(dataset=dataset):
                case = load_representative_case("segment_polygon_hitcount", dataset)
                expected = rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
                actual = rt.run_embree(segment_polygon_hitcount_reference, **case.inputs)
                self.assertTrue(rt.compare_baseline_rows("segment_polygon_hitcount", expected, actual))

    def test_prepared_embree_matches_current_on_authored_and_fixture_cases(self) -> None:
        prepared = rt.prepare_embree(segment_polygon_hitcount_reference)
        for dataset in PREPARED_DATASETS:
            with self.subTest(dataset=dataset):
                case = load_representative_case("segment_polygon_hitcount", dataset)
                packed = _pack_case_inputs(case)
                current_rows = rt.run_embree(segment_polygon_hitcount_reference, **case.inputs)
                prepared_rows = prepared.run(**packed)
                raw_rows = prepared.bind(**packed).run_raw()
                try:
                    raw_dict_rows = raw_rows.to_dict_rows()
                finally:
                    raw_rows.close()
                self.assertEqual(current_rows, prepared_rows)
                self.assertEqual(current_rows, raw_dict_rows)


@unittest.skipUnless(native_oracle_available(), "Native oracle is not available in the current environment")
class Goal110CpuClosureTest(unittest.TestCase):
    def test_cpu_matches_python_reference_on_goal110_datasets(self) -> None:
        for dataset in DATASETS:
            with self.subTest(dataset=dataset):
                case = load_representative_case("segment_polygon_hitcount", dataset)
                expected = rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
                actual = rt.run_cpu(segment_polygon_hitcount_reference, **case.inputs)
                self.assertTrue(rt.compare_baseline_rows("segment_polygon_hitcount", expected, actual))


@unittest.skipUnless(optix_available(), "OptiX is not available in the current environment")
class Goal110OptixClosureTest(unittest.TestCase):
    def test_optix_matches_python_reference_on_goal110_datasets(self) -> None:
        for dataset in DATASETS:
            with self.subTest(dataset=dataset):
                case = load_representative_case("segment_polygon_hitcount", dataset)
                expected = rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
                actual = rt.run_optix(segment_polygon_hitcount_reference, **case.inputs)
                self.assertTrue(rt.compare_baseline_rows("segment_polygon_hitcount", expected, actual))

    def test_optix_matches_python_reference_for_short_segment_inside_polygon(self) -> None:
        inputs = {
            "segments": (rt.Segment(id=1, x0=0.1, y0=0.1, x1=0.35, y1=0.1),),
            "polygons": (rt.Polygon(id=10, vertices=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))),),
        }
        expected = rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **inputs)
        self.assertEqual(expected, ({"segment_id": 1, "hit_count": 1},))
        self.assertEqual(rt.run_optix(segment_polygon_hitcount_reference, **inputs), expected)

    def test_prepared_optix_matches_current_on_authored_and_fixture_cases(self) -> None:
        prepared = rt.prepare_optix(segment_polygon_hitcount_reference)
        for dataset in PREPARED_DATASETS:
            with self.subTest(dataset=dataset):
                case = load_representative_case("segment_polygon_hitcount", dataset)
                packed = _pack_case_inputs(case)
                current_rows = rt.run_optix(segment_polygon_hitcount_reference, **case.inputs)
                prepared_rows = prepared.run(**packed)
                raw_rows = prepared.bind(**packed).run_raw()
                try:
                    raw_dict_rows = raw_rows.to_dict_rows()
                finally:
                    raw_rows.close()
                self.assertEqual(current_rows, prepared_rows)
                self.assertEqual(current_rows, raw_dict_rows)


if __name__ == "__main__":
    unittest.main()
