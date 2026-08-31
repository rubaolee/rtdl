from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tarfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "history" / "internal_docs" / (
    "goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json"
)
A2_RESULT = ROOT / "history" / "internal_docs" / (
    "goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json"
)
BASE = ROOT / "history" / "internal_docs" / (
    "goal5790_a1_portable_source_v4_20260816.tar.gz"
)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_result() -> dict[str, object]:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def _load_a2_result() -> dict[str, object]:
    return json.loads(A2_RESULT.read_text(encoding="utf-8"))


class Goal5791PretimerExecutionTokenAmendmentTest(unittest.TestCase):
    def test_result_is_canonically_sealed_and_cannot_authorize_target_work(self):
        result = _load_result()
        claimed = result.pop("canonical_content_sha256")
        canonical = json.dumps(
            result, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        self.assertEqual(claimed, _sha_bytes(canonical))
        self.assertEqual(
            result["status"],
            "FINAL_LOCAL_PRETARGET__NO_POD__NO_REGISTERED_TIMING",
        )
        authorization = result["authorization"]
        self.assertTrue(authorization["authorizes_home_functional_requalification"])
        for field in (
            "authorizes_pod",
            "authorizes_target_prepare",
            "authorizes_formal_worker_zero",
            "authorizes_registered_timing",
            "authorizes_performance_claim",
            "authorizes_publication_or_submission",
        ):
            self.assertIs(authorization[field], False)

    def test_selected_base_and_append_only_product_lineage_are_exact(self):
        result = _load_result()
        a2 = _load_a2_result()
        self.assertEqual(
            _sha_file(BASE), result["selected_base"]["archive_sha256"]
        )
        rows = result["product_delta"]
        self.assertEqual(
            [row["path"] for row in rows],
            [
                "src/rtdsl/v4_operation_evidence.py",
                "src/rtdsl/v4_triangle_reduction_device_runtime.py",
            ],
        )
        with tarfile.open(BASE, "r:gz") as archive:
            for row in rows:
                base_bytes = archive.extractfile(row["path"]).read()
                successor = ROOT / row["path"]
                self.assertEqual(_sha_bytes(base_bytes), row["base_sha256"])
                self.assertNotEqual(row["base_sha256"], row["successor_sha256"])
                if row["path"] == "src/rtdsl/v4_operation_evidence.py":
                    self.assertEqual(_sha_file(successor), row["successor_sha256"])
                    self.assertEqual(successor.stat().st_size, row["successor_bytes"])
                else:
                    self.assertEqual(
                        a2["product_delta"]["a1_sha256"],
                        row["successor_sha256"],
                    )
                    self.assertEqual(
                        _sha_file(successor),
                        a2["product_delta"]["successor_sha256"],
                    )
                    self.assertEqual(
                        successor.stat().st_size,
                        a2["product_delta"]["successor_bytes"],
                    )

    def test_new_test_identity_and_zero_native_delta_are_bound(self):
        result = _load_result()
        a2 = _load_a2_result()
        row = result["new_test"]
        path = ROOT / row["path"]
        self.assertEqual(a2["focused_test"]["path"], row["path"])
        self.assertEqual(_sha_file(path), a2["focused_test"]["sha256"])
        self.assertEqual(path.stat().st_size, a2["focused_test"]["bytes"])
        self.assertIn(
            "focused token test",
            a2["supersession"]["supersession_scope"],
        )
        self.assertEqual(result["verification"]["source_diff_exact_product_files"], 2)
        self.assertEqual(result["verification"]["native_files_changed"], 0)
        self.assertEqual(result["verification"]["registered_timings"], 0)

    def test_a2_is_canonically_sealed_and_preexecution_only(self):
        result = _load_a2_result()
        claimed = result.pop("canonical_content_sha256")
        canonical = json.dumps(
            result, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        self.assertEqual(claimed, _sha_bytes(canonical))
        self.assertEqual(result["verification"]["tests_passed"], 16)
        self.assertEqual(result["verification"]["home_gpu_lanes_executed"], 0)
        self.assertEqual(result["verification"]["target_workers_executed"], 0)
        self.assertEqual(result["verification"]["registered_timings"], 0)

    def test_timer_and_claim_boundary_remain_explicit(self):
        result = _load_result()
        timer = result["formal_timer_contract"]
        self.assertEqual(timer["token_issue_phase"], "preparation_before_registered_execute")
        self.assertIs(timer["timer_pause_or_resume_allowed"], False)
        self.assertIs(timer["receipt_sealing_inside_timer"], False)
        self.assertIs(timer["operation_event_instrumentation_inside_timer"], True)
        self.assertEqual(timer["operation_event_counts"], {
            "fusion_on": 2,
            "fusion_off": 7,
        })
        self.assertIs(timer["event_overhead_subtracted_or_corrected"], False)


if __name__ == "__main__":
    unittest.main()
