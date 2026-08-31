from __future__ import annotations

from pathlib import Path
import os
from types import SimpleNamespace
import unittest
from unittest import mock

from examples.current.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)


ROOT = Path(__file__).resolve().parents[1]
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3321_rayjoin_pip_preflight_pod_smoke_2026-06-04.json"
EXPECTED_POD_COMMIT = "4b72d290b2c3f7fea309e79ad13ce9bbfc5459f1"


class _PackedPoints:
    count = 2


class _PackedShapes:
    polygon_count = 1


class _PreparedPointColumns:
    def __init__(self) -> None:
        self.closed = False

    def to_metadata(self) -> dict[str, object]:
        return {
            "schema": "rtdl.optix.prepared_point_probe_columns_2d.v1",
            "count": 2,
        }

    def close(self) -> None:
        self.closed = True


class _Prepared:
    def __init__(self, *, exact_count: int, fast_count: int) -> None:
        self.exact_count = exact_count
        self.fast_count = fast_count
        self.closed = False
        self.prepared_columns = _PreparedPointColumns()
        self.observed_device_predicate_eps: list[str | None] = []

    def count(self, _packed_points) -> int:
        return self.exact_count

    def count_device_filtered_prepared_points(self, _prepared_point_columns) -> int:
        self.observed_device_predicate_eps.append(os.environ.get("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS"))
        return self.fast_count

    def prepare_point_probe_columns(self, _packed_points) -> _PreparedPointColumns:
        return self.prepared_columns

    def close(self) -> None:
        self.closed = True


class Goal3321RayJoinPipValidatedDomainPreflightTest(unittest.TestCase):
    def _run_preflight(
        self,
        *,
        exact_count: int,
        fast_count: int,
        require_match: bool = False,
        device_predicate_eps: float | None = None,
    ):
        prepared = _Prepared(exact_count=exact_count, fast_count=fast_count)
        case = SimpleNamespace(
            inputs={
                "points": [{"id": 0, "x": 0.0, "y": 0.0}, {"id": 1, "x": 1.0, "y": 1.0}],
                "polygons": [{"id": 7}],
            },
            note="mock case",
        )
        with mock.patch.object(rayjoin_app, "_load_rayjoin_case", return_value=case), mock.patch.object(
            rayjoin_app,
            "_order_points_for_locality",
            side_effect=lambda points, _mode: points,
        ), mock.patch(
            "rtdsl.optix_runtime.pack_points",
            return_value=_PackedPoints(),
        ), mock.patch(
            "rtdsl.optix_runtime.pack_polygons",
            return_value=_PackedShapes(),
        ), mock.patch(
            "rtdsl.optix_runtime.prepare_point_closed_shape_membership_2d_optix",
            return_value=prepared,
        ):
            result = rayjoin_app.preflight_rayjoin_pip_fast_count_domain(
                dataset="mock.cdb",
                count_mode="device_filtered_prepared_points_validated",
                device_filtered_boundary_mode="inclusive",
                query_axis="z_point",
                scalar_count_pipeline=True,
                device_predicate_eps=device_predicate_eps,
                require_match=require_match,
            )
        return result, prepared

    def test_preflight_allows_matching_fast_route_with_clean_boundaries(self) -> None:
        result, prepared = self._run_preflight(exact_count=1471, fast_count=1471)

        self.assertEqual(result["schema"], "rtdl.rayjoin.pip_fast_count_domain_preflight.v1")
        self.assertEqual(result["dataset"], "mock.cdb")
        self.assertEqual(result["count_mode"], "device_filtered_prepared_points_validated")
        self.assertEqual(result["device_filtered_boundary_mode"], "inclusive")
        self.assertEqual(result["query_axis"], "z_point")
        self.assertTrue(result["scalar_count_pipeline"])
        self.assertEqual(result["point_count"], 2)
        self.assertEqual(result["shape_count"], 1)
        self.assertEqual(result["exact_count"], 1471)
        self.assertEqual(result["fast_count"], 1471)
        self.assertTrue(result["matches_exact"])
        self.assertEqual(result["status"], "validated_fast_route_allowed")
        self.assertFalse(result["fallback_required"])
        self.assertIsNone(result["fallback_reason"])
        self.assertEqual(result["prepared_point_probe_columns"]["count"], 2)
        self.assertTrue(prepared.closed)
        self.assertTrue(prepared.prepared_columns.closed)
        for authorized in result["claim_boundary"].values():
            self.assertIs(authorized, False)

    def test_preflight_scopes_device_predicate_eps_to_match_measured_route(self) -> None:
        result, prepared = self._run_preflight(
            exact_count=1417,
            fast_count=1417,
            device_predicate_eps=1e-9,
        )

        self.assertEqual(result["device_predicate_eps"], 1e-9)
        self.assertEqual(prepared.observed_device_predicate_eps, ["1.0000000000000001e-09"])
        self.assertIsNone(os.environ.get("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS"))

    def test_preflight_records_mismatch_as_fallback_required(self) -> None:
        result, prepared = self._run_preflight(exact_count=1417, fast_count=1429)

        self.assertEqual(result["exact_count"], 1417)
        self.assertEqual(result["fast_count"], 1429)
        self.assertFalse(result["matches_exact"])
        self.assertEqual(result["status"], "fast_route_rejected")
        self.assertTrue(result["fallback_required"])
        self.assertEqual(result["fallback_reason"], "fast count route did not match exact prepared count")
        self.assertIn("generic point/closed-shape count primitives", result["native_engine_boundary"])
        self.assertTrue(prepared.closed)
        self.assertTrue(prepared.prepared_columns.closed)

    def test_require_match_fails_closed_on_mismatch(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "validated-domain preflight rejected fast PIP count route"):
            self._run_preflight(exact_count=47262, fast_count=47554, require_match=True)

    def test_report_documents_boundary(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal3321_rayjoin_pip_validated_domain_preflight_2026-06-04.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Goal3321 - RayJoin PIP Validated-Domain Preflight", report)
        self.assertIn("preflight_rayjoin_pip_fast_count_domain", report)
        self.assertIn("4b72d290b2c3f7fea309e79ad13ce9bbfc5459f1", report)
        self.assertIn("soil_pass", report)
        self.assertIn("county_fail", report)
        self.assertIn("fallback is required", report)
        self.assertIn("does not add RayJoin-specific native logic", report)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", report)

    def test_pod_artifact_records_pass_and_fail_closed_preflight(self) -> None:
        import json

        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3321.rayjoin_pip_preflight_pod_smoke.v1")
        self.assertEqual(data["goal"], 3321)
        self.assertEqual(data["rtdl_commit"], EXPECTED_POD_COMMIT)
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")

        rows = {row["label"]: row for row in data["rows"]}
        self.assertEqual(set(rows), {"soil_pass", "county_fail"})
        self.assertEqual(rows["soil_pass"]["exact_count"], 1471)
        self.assertEqual(rows["soil_pass"]["fast_count"], 1471)
        self.assertTrue(rows["soil_pass"]["matches_exact"])
        self.assertEqual(rows["soil_pass"]["status"], "validated_fast_route_allowed")
        self.assertFalse(rows["soil_pass"]["fallback_required"])

        self.assertEqual(rows["county_fail"]["exact_count"], 1417)
        self.assertEqual(rows["county_fail"]["fast_count"], 1429)
        self.assertFalse(rows["county_fail"]["matches_exact"])
        self.assertEqual(rows["county_fail"]["status"], "fast_route_rejected")
        self.assertTrue(rows["county_fail"]["fallback_required"])

        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)


if __name__ == "__main__":
    unittest.main()
