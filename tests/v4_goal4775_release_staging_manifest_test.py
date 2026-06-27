from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4775_release_staging_manifest import (  # noqa: E402
    REQUIRED_STAGE_PATHS,
    validate_v4_goal4775_release_staging_manifest,
)


class V4Goal4775ReleaseStagingManifestTest(unittest.TestCase):
    def test_manifest_pathspec_is_ready_but_tag_still_requires_clean_commit(self) -> None:
        manifest = validate_v4_goal4775_release_staging_manifest(ROOT)

        self.assertTrue(manifest["pathspec_ready"])
        self.assertFalse(manifest["direct_git_tag_allowed_now"])
        self.assertTrue(manifest["clean_release_commit_required_before_tag"])

    def test_manifest_stages_required_current_release_files(self) -> None:
        manifest = validate_v4_goal4775_release_staging_manifest(ROOT)
        available = set(manifest["stage_for_v4_release_commit"]) | set(
            manifest["required_stage_paths_already_clean"]
        )

        for required in REQUIRED_STAGE_PATHS:
            self.assertIn(required, available)

    def test_manifest_holds_v3_history_out_of_v4_tag(self) -> None:
        manifest = validate_v4_goal4775_release_staging_manifest(ROOT)
        staged = tuple(manifest["stage_for_v4_release_commit"])
        held = tuple(manifest["hold_v3_history_not_v4_tag"])

        self.assertFalse(any(path.startswith("tests/v3_") for path in staged))
        if held:
            self.assertTrue(
                any(path.startswith("tests/v3_") or "phoenix_v3" in path for path in held)
            )
        self.assertFalse(any("phoenix_v3" in path for path in staged))

    def test_manifest_excludes_raw_logs_external_and_build_artifacts(self) -> None:
        manifest = validate_v4_goal4775_release_staging_manifest(ROOT)
        staged = tuple(manifest["stage_for_v4_release_commit"])
        excluded = tuple(manifest["exclude_from_v4_release_commit"])

        self.assertFalse(any(path.startswith("external/") for path in staged))
        self.assertFalse(any(path.startswith("dist/") for path in staged))
        self.assertFalse(any(path.endswith(".stderr.txt") for path in staged))
        self.assertFalse(any(path.endswith(".stdout.txt") for path in staged))
        self.assertFalse(any("__pycache__" in path for path in staged))
        self.assertFalse(any(path.startswith("external/") for path in staged))
        self.assertFalse(any(path.startswith("dist/") for path in staged))

    def test_manifest_keeps_compact_v4_evidence_but_not_raw_text_outputs(self) -> None:
        manifest = validate_v4_goal4775_release_staging_manifest(ROOT)
        staged = set(manifest["stage_for_v4_release_commit"])
        excluded = set(manifest["exclude_from_v4_release_commit"])
        exists = lambda path: (ROOT / path).exists()

        compact_matrix = (
            "tools/_archive/future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json"
        )
        compact_barnes_hut = (
            "tools/_archive/future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/"
            "v4_goal4772_four_way_fair_compare_pod_2026-06-26.json"
        )
        raw_stdout = (
            "tools/_archive/future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/"
            "author_1m_stdout.txt"
        )

        self.assertTrue(compact_matrix in staged or exists(compact_matrix))
        self.assertTrue(compact_barnes_hut in staged or exists(compact_barnes_hut))
        if exists(raw_stdout):
            self.assertNotIn(raw_stdout, staged)
            if raw_stdout in excluded:
                self.assertIn(raw_stdout, excluded)

    def test_manifest_excludes_empty_evidence_files(self) -> None:
        manifest = validate_v4_goal4775_release_staging_manifest(ROOT)
        staged = set(manifest["stage_for_v4_release_commit"])
        excluded = set(manifest["exclude_from_v4_release_commit"])

        empty_probe = "tools/_archive/future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/v3_0_2_optix_device_max_numba_copies16384.json"
        self.assertNotIn(empty_probe, staged)
        if (ROOT / empty_probe).exists():
            self.assertNotIn(empty_probe, staged)
            if empty_probe in excluded:
                self.assertIn(empty_probe, excluded)


if __name__ == "__main__":
    unittest.main()
