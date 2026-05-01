from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal1176_pod_archive_batch_executor.sh"


class Goal1176PodArchiveBatchExecutorTest(unittest.TestCase):
    def test_executor_verifies_archive_before_extracting(self):
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("sha256sum", text)
        self.assertIn("Archive SHA256 mismatch", text)
        self.assertLess(text.index("Archive SHA256 mismatch"), text.index("tar -xzf"))

    def test_executor_runs_prepared_batch_and_packages_results(self):
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("git init", text)
        self.assertIn("git commit -m \"Goal1176 staged source archive\"", text)
        self.assertIn("RTDL_SOURCE_COMMIT=\"goal1175-archive-${EXPECTED_SHA256}\"", text)
        self.assertIn("docs/reports/", text)
        self.assertIn("goal1170_clean_source_rtx_batch_manifest.py", text)
        self.assertLess(
            text.index("goal1170_clean_source_rtx_batch_manifest.py"),
            text.index("make build-optix"),
        )
        self.assertIn("make build-optix", text)
        self.assertIn("goal1170_clean_source_rtx_batch_runner.sh", text)
        self.assertIn("goal1170_clean_source_rtx_claim_grade_batch", text)
        self.assertIn("goal1176_goal1170_results.tgz", text)


if __name__ == "__main__":
    unittest.main()
