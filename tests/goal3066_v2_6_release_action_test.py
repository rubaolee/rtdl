from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3066_v2_6_release_action_2026-06-02.md"
RELEASE_README = ROOT / "docs" / "release_reports" / "v2_6" / "README.md"


EXCLUDED_CURRENT_PREFIXES = (
    "docs/history/",
    "docs/reports/",
    "docs/reviews/",
    "docs/handoff/",
    "docs/audit/",
    "docs/release_reports/",
    "docs/directives/",
    "docs/engineering/",
    "docs/research/archive/",
    "examples/generated/",
    "history/examples_internal/",
    "examples/legacy_or_backend_proofs/",
    "examples/reference/",
)


CURRENT_PUBLIC_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/current_architecture.md",
    "docs/current_main_support_matrix.md",
    "docs/backend_maturity.md",
    "docs/capability_boundaries.md",
    "docs/partner_acceleration_boundaries.md",
    "docs/release_facing_examples.md",
    "docs/tutorials/README.md",
    "examples/README.md",
    "examples/current/README.md",
)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _current_docs() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / "examples").rglob("*.md"))
    out: list[Path] = []
    for path in files:
        rel = _rel(path)
        if not any(rel.startswith(prefix) for prefix in EXCLUDED_CURRENT_PREFIXES):
            out.append(path)
    return sorted(out)


class Goal3066V26ReleaseActionTest(unittest.TestCase):
    def test_version_marker_is_v2_6(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v2.6")

    def test_release_action_records_authorized_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("v2_6_source_tree_python_partner_rtdl_release_action_authorized", text)
        self.assertIn("user explicitly authorized the v2.6 release", text)
        self.assertIn("tag the committed tree as `v2.6`", text)
        self.assertIn("does not claim package-install support", text)
        self.assertIn("automatic partner selection", text)
        self.assertIn("Goal3065", text)

    def test_front_door_docs_now_name_current_release(self) -> None:
        for rel in CURRENT_PUBLIC_DOCS:
            with self.subTest(rel=rel):
                text = (ROOT / rel).read_text(encoding="utf-8")
                self.assertIn("v2.6", text)
                self.assertNotIn("release-candidate", text.lower())
                self.assertNotIn("release candidate", text.lower())
                self.assertNotIn("pre-release", text.lower())

    def test_current_docs_no_longer_expose_candidate_status(self) -> None:
        forbidden = (
            "release-candidate",
            "release candidate",
            "pre-release",
            "release-prep",
            "current v2.3 release",
            "v2.3 users first",
        )
        offenders: list[str] = []
        for path in _current_docs():
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for phrase in forbidden:
                if phrase in text:
                    offenders.append(f"{_rel(path)}:{phrase}")

        self.assertEqual([], offenders)

    def test_release_package_is_source_tree_only_and_evidence_linked(self) -> None:
        text = RELEASE_README.read_text(encoding="utf-8")

        self.assertIn("Version marker: `v2.6`", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("not a package-install release", text)
        self.assertIn("not a broad RT-core", text)
        self.assertIn("not a whole-application speedup claim", text)
        self.assertIn("user-chosen partner guidance", text)

        for goal in ("Goal3058", "Goal3061", "Goal3062", "Goal3065"):
            self.assertIn(goal.lower().replace("goal", "goal"), text.lower())

    def test_protected_local_files_are_named_for_exclusion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for protected in (
            "docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz",
            "id_ed25519_rtdl_codex",
            "rtdl_v0_4.tar.gz",
            "scratch/",
            "Lib/",
        ):
            self.assertIn(protected, text)


if __name__ == "__main__":
    unittest.main()
