import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1711_optix_source_recovery_and_linux_build_validation_2026-05-12.md"
)
OPTIX = ROOT / "src" / "native" / "optix"


class Goal1711OptixSourceRecoveryAndLinuxBuildValidationTest(unittest.TestCase):
    def _optix_text(self) -> str:
        return "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in OPTIX.glob("*")
            if path.is_file()
        )

    def test_optix_sources_are_not_truncated(self):
        api = (OPTIX / "rtdl_optix_api.cpp").read_text(encoding="utf-8", errors="ignore")
        prelude = (OPTIX / "rtdl_optix_prelude.h").read_text(
            encoding="utf-8", errors="ignore"
        )
        workloads = (OPTIX / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertTrue(api.rstrip().endswith("}"))
        self.assertTrue(prelude.rstrip().endswith('} // extern "C"'))
        self.assertTrue(workloads.rstrip().endswith("}"))
        self.assertNotIn("std::st\n", workloads)
        self.assertIn("rtdl_optix_free_rows", api)

    def test_stale_optix_replay_artifacts_are_absent(self):
        text = self._optix_text()
        for stale in (
            "pose",
            "db_copy_dataset_table",
            "DB columnar inputs must not be null",
            "field_index_count",
            "rtdl_optix_db_dataset",
            "rtdl_optix_run_lsi",
            "rtdl_optix_run_overlay",
            "rtdl_optix_run_triangle_probe",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text.lower())

    def test_report_records_linux_build_and_release_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "192.168.1.20",
            "make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev",
            "build/librtdl_optix.so 792480 bytes",
            "Ran 30 tests",
            "Ran 83 tests",
            "Ran 34 tests",
            "needs-more-evidence",
            "does not provide accepted pod performance or release hardware evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
