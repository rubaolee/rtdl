from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal4303CurrentSecurityRedactionGuardTest(unittest.TestCase):
    def test_local_secret_shapes_are_ignored_and_absent_from_repo_root(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in (
            "id_ed25519*",
            "*.pem",
            "*.ppk",
            "*.key",
            "/Lib/",
            "/before_*.txt",
            "/rtdl_v0_4.tar.gz",
        ):
            self.assertIn(pattern, gitignore)

        forbidden_root_files = (
            ROOT / "id_ed25519_rtdl_codex",
            ROOT / "id_ed25519",
            ROOT / "id_rsa",
        )
        for path in forbidden_root_files:
            self.assertFalse(path.exists(), f"private-key-shaped file must not live in repo root: {path}")

        for path in (
            ROOT / "before_3958.txt",
            ROOT / "rtdl_v0_4.tar.gz",
            ROOT / "Lib",
        ):
            self.assertFalse(path.exists(), f"root debris must stay outside repo root: {path}")

    def test_current_goal_reports_and_handoffs_redact_live_pod_access_details(self) -> None:
        candidates: list[Path] = []
        for base in (ROOT / "docs" / "reports", ROOT / "docs" / "handoff", ROOT / "docs" / "reviews"):
            candidates.extend(
                path
                for path in base.rglob("goal42*")
                if re.match(r"goal42\d", path.name) and path.suffix.lower() in {".md", ".json"}
            )
            candidates.extend(
                path
                for path in base.rglob("goal43*")
                if re.match(r"goal43\d", path.name) and path.suffix.lower() in {".md", ".json"}
            )
            for directory in base.glob("goal42*"):
                if directory.is_dir() and re.match(r"goal42\d", directory.name):
                    candidates.extend(path for path in directory.rglob("*") if path.suffix.lower() in {".md", ".json"})
            for directory in base.glob("goal43*"):
                if directory.is_dir() and re.match(r"goal43\d", directory.name):
                    candidates.extend(path for path in directory.rglob("*") if path.suffix.lower() in {".md", ".json"})
            candidates.extend(path for path in base.glob("*.md") if "GOAL42" in path.name)
            candidates.extend(path for path in base.glob("*.md") if "GOAL43" in path.name)
        patterns = {
            "private_key_header": re.compile(r"BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY"),
            "raw_root_ssh": re.compile(r"ssh\s+root@"),
            "working_key_name": re.compile(r"id_ed25519_rtdl_codex"),
            "windows_identity_file": re.compile(r"--identity-file\s+[A-Za-z]:\\"),
            "raw_ipv4_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        }
        violations: list[str] = []
        for path in sorted(set(candidates)):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in patterns.items():
                if pattern.search(text):
                    violations.append(f"{path.relative_to(ROOT)}:{label}")
        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
