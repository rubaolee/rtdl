from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PY_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal2337_rayjoin_pip_first_hit_comparison.py"
REPORT = ROOT / "docs" / "reports" / "goal2337_v2_1_rayjoin_first_hit_runtime_extension_2026-05-18.md"
ARTIFACTS = ROOT / "docs" / "reports" / "goal2337_v2_1_rayjoin_first_hit_pod"


class Goal2337V21SegmentFirstHitRuntimeExtensionTest(unittest.TestCase):
    def test_native_abi_adds_generic_first_hit_without_rayjoin_names(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for text in (prelude, api):
            self.assertIn("RtdlSegmentFirstHitRow", text)
            self.assertIn("rtdl_optix_run_prepared_segment_first_hit", text)
            self.assertIn("rtdl_optix_count_prepared_segment_first_hit", text)
            self.assertNotIn("RayJoin", text)
            self.assertNotIn("rayjoin", text)

    def test_optix_kernel_keeps_one_bounded_witness_per_probe_on_device(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("kSegmentFirstHitKernelSrc", core)
        self.assertIn("SegmentFirstHitParams", core)
        self.assertIn("atomicCAS", core)
        self.assertIn("best_pair", core)
        self.assertIn("ensure_segment_first_hit_pipeline", workloads)
        self.assertIn("collect_segment_first_hits_optix", workloads)
        self.assertIn("materialize_segment_first_hit_rows", workloads)
        self.assertNotIn("query=pip", core)
        self.assertNotIn("RayJoin", core)

    def test_python_binding_exposes_generic_prepared_first_hit_methods(self) -> None:
        runtime = PY_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("class _RtdlSegmentFirstHitRow", runtime)
        self.assertIn("def first_hit_raw", runtime)
        self.assertIn("def first_hit_count", runtime)
        self.assertIn('"rtdl_optix_run_prepared_segment_first_hit"', runtime)
        self.assertIn('"rtdl_optix_count_prepared_segment_first_hit"', runtime)
        self.assertIn('"first_hit_rows"', runtime)
        self.assertIn('"first_hit_count"', runtime)
        self.assertIn('"device_witness_materialize"', runtime)

    def test_rayjoin_runner_uses_first_hit_as_application_mapping_only(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("prepared.first_hit_raw", script)
        self.assertIn("rtdl.rayjoin.pip_first_hit_comparison.v1", script)
        self.assertIn("generic_segment_first_hit_primitive_measured", script)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized", script)
        self.assertIn("False", script)

    def test_pod_artifacts_show_correctness_and_v2_1_speedup_boundary(self) -> None:
        expected = {
            4096: 3374,
            65536: 53372,
        }
        for scale, positives in expected.items():
            with self.subTest(scale=scale):
                payload = json.loads(
                    (ARTIFACTS / f"rtdl_first_hit_pip_compare_{scale}.json").read_text(encoding="utf-8")
                )
                self.assertEqual(payload["schema"], "rtdl.rayjoin.pip_first_hit_comparison.v1")
                self.assertTrue(payload["all_same_positive_point_set"])
                self.assertEqual(payload["runs"][0]["rayjoin_positive_count"], positives)
                self.assertEqual(payload["runs"][0]["rtdl_unique_positive_count"], positives)
                self.assertEqual(payload["runs"][0]["missing_count"], 0)
                self.assertEqual(payload["runs"][0]["extra_count"], 0)
                self.assertGreater(payload["v2_1_speedup_over_v2_0_vertical_probe"], 10.0)
                self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
                self.assertFalse(payload["claim_boundary"]["v2_1_release_authorized"])

    def test_report_names_v2_1_boundary_without_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v2.1-candidate-evidence-collected", text)
        self.assertIn("60.30x", text)
        self.assertIn("1.91x slower", text)
        self.assertIn("does not require user-defined shader injection", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL beats RayJoin", text)


if __name__ == "__main__":
    unittest.main()
