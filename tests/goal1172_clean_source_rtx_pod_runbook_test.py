import unittest

from scripts.goal1172_clean_source_rtx_pod_runbook import build_runbook, to_markdown


class Goal1172CleanSourceRtxPodRunbookTest(unittest.TestCase):
    def test_runbook_has_required_batch_lifecycle(self):
        payload = build_runbook()
        names = [step["name"] for step in payload["steps"]]

        self.assertEqual(
            names,
            [
                "clone_clean_source",
                "install_linux_prerequisites",
                "prepare_optix_headers",
                "build_native_optix",
                "preflight",
                "run_goal1170_batch",
                "package_copyback",
            ],
        )

    def test_runbook_mentions_geos_optix_preflight_and_copyback(self):
        text = to_markdown(build_runbook())

        self.assertIn("libgeos-dev", text)
        self.assertIn("optix-dev", text)
        self.assertIn("goal1171_clean_source_rtx_pod_preflight.py", text)
        self.assertIn("goal1170_clean_source_rtx_batch_runner.sh", text)
        self.assertIn("tar -czf", text)

    def test_runbook_forbids_dirty_tree_claims(self):
        payload = build_runbook()

        self.assertIn("must not be used with a copied dirty tree", payload["boundary"])


if __name__ == "__main__":
    unittest.main()
