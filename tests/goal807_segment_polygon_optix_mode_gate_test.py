from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from scripts import goal807_segment_polygon_optix_mode_gate as gate


def _payload(segment_id: int = 1, hit_count: int = 2) -> dict[str, object]:
    return {
        "backend": "mock",
        "optix_mode": "not_applicable",
        "rows": ({"segment_id": segment_id, "hit_count": hit_count},),
        "optix_performance": {"class": "host_indexed_fallback"},
    }


class Goal807SegmentPolygonOptixModeGateTest(unittest.TestCase):
    def test_gate_runs_reference_host_indexed_and_native_modes(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_run_case(backend: str, dataset: str, *, optix_mode: str = "auto"):
            calls.append((backend, optix_mode))
            return _payload()

        with mock.patch.object(gate.app, "run_case", side_effect=fake_run_case):
            payload = gate.run_gate(dataset="authored_segment_polygon_minimal", strict=True)

        self.assertEqual(
            calls,
            [
                ("cpu_python_reference", "auto"),
                ("optix", "host_indexed"),
                ("optix", "native"),
            ],
        )
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["strict_pass"])
        self.assertEqual(payload["strict_failures"], [])
        self.assertEqual(payload["schema_version"], "goal831_segment_polygon_native_gate_contract_v1")
        self.assertIn("cloud_claim_contract", payload)
        self.assertIn("optix_native", payload["cloud_claim_contract"]["required_record_labels"])

    def test_non_strict_gate_records_missing_native_optix_without_throwing(self) -> None:
        def fake_run_case(backend: str, dataset: str, *, optix_mode: str = "auto"):
            if backend == "optix" and optix_mode == "native":
                raise RuntimeError("native OptiX unavailable")
            return _payload()

        with mock.patch.object(gate.app, "run_case", side_effect=fake_run_case):
            payload = gate.run_gate(dataset="authored_segment_polygon_minimal")

        self.assertEqual(payload["status"], "non_strict_recorded_gaps")
        self.assertFalse(payload["strict_pass"])
        self.assertIn("optix_native did not run", payload["strict_failures"])

    def test_postgis_record_digest_is_preserved(self) -> None:
        def fake_run_case(backend: str, dataset: str, *, optix_mode: str = "auto"):
            return _payload()

        with mock.patch.object(gate.app, "run_case", side_effect=fake_run_case):
            with mock.patch.object(
                gate,
                "_postgis_record",
                return_value={
                    "label": "postgis",
                    "status": "ok",
                    "postgis_query_sec": 0.25,
                    "row_digest": gate._row_digest(({"segment_id": 1, "hit_count": 2},)),
                },
            ):
                payload = gate.run_gate(
                    dataset="authored_segment_polygon_minimal",
                    include_postgis=True,
                    strict=True,
                )

        postgis = next(record for record in payload["records"] if record["label"] == "postgis")
        self.assertTrue(postgis["parity_vs_cpu_python_reference"])
        self.assertEqual(postgis["postgis_query_sec"], 0.25)
        self.assertEqual(payload["status"], "pass")

    def test_cli_writes_json_and_uses_copy_shortcut(self) -> None:
        output = Path("docs/reports/goal807_test_output.json")

        def fake_run_gate(**kwargs):
            return {
                "status": "pass",
                "strict_failures": [],
                "dataset": kwargs["dataset"],
            }

        try:
            with mock.patch.object(gate, "run_gate", side_effect=fake_run_gate):
                rc = gate.main(["--copies", "8", "--output-json", str(output)])
            self.assertEqual(rc, 0)
            self.assertIn("tiled_x8", output.read_text(encoding="utf-8"))
        finally:
            output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
