from __future__ import annotations

import pathlib
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1873_fixed_radius_partner_reference_columns_2026-05-13.md"


class _FakeColumn:
    def __init__(self, values):
        self.values = list(values)
        self.shape = (len(self.values),)


def _fake_fixed_radius_count_threshold_2d(query, search, radius, threshold):
    radius_sq = float(radius) * float(radius)
    counts = []
    for qx, qy in zip(query["x"].values, query["y"].values):
        count = 0
        for sx, sy in zip(search["x"].values, search["y"].values):
            dx = float(qx) - float(sx)
            dy = float(qy) - float(sy)
            if dx * dx + dy * dy <= radius_sq:
                count += 1
        counts.append(count)
    return _FakeColumn(counts)


def _fake_partner_module(name: str):
    if name != "torch":
        raise AssertionError(name)
    return {
        "name": "torch",
        "sync": lambda: None,
        "greater_equal_uint32": lambda value, threshold: _FakeColumn(
            [1 if int(item) >= int(threshold) else 0 for item in value.values]
        ),
        "invert_binary_uint32": lambda value: _FakeColumn([1 - int(item) for item in value.values]),
        "fixed_radius_count_threshold_2d": _fake_fixed_radius_count_threshold_2d,
    }


class Goal1873FixedRadiusPartnerReferenceColumnsTest(unittest.TestCase):
    def test_fixed_radius_partner_reference_surface_is_exported(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIsNotNone(rt.fixed_radius_count_threshold_2d_partner_columns)
        self.assertIsNotNone(rt.service_coverage_gap_flags_partner_columns)
        self.assertIsNotNone(rt.event_hotspot_flags_partner_columns)
        self.assertIn("fixed_radius_count_threshold_2d_partner_columns", adapter_source)
        self.assertIn("service_coverage_gap_flags_partner_columns", init_source)
        self.assertIn("event_hotspot_flags_partner_columns", init_source)

    def test_fixed_radius_partner_reference_counts_and_flags(self) -> None:
        query = {
            "ids": _FakeColumn([1, 2]),
            "x": _FakeColumn([0.0, 5.0]),
            "y": _FakeColumn([0.0, 0.0]),
        }
        search = {
            "ids": _FakeColumn([10, 11]),
            "x": _FakeColumn([0.0, 0.5]),
            "y": _FakeColumn([0.0, 0.0]),
        }

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            result = rt.fixed_radius_count_threshold_2d_partner_columns(
                query,
                search,
                radius=1.0,
                threshold=2,
                partner="torch",
                return_metadata=True,
            )

        self.assertIs(result["columns"]["query_ids"], query["ids"])
        self.assertEqual(result["columns"]["neighbor_counts"].values, [2, 0])
        self.assertEqual(result["columns"]["threshold_flags"].values, [1, 0])
        metadata = result["metadata"]
        self.assertEqual(metadata["partner_reference_contract"], "generic_fixed_radius_count_threshold_2d")
        self.assertEqual(metadata["native_engine_row_contract"], "not_called_partner_reference_only")
        self.assertFalse(metadata["direct_device_handoff_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["v2_0_release_authorized"])

    def test_service_coverage_reference_flags_uncovered_households(self) -> None:
        households = {
            "ids": _FakeColumn([1, 2]),
            "x": _FakeColumn([0.0, 5.0]),
            "y": _FakeColumn([0.0, 0.0]),
        }
        clinics = {
            "ids": _FakeColumn([10]),
            "x": _FakeColumn([0.1]),
            "y": _FakeColumn([0.0]),
        }

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            result = rt.service_coverage_gap_flags_partner_columns(
                households,
                clinics,
                radius=1.0,
                partner="torch",
                return_metadata=True,
            )

        self.assertIs(result["columns"]["household_ids"], households["ids"])
        self.assertEqual(result["columns"]["nearby_clinic_counts"].values, [1, 0])
        self.assertEqual(result["columns"]["covered_flags"].values, [1, 0])
        self.assertEqual(result["columns"]["uncovered_flags"].values, [0, 1])
        self.assertEqual(result["metadata"]["adapter"], "service_coverage_gap_flags_partner_columns")
        self.assertEqual(result["metadata"]["app"], "service_coverage_gaps")
        self.assertFalse(result["metadata"]["rt_core_speedup_claim_authorized"])

    def test_event_hotspot_reference_uses_self_including_threshold(self) -> None:
        events = {
            "ids": _FakeColumn([1, 2, 3]),
            "x": _FakeColumn([0.0, 0.1, 5.0]),
            "y": _FakeColumn([0.0, 0.0, 0.0]),
        }

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            result = rt.event_hotspot_flags_partner_columns(
                events,
                radius=0.5,
                hotspot_threshold=1,
                partner="torch",
                return_metadata=True,
            )

        self.assertIs(result["columns"]["event_ids"], events["ids"])
        self.assertEqual(result["columns"]["neighbor_counts_including_self"].values, [2, 2, 1])
        self.assertEqual(result["columns"]["hotspot_flags"].values, [1, 1, 0])
        self.assertEqual(result["metadata"]["adapter"], "event_hotspot_flags_partner_columns")
        self.assertEqual(result["metadata"]["fixed_radius_threshold_including_self"], 2)

    def test_invalid_radius_and_threshold_fail_closed(self) -> None:
        columns = {"ids": _FakeColumn([]), "x": _FakeColumn([]), "y": _FakeColumn([])}
        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with self.assertRaisesRegex(ValueError, "radius must be non-negative"):
                rt.fixed_radius_count_threshold_2d_partner_columns(
                    columns,
                    columns,
                    radius=-1.0,
                    partner="torch",
                )
            with self.assertRaisesRegex(ValueError, "threshold must be non-negative"):
                rt.fixed_radius_count_threshold_2d_partner_columns(
                    columns,
                    columns,
                    radius=1.0,
                    threshold=-1,
                    partner="torch",
                )
            with self.assertRaisesRegex(ValueError, "hotspot_threshold must be non-negative"):
                rt.event_hotspot_flags_partner_columns(
                    columns,
                    radius=1.0,
                    hotspot_threshold=-1,
                    partner="torch",
                )

    def test_report_keeps_native_bridge_blocked(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("partner reference/conformance path only", report)
        self.assertIn("native_engine_row_contract: not_called_partner_reference_only", report)
        self.assertIn("direct_device_handoff_authorized: false", report)
        self.assertIn("rt_core_speedup_claim_authorized: false", report)
        self.assertIn("native bridge", report)


if __name__ == "__main__":
    unittest.main()
