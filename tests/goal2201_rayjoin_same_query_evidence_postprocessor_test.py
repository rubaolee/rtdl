from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2201_rayjoin_same_query_evidence_report.py"
REPORT = ROOT / "docs" / "reports" / "goal2201_rayjoin_same_query_evidence_postprocessor_2026-05-17.md"
RUNNER = ROOT / "scripts" / "goal2198_rayjoin_same_query_pod_runner.sh"


def _rayjoin_log(*, query_ms: float, build_ms: float, optix_launches: int = 0, intersections: int | None = None) -> str:
    launch_lines = "\n".join("I20260517 rt_engine.cu:554] optixLaunch, [w,h,d] = 100000,1,1" for _ in range(optix_launches))
    intersection_line = f"\nI20260517 run_query.cu:306] Intersections: {intersections} Queue Load Factor: 0.1" if intersections is not None else ""
    return f"""{launch_lines}{intersection_line}
Timing results:
 - Build Index: {build_ms} ms

 - Query: {query_ms} ms
"""


def _rtdl_artifact(workload: str) -> dict[str, object]:
    return {
        "schema": "rtdl.rayjoin.same_query_result.v1",
        "query_stream": f"/tmp/rayjoin_{workload}_stream.json",
        "query_stream_schema": "rtdl.rayjoin.same_query_stream.v1",
        "query_stream_producer": "rayjoin_query_exec_export_patch",
        "workload": workload,
        "query_count": 100000,
        "base_cdb": "/tmp/base.cdb",
        "warmups": 1,
        "repeats": 3,
        "reference_backend": "cpu",
        "reference_row_count": 42,
        "backends": {
            "cpu": {
                "elapsed_sec_values": [0.3, 0.31, 0.32],
                "elapsed_sec_median": 0.31,
                "row_counts": [42, 42, 42],
                "parity_reference_backend": "cpu",
                "all_parity_vs_reference": True,
                "all_parity_vs_cpu_python_reference": True,
                "rt_core_accelerated": False,
            },
            "embree": {
                "elapsed_sec_values": [0.2, 0.21, 0.22],
                "elapsed_sec_median": 0.21,
                "row_counts": [42, 42, 42],
                "parity_reference_backend": "cpu",
                "all_parity_vs_reference": True,
                "all_parity_vs_cpu_python_reference": True,
                "rt_core_accelerated": False,
            },
            "optix": {
                "elapsed_sec_values": [0.1, 0.11, 0.12],
                "elapsed_sec_median": 0.11,
                "row_counts": [42, 42, 42],
                "parity_reference_backend": "cpu",
                "all_parity_vs_reference": True,
                "all_parity_vs_cpu_python_reference": True,
                "rt_core_accelerated": True,
            },
        },
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": True,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }


class Goal2201RayJoinSameQueryEvidencePostprocessorTest(unittest.TestCase):
    def test_postprocessor_parses_logs_and_rtdl_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = pathlib.Path(tmp)
            for workload in ("lsi", "pip"):
                for mode, query_ms, launches in (
                    ("grid", 4.0, 0),
                    ("lbvh", 2.0, 0),
                    ("rt", 1.0, 4),
                ):
                    (artifact_dir / f"rayjoin_{workload}_{mode}.log").write_text(
                        _rayjoin_log(query_ms=query_ms, build_ms=0.5, optix_launches=launches, intersections=7 if workload == "lsi" else None),
                        encoding="utf-8",
                    )
                (artifact_dir / f"rtdl_{workload}_same_rayjoin_stream.json").write_text(
                    json.dumps(_rtdl_artifact(workload), indent=2),
                    encoding="utf-8",
                )

            output_json = artifact_dir / "evidence_summary.json"
            output_md = artifact_dir / "evidence_report.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
            )

            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(summary["rayjoin"]["lsi"]["rt"]["optix_launch_count"], 4)
            self.assertEqual(summary["rayjoin"]["lsi"]["rt"]["intersections"], 7)
            self.assertEqual(summary["rtdl"]["lsi"]["reference_backend"], "cpu")
            self.assertAlmostEqual(summary["derived"]["lsi"]["rayjoin_rt_vs_grid_query_ratio"], 0.25)
            self.assertAlmostEqual(summary["derived"]["pip"]["rtdl_optix_vs_cpu_ratio"], 0.11 / 0.31)
            self.assertFalse(summary["claim_boundary"]["v2_0_release_authorized"])
            self.assertIn("RTDL Same-Stream Replay", output_md.read_text(encoding="utf-8"))

    def test_postprocessor_fails_closed_on_claim_leak(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = pathlib.Path(tmp)
            for workload in ("lsi", "pip"):
                for mode in ("grid", "lbvh", "rt"):
                    (artifact_dir / f"rayjoin_{workload}_{mode}.log").write_text(
                        _rayjoin_log(query_ms=1.0, build_ms=0.5),
                        encoding="utf-8",
                    )
                artifact = _rtdl_artifact(workload)
                if workload == "pip":
                    artifact["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"] = True
                (artifact_dir / f"rtdl_{workload}_same_rayjoin_stream.json").write_text(
                    json.dumps(artifact),
                    encoding="utf-8",
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output-json",
                    str(artifact_dir / "out.json"),
                    "--output-md",
                    str(artifact_dir / "out.md"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("blocked claim key unexpectedly true", result.stderr + result.stdout)

    def test_postprocessor_reports_missing_required_artifacts_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = pathlib.Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output-json",
                    str(artifact_dir / "out.json"),
                    "--output-md",
                    str(artifact_dir / "out.md"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing required RayJoin log", result.stderr + result.stdout)

    def test_report_and_runner_wire_the_postprocessor(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("Fail-Closed Checks", report)
        self.assertIn("query_stream_producer", report)
        self.assertIn("goal2201_rayjoin_same_query_evidence_report.py", runner)
        self.assertIn("evidence_summary.json", runner)
        self.assertIn("evidence_report.md", runner)


if __name__ == "__main__":
    unittest.main()
