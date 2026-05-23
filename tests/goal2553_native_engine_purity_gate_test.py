from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2553_native_engine_purity_gate.py"
OPTIX_CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
EMBREE_SCENE = ROOT / "src/native/embree/rtdl_embree_scene.cpp"
EMBREE_API = ROOT / "src/native/embree/rtdl_embree_api.cpp"
REPORT = ROOT / "docs/reports/goal2553_native_app_term_purity_gate_2026-05-23.md"


class Goal2553NativeEnginePurityGateTest(unittest.TestCase):
    def test_active_embree_optix_sources_have_no_benchmark_app_terms(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("purity gate passed", result.stdout)

    def test_internal_predicate_scan_names_are_generic(self) -> None:
        for path in (OPTIX_CORE, OPTIX_WORKLOADS, EMBREE_SCENE, EMBREE_API):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("DbScan", text)
            self.assertNotIn("db_scan", text)
        self.assertIn("ColumnarPredicateScan", OPTIX_CORE.read_text(encoding="utf-8"))
        self.assertIn("columnar_predicate_scan_kernel.cu", OPTIX_WORKLOADS.read_text(encoding="utf-8"))
        self.assertIn("ColumnarPredicateScanRay", EMBREE_SCENE.read_text(encoding="utf-8"))

    def test_gate_catches_reintroduced_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.cpp"
            bad.write_text("int dbscan_should_not_be_native = 1;\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(bad)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("app term `dbscan`", result.stderr)

    def test_report_records_scope_and_remaining_abi_work(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2553", text)
        self.assertIn("ColumnarPredicateScan", text)
        self.assertIn("active Embree/OptiX", text)
        self.assertIn("does not rename the public `RtdlDb*` ABI", text)


if __name__ == "__main__":
    unittest.main()
