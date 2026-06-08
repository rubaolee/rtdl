from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from unittest.mock import patch
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3866_rayjoin_representative_scale_profile.py"
REPORT = ROOT / "docs" / "reports" / "goal3907_rayjoin_wrapper_phase_timing_2026-06-08.md"


def _fake_case(workload: str, *, numba_sec: float, optix_sec: float) -> dict[str, object]:
    return {
        "workload": workload,
        "dataset": f"{workload}.cdb",
        "counts_match": True,
        "numba_cuda_jit_baseline": {"hot_median_sec": numba_sec},
        "rtdl_optix": {"hot_median_sec": optix_sec},
    }


class Goal3907RayJoinWrapperPhaseTimingTest(unittest.TestCase):
    def test_representative_profile_emits_wrapper_phase_timing_sec(self) -> None:
        import scripts.goal3866_rayjoin_representative_scale_profile as profile
        from scripts.goal3828_current_benchmark_scale_profile_runner import _payload_timing_summary

        data_dir = ROOT / "scratch" / "goal3907_fake_rayjoin_data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / profile.PIP_DATASET_NAME).write_text("", encoding="utf-8")
        (data_dir / profile.SOIL_DATASET_NAME).write_text("", encoding="utf-8")
        args = Namespace(
            data_dir=str(data_dir),
            repeat=2,
            warmup=1,
            block_size=64,
            pip_batch_query_axis="z_point",
            pip_batch_boundary_mode="inclusive",
            pip_batch_device_predicate_eps="1e-9",
            pip_batch_stream_count="auto",
            pip_batch_single_warmup=1,
            pip_batch_single_repeat=2,
            pip_batch_warmup=1,
            pip_batch_repeat=2,
            pip_batch_request_counts=[1, 8],
        )
        fake_pip = {
            **_fake_case("pip", numba_sec=0.001, optix_sec=0.004),
            "summary": {"numba_row_count": 7},
        }
        fake_lsi_overlay = {
            "summary": {"all_counts_match": True},
            "rows": [
                _fake_case("lsi", numba_sec=0.020, optix_sec=0.0001),
                _fake_case("overlay_seed", numba_sec=0.050, optix_sec=0.0002),
            ],
        }
        fake_batch = {
            "dataset": str(data_dir / profile.PIP_DATASET_NAME),
            "exact_count": 7,
            "point_count": 8,
            "shape_count": 8,
            "single_ms_median": 0.2,
            "batch_rows": [
                {
                    "request_count": 8,
                    "per_request_ms_median": 0.025,
                    "total_ms_median": 0.2,
                    "batch_stream_count_effective": 4,
                }
            ],
        }

        with (
            patch.object(profile, "run_pip_probe", return_value=fake_pip),
            patch.object(profile, "run_lsi_overlay_probe", return_value=fake_lsi_overlay),
            patch.object(profile, "run_pip_batch_probe", return_value=fake_batch),
        ):
            payload = profile.run_representative_profile(args)

        phases = payload["wrapper_phase_timing_sec"]
        for key in (
            "data_dir_resolve_sec",
            "pip_one_shot_probe_sec",
            "lsi_overlay_probe_sec",
            "pip_batch_probe_sec",
            "profile_total_sec",
        ):
            self.assertIn(key, phases)
            self.assertGreaterEqual(phases[key], 0.0)
        self.assertAlmostEqual(phases["profile_total_sec"], payload["wrapper_elapsed_sec"])

        timing_summary = _payload_timing_summary(payload)
        paths = {item["path"] for item in timing_summary["timing_scalars_sample"]}
        self.assertIn("$.wrapper_phase_timing_sec.profile_total_sec", paths)
        self.assertIn("$.wrapper_phase_timing_sec.pip_batch_probe_sec", paths)

    def test_report_and_script_preserve_boundaries(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn('"wrapper_phase_timing_sec"', source)
        self.assertIn("automatic_partner_selection_authorized", source)
        self.assertIn("instrumentation-only", report)
        self.assertIn("does not authorize release action", report)
        self.assertIn("not a public performance comparison", report)


if __name__ == "__main__":
    unittest.main()
