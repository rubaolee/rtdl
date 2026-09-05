from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.goal5848_strong_baseline import predecessor_worker, worker


class Goal5848PredecessorWorkerTest(unittest.TestCase):
    def test_provider_start_uses_exact_legacy_api_for_predecessor(self):
        calls = []

        class LegacyDeployment:
            def begin_provider_initialization(self, native):
                calls.append((native, {}))
                return "legacy"

        class CurrentDeployment:
            def begin_provider_initialization(self, native, **kwargs):
                calls.append((native, kwargs))
                return "current"

        native = Path("/tmp/native.so")
        self.assertEqual(
            worker._begin_rtdl_provider_initialization(
                LegacyDeployment(),
                native,
                collect_phase_timings=True,
                legacy_provider_timing_api=True,
            ),
            "legacy",
        )
        self.assertEqual(
            worker._begin_rtdl_provider_initialization(
                CurrentDeployment(),
                native,
                collect_phase_timings=True,
                legacy_provider_timing_api=False,
            ),
            "current",
        )
        self.assertEqual(calls, [
            (native, {}),
            (native, {"collect_phase_timings": True}),
        ])

    def test_activate_requires_real_package_without_prior_import(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "src" / "rtdsl"
            package.mkdir(parents=True)
            (package / "v4_rtdlexe.py").write_text("# fixture\n")
            original = list(sys.path)
            prior_rtdsl_modules = {
                name: module
                for name, module in sys.modules.items()
                if name == "rtdsl" or name.startswith("rtdsl.")
            }
            try:
                for name in prior_rtdsl_modules:
                    sys.modules.pop(name)
                source = predecessor_worker._activate_predecessor(root)
                self.assertEqual(Path(sys.path[0]), source)
            finally:
                sys.path[:] = original
                sys.modules.update(prior_rtdsl_modules)

    def test_activate_rejects_preloaded_rtdsl(self):
        with (
            mock.patch.dict(sys.modules, {"rtdsl": mock.Mock()}),
            self.assertRaisesRegex(RuntimeError, "already imported"),
        ):
            predecessor_worker._activate_predecessor(Path("/absent"))

    def test_git_identity_reports_clean_exact_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", root], check=True)
            subprocess.run(
                ["git", "-C", root, "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", root, "config", "user.name", "Goal5848 Test"],
                check=True,
            )
            (root / "tracked").write_text("fixture\n")
            subprocess.run(["git", "-C", root, "add", "tracked"], check=True)
            subprocess.run(
                ["git", "-C", root, "commit", "-qm", "fixture"], check=True
            )
            identity = predecessor_worker._git_identity(root)
            self.assertTrue(identity["clean"])
            self.assertEqual(len(identity["commit"]), 40)


if __name__ == "__main__":
    unittest.main()
