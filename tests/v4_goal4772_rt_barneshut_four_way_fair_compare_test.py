from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_goal4772_rt_barneshut_four_way_fair_compare.py"
V4_JSON = ROOT / "future" / "v4" / "evidence" / "rt_barneshut_author_reproduction_2026-06-26" / "v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json"
V4_PROFILE = ROOT / "future" / "v4" / "evidence" / "rt_barneshut_author_reproduction_2026-06-26" / "v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl"
AUTHOR_STDOUT = ROOT / "future" / "v4" / "evidence" / "rt_barneshut_author_reproduction_2026-06-26" / "v4_goal4769_author_phase_print_false_10m_stdout.txt"


class V4Goal4772RtBarnesHutFourWayFairCompareTest(unittest.TestCase):
    def test_script_builds_protocol_with_explicit_absent_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            v2 = base / "v2"
            v3 = base / "v3"
            v4 = base / "v4"
            for root in (v2, v3, v4):
                (root / "src" / "rtdsl").mkdir(parents=True)
                (root / "src" / "native" / "optix").mkdir(parents=True)
                (root / "build").mkdir(parents=True)
            (v2 / "src" / "rtdsl" / "app_adapters").mkdir(parents=True)
            (v2 / "src" / "rtdsl" / "app_adapters" / "barnes_hut.py").write_text("# legacy\n", encoding="utf-8")
            (v3 / "src" / "rtdsl" / "app_adapters").mkdir(parents=True)
            (v3 / "src" / "rtdsl" / "app_adapters" / "barnes_hut.py").write_text("# legacy\n", encoding="utf-8")
            (v4 / "src" / "rtdsl" / "rt_barneshut_author_contract.py").write_text("# contract\n", encoding="utf-8")
            (v4 / "src" / "rtdsl" / "v4_rt_barneshut_native_route.py").write_text("# native route\n", encoding="utf-8")
            (v4 / "src" / "native" / "optix" / "rtdl_optix_api.cpp").write_text(
                "\n".join(
                    (
                        "rtdl_optix_prepare_rt_barneshut_author_3d",
                        "rtdl_optix_run_rt_barneshut_author_3d",
                        "rtdl_optix_destroy_rt_barneshut_author_3d",
                    )
                ),
                encoding="utf-8",
            )
            output = base / "out.json"
            proc = subprocess.run(
                (
                    sys.executable,
                    str(SCRIPT),
                    "--author-root",
                    str(base / "author"),
                    "--v2-root",
                    str(v2),
                    "--v3-root",
                    str(v3),
                    "--v4-root",
                    str(v4),
                    "--dataset",
                    "/root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt",
                    "--author-phase-stdout",
                    str(AUTHOR_STDOUT),
                    "--v4-benchmark-json",
                    str(V4_JSON),
                    "--v4-profile-jsonl",
                    str(V4_PROFILE),
                    "--output",
                    str(output),
                ),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
        rows = {row["version"]: row for row in payload["rows"]}
        self.assertEqual("no_same_semantics_author_route", rows["v2_14"]["status"])
        self.assertEqual("no_same_semantics_author_route", rows["v3_0_2"]["status"])
        self.assertEqual("same_semantics_native_rt_core_route_present", rows["v4_0"]["status"])
        self.assertFalse(payload["comparison_policy"]["author_vs_v2_14_allowed"])
        self.assertFalse(payload["comparison_policy"]["author_vs_v3_0_2_allowed"])
        self.assertGreater(payload["fair_ratios"]["v4_author_total_program_over_v4_internal_program"], 1.3)
        self.assertFalse(payload["claim_boundary"]["paper_reproduction_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
