from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5055_run_v2144_pod_smoke_remote.ps1"


class Goal5055V2144PodSmokeRemoteLauncherTest(unittest.TestCase):
    def test_launcher_runs_strict_goal5052_and_downloads_json(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("goal5052_v2144_public_api_pod_smoke_runner.sh", text)
        self.assertIn("history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json", text)
        self.assertIn("& ssh @sshArgs", text)
        self.assertIn("& scp @scpArgs", text)
        self.assertIn("BatchMode=yes", text)
        self.assertIn("ConnectTimeout=12", text)
        self.assertIn("RemotePythonVenv", text)
        self.assertIn("RemoteCudaHome", text)
        self.assertIn("RemoteRtdlOptixLibrary", text)
        self.assertIn("BootstrapPodEnv", text)
        self.assertIn("goal5057_v2144_strict_pod_smoke_with_env.sh", text)
        self.assertIn("LD_LIBRARY_PATH", text)

    def test_launcher_is_non_destructive(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8").lower()
        forbidden = [
            "rm -rf",
            "git reset",
            "git checkout --",
            "remove-item",
            "del ",
            "rmdir",
        ]
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_launcher_preserves_claim_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("does not claim public release readiness", text)
        self.assertIn("speedup", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("author parity", text)
        self.assertIn("does not create, delete, or reset the remote checkout", text)


if __name__ == "__main__":
    unittest.main()
