from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PROBE = ROOT / "scripts" / "goal3310_rayjoin_pip_batch_scalar_count_probe.py"


class Goal3314PreparedPointMultistreamBatchCountTest(unittest.TestCase):
    def test_native_batch_path_has_opt_in_stream_pool(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT", text)
        self.assertIn("prepared_closed_shape_batch_stream_count", text)

        start = text.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d_optix"
        )
        end = text.index("struct PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D", start)
        body = text[start:end]
        self.assertIn("std::vector<CUstream> streams", body)
        self.assertIn("cuStreamCreate", body)
        self.assertIn("request_index % stream_count", body)
        self.assertIn("cuStreamSynchronize(stream)", body)
        self.assertIn("cuStreamDestroy(stream)", body)
        self.assertNotIn("rayjoin", body.lower())

    def test_probe_script_exposes_stream_count_without_changing_claim_boundary(self) -> None:
        probe = PROBE.read_text(encoding="utf-8")
        self.assertIn("--batch-stream-count", probe)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT", probe)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', probe)
        self.assertIn("repeated-query throughput evidence only", probe)


if __name__ == "__main__":
    unittest.main()
