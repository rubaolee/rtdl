from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m13_hit_stream_no_hidden_copy_evidence.py"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
RUNNER = ROOT / "scripts/v3_0_m13_hit_stream_no_hidden_copy_measure.py"


class Goal4409V30M13HitStreamNoHiddenCopyEvidenceTest(unittest.TestCase):
    def test_m13_module_defines_second_workload_contract(self) -> None:
        text = MODULE.read_text(encoding="utf-8")
        self.assertIn("V3_M13_HIT_STREAM_NO_HIDDEN_COPY_VERSION", text)
        self.assertIn("ray_triangle_hit_stream_row_reduction_no_hidden_copy_pilot", text)
        self.assertIn("classify_no_hidden_copy_transfer_snapshot", text)
        self.assertIn("validate_no_hidden_copy_payload", text)
        self.assertIn("post_native_enqueue_same_stream_hit_stream_row_reduction_before_summary_materialization", text)
        self.assertIn("make_v3_m13_hit_stream_rays", text)

    def test_runtime_hook_disables_counter_before_summary_materialization(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")
        helper_start = text.index("def _run_hit_stream_same_stream_row_reduction_summary_cupy")
        helper_end = text.index("def _run_hit_stream_event_ordered_row_reduction_summary_cupy", helper_start)
        helper = text[helper_start:helper_end]
        self.assertIn("transfer_counter=None", helper)
        self.assertIn("transfer_counter.disable_and_snapshot()", helper)
        self.assertIn("result = {", helper)
        self.assertIn('result["_transfer_counter_snapshot"] = transfer_counter_snapshot', helper)
        self.assertIn("return result", helper)
        self.assertLess(helper.index("transfer_counter.disable_and_snapshot()"), helper.index("cp.asnumpy(summary)"))
        self.assertLess(helper.index('result["_transfer_counter_snapshot"]'), helper.rindex("return result"))

        method_start = text.index("def ray_triangle_hit_stream_same_stream_row_reduction_summary")
        method_end = text.index("def ray_triangle_hit_stream_event_ordered_row_reduction_summary", method_start)
        method = text[method_start:method_end]
        self.assertIn("transfer_counter=None", method)
        self.assertIn("transfer_counter.enable()", method)
        self.assertIn('"transfer_counter_window"', method)
        self.assertIn("post_native_enqueue_same_stream_row_reduction_before_summary_materialization", method)

    def test_runner_preloads_counter_before_rtdsl_import(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("LD_PRELOAD", text)
        self.assertIn("os.execvpe", text)
        self.assertLess(text.index("_ensure_transfer_counter_preloaded"), text.index("import rtdsl as rt"))
        self.assertIn("run_v3_m13_hit_stream_no_hidden_copy_evidence_case", text)

    def test_fixture_generation_is_deterministic_and_nonempty(self) -> None:
        triangles = rt.make_v3_m13_two_plane_triangles()
        rays = rt.make_v3_m13_hit_stream_rays(8)
        self.assertEqual(2, len(triangles))
        self.assertEqual(8, len(rays))
        self.assertEqual((0, 1), tuple(triangle.id for triangle in triangles))
        self.assertEqual(tuple(range(8)), tuple(ray.id for ray in rays))
        with self.assertRaisesRegex(GraphValidationError, "ray_count must be positive"):
            rt.make_v3_m13_hit_stream_rays(0)

    def test_validator_accepts_synthetic_m13_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m13_hit_stream_no_hidden_copy_payload(payload)
        self.assertTrue(validation["same_stream_ready"])
        self.assertTrue(validation["true_zero_copy_ready"])
        self.assertFalse(validation["public_claim_authorized"])

    def test_validator_rejects_wrong_window_scope(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        metadata = dict(row["metadata"])
        evidence = dict(metadata["same_stream_evidence"])
        evidence["event_pair_scope"] = "wrong_window"
        metadata["same_stream_evidence"] = evidence
        row["metadata"] = metadata
        payload["partner_rows"] = (row,)
        with self.assertRaisesRegex(GraphValidationError, "measured window scope"):
            rt.validate_v3_m13_hit_stream_no_hidden_copy_payload(payload)


def _snapshot() -> dict[str, object]:
    return {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": 0,
        "total_bytes": 0,
        "host_to_device_calls": 0,
        "host_to_device_bytes": 0,
        "device_to_host_calls": 0,
        "device_to_host_bytes": 0,
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }


def _synthetic_payload() -> dict[str, object]:
    classification = rt.classify_no_hidden_copy_transfer_snapshot(
        _snapshot(),
        min_named_column_bytes=8192,
        measured_window="post_native_enqueue_same_stream_hit_stream_row_reduction_before_summary_materialization",
        readiness_source="v3_m13_hit_stream_transfer_counter_classification",
    )
    metadata = rt.annotate_no_hidden_copy_metadata(
        {
            "same_stream_evidence": {
                "event_pair_scope": "post_native_enqueue_to_cupy_row_reduction_before_summary_materialization",
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(),
                "host_row_materialization_before_consumer": False,
            }
        },
        classification,
        readiness_source="v3_m13_hit_stream_transfer_counter_classification",
    )
    return {
        "version": rt.V3_M13_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        "status": rt.V3_M13_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        "graph_id": rt.V3_M13_GRAPH_ID,
        "contract_key": rt.V3_M13_CONTRACT_KEY,
        "partner_rows": (
            {
                "partner": "cupy",
                "backend": "optix",
                "validation_signature": (16, 16, 16, 28, 8, 0, 0, 1),
                "ray_count": 8,
                "metadata": metadata,
                "transfer_counter_classification": classification,
                "same_stream_ready": True,
                "transfer_counter_observed": True,
                "no_hidden_column_copy_ready": True,
                "true_zero_copy_ready": True,
                "public_claim_authorized": False,
            },
        ),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "no_hidden_column_copy_ready": True,
            "true_zero_copy_ready": True,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
