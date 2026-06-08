from __future__ import annotations

from pathlib import Path
import tempfile
import unittest


from scripts import goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline as probe


class Goal3909RayJoinLsiOverlaySubprobePhaseTimingTest(unittest.TestCase):
    def test_run_probe_records_per_case_phase_timing_with_mocked_backends(self) -> None:
        def fake_numba_baseline(*args, **kwargs):
            return {
                "partner": "numba",
                "raw_kernel_required": False,
                "load_case_sec": 0.25,
                "prepare_sec": 0.50,
                "hot_median_sec": 0.020,
                "hot_total_sec": 0.040,
                "row_count": 17,
                "claim_boundary": {"release_authorized": False},
            }

        def fake_cupy_baseline(*args, **kwargs):
            return {
                "prepare_sec": 0.75,
                "hot_median_sec": 0.030,
                "hot_total_sec": 0.060,
                "row_count": 17,
                "claim_boundary": {"release_authorized": False},
            }

        def fake_rtdl_optix(*args, **kwargs):
            return {
                "prepare_sec": {"prepare_build_sec": 1.0, "input_pack_sec": 2.0},
                "hot_median_sec": 0.001,
                "hot_total_sec": 0.002,
                "row_count": 17,
                "claim_boundary": {"release_authorized": False},
            }

        old_numba = probe.run_numba_baseline
        old_cupy = probe.run_cupy_baseline
        old_rtdl = probe.run_rtdl_optix
        try:
            probe.run_numba_baseline = fake_numba_baseline
            probe.run_cupy_baseline = fake_cupy_baseline
            probe.run_rtdl_optix = fake_rtdl_optix
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir)
                (data_dir / "br_county_start256_count512.cdb").write_text("fake", encoding="utf-8")
                (data_dir / "br_soil_start256_count512.cdb").write_text("fake", encoding="utf-8")
                payload = probe.run_probe(
                    data_dir=data_dir,
                    cases=("lsi_county512_soil512",),
                    repeat=2,
                    warmup=1,
                    block_size=128,
                    skip_cupy=False,
                    skip_optix=False,
                )
        finally:
            probe.run_numba_baseline = old_numba
            probe.run_cupy_baseline = old_cupy
            probe.run_rtdl_optix = old_rtdl

        self.assertTrue(payload["summary"]["wrapper_phase_timing_available"])
        row = payload["rows"][0]
        timing = row["wrapper_phase_timing_sec"]
        self.assertGreaterEqual(timing["case_total_sec"], 0.0)
        self.assertEqual(timing["numba_load_case_sec"], 0.25)
        self.assertEqual(timing["numba_prepare_sec"], 0.50)
        self.assertEqual(timing["numba_hot_total_sec"], 0.040)
        self.assertEqual(timing["cupy_prepare_sec"], 0.75)
        self.assertEqual(timing["cupy_hot_total_sec"], 0.060)
        self.assertEqual(timing["rtdl_optix_prepare_total_sec"], 3.0)
        self.assertEqual(timing["rtdl_optix_hot_total_sec"], 0.002)
        self.assertTrue(row["counts_match"])

    def test_script_mentions_wrapper_phase_timing_contract(self) -> None:
        text = Path(probe.__file__).read_text(encoding="utf-8")
        self.assertIn('"wrapper_phase_timing_sec"', text)
        self.assertIn('"numba_load_case_sec"', text)
        self.assertIn('"rtdl_optix_prepare_total_sec"', text)
        self.assertIn('"wrapper_phase_timing_available"', text)


if __name__ == "__main__":
    unittest.main()
