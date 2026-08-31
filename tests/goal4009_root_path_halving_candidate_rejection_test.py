from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
BASELINE = ROOT / "docs" / "reports" / "goal4007_grouped_union_root_read_telemetry_pod"
CANDIDATE = ROOT / "docs" / "reports" / "goal4009_root_path_halving_candidate_pod"
ACCEPTED_APP = ROOT / "docs" / "reports" / "goal4002_direct_side_effect_app_probe_pod"
CANDIDATE_APP = ROOT / "docs" / "reports" / "goal4009_root_path_halving_app_signature_pod"
REPORT = ROOT / "docs" / "reports" / "goal4009_root_path_halving_candidate_rejection_2026-06-08.md"


class Goal4009RootPathHalvingCandidateRejectionTest(unittest.TestCase):
    def _default_variant(self, directory: pathlib.Path, filename: str) -> dict[str, object]:
        payload = json.loads((directory / filename).read_text(encoding="utf-8"))
        return next(
            variant for variant in payload["rows"][0]["variants"]
            if variant["label"] == "same_root_on_direct_off"
        )

    def test_raw_candidate_reduces_root_steps_but_is_not_sufficient(self) -> None:
        for filename in ("clustered3d_65536.json", "road3d_65536.json", "ngsim_dense_65536.json"):
            baseline = self._default_variant(BASELINE, filename)
            candidate = self._default_variant(CANDIDATE, filename)
            baseline_steps = baseline["last_telemetry"][9]
            candidate_steps = candidate["last_telemetry"][9]
            self.assertLess(candidate_steps, baseline_steps)
            self.assertLess(
                float(candidate["median_native_elapsed_sec"]),
                float(baseline["median_native_elapsed_sec"]),
            )

    def test_app_signature_gate_rejects_candidate(self) -> None:
        clustered_default = json.loads((ACCEPTED_APP / "clustered3d_default.json").read_text(encoding="utf-8"))
        clustered_candidate = json.loads((CANDIDATE_APP / "clustered3d_candidate.json").read_text(encoding="utf-8"))
        self.assertNotEqual(clustered_default["signature"], clustered_candidate["signature"])
        self.assertGreater(
            float(clustered_candidate["elapsed_sec"]) / float(clustered_default["elapsed_sec"]),
            1.1,
        )
        for profile in ("road3d", "ngsim_dense"):
            default = json.loads((ACCEPTED_APP / f"{profile}_default.json").read_text(encoding="utf-8"))
            candidate = json.loads((CANDIDATE_APP / f"{profile}_candidate.json").read_text(encoding="utf-8"))
            self.assertEqual(default["signature"], candidate["signature"])

    def test_committed_source_keeps_root_find_readonly(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        root_helper = core.split("int find_grouped_union_root_readonly", 1)[1].split(
            "extern \"C\" __device__\nvoid union_grouped_min_root", 1
        )[0]
        self.assertIn("root = parent[root];", root_helper)
        self.assertNotIn("const int grand = parent[next];", root_helper)
        self.assertNotIn("atomicMin(parent + root, grand);", root_helper)

    def test_report_records_rejection_without_overclaim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`reject-as-default`",
            "raw telemetry speed is not a substitute",
            "Do not promote root path halving",
            "partition-convergence hybrid",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
