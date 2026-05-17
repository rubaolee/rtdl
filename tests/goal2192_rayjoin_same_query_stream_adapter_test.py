from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2192_rayjoin_same_query_stream_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2192_rayjoin_same_query_stream_adapter_2026-05-17.md"
PIP_ARTIFACT = ROOT / "docs" / "reports" / "goal2192_demo_pip_same_query_local_smoke_2026-05-17.json"
LSI_ARTIFACT = ROOT / "docs" / "reports" / "goal2192_demo_lsi_same_query_local_smoke_2026-05-17.json"
FIXTURE = ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb"


def _load_runner():
    spec = importlib.util.spec_from_file_location("goal2192_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load goal2192 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal2192RayjoinSameQueryStreamAdapterTest(unittest.TestCase):
    def test_report_defines_same_query_contract_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("rtdl.rayjoin.same_query_stream.v1", text)
        self.assertIn("rayjoin_query_exec_export_patch", text)
        self.assertIn("same_contract_with_rayjoin_query_exec: false", text)
        self.assertIn("No RTDL native engine code was changed", text)
        self.assertIn("It is not yet RayJoin paper reproduction", text)

    def test_materialize_and_run_pip_stream(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            stream = pathlib.Path(tmp) / "pip_stream.json"
            runner.materialize_demo_stream(
                workload="pip",
                base_cdb=FIXTURE,
                output=stream,
                gen_n=8,
                gen_t=0.1,
                seed=2192,
            )
            loaded = runner.load_query_stream(stream)
            self.assertEqual(loaded["schema"], runner.SCHEMA)
            self.assertEqual(loaded["producer"], "rtdl_demo_generator_not_rayjoin_cpp")
            result = runner.run_stream(
                query_stream=stream,
                backends=("cpu_python_reference", "cpu"),
                warmups=0,
                repeats=1,
            )
        self.assertEqual(result["workload"], "pip")
        self.assertEqual(result["query_count"], 8)
        self.assertFalse(result["claim_boundary"]["same_contract_with_rayjoin_query_exec"])
        for backend in ("cpu_python_reference", "cpu"):
            self.assertEqual(result["backends"][backend]["status"], "ok")
            self.assertTrue(result["backends"][backend]["all_parity_vs_cpu_python_reference"])

    def test_materialize_and_run_lsi_stream(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            stream = pathlib.Path(tmp) / "lsi_stream.json"
            runner.materialize_demo_stream(
                workload="lsi",
                base_cdb=FIXTURE,
                output=stream,
                gen_n=8,
                gen_t=0.5,
                seed=2192,
            )
            result = runner.run_stream(
                query_stream=stream,
                backends=("cpu_python_reference", "cpu"),
                warmups=0,
                repeats=1,
            )
        self.assertEqual(result["workload"], "lsi")
        self.assertEqual(result["query_count"], 8)
        self.assertFalse(result["claim_boundary"]["paper_scale_perf_claim_authorized"])
        for backend in ("cpu_python_reference", "cpu"):
            self.assertEqual(result["backends"][backend]["status"], "ok")
            self.assertTrue(result["backends"][backend]["row_count_consistent"])
            self.assertTrue(result["backends"][backend]["all_parity_vs_cpu_python_reference"])

    def test_checked_in_smoke_artifacts_are_bounded(self) -> None:
        for artifact_path, workload in ((PIP_ARTIFACT, "pip"), (LSI_ARTIFACT, "lsi")):
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
            self.assertEqual(artifact["goal"], "2192")
            self.assertEqual(artifact["workload"], workload)
            self.assertEqual(artifact["query_stream_schema"], "rtdl.rayjoin.same_query_stream.v1")
            self.assertEqual(artifact["query_stream_producer"], "rtdl_demo_generator_not_rayjoin_cpp")
            self.assertFalse(artifact["claim_boundary"]["same_contract_with_rayjoin_query_exec"])
            self.assertFalse(artifact["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
            self.assertTrue(artifact["backends"]["cpu"]["all_parity_vs_cpu_python_reference"])


if __name__ == "__main__":
    unittest.main()
