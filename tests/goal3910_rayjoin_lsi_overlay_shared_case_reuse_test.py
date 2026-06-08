from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest


from scripts import goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline as probe


class Goal3910RayJoinLsiOverlaySharedCaseReuseTest(unittest.TestCase):
    def test_run_probe_loads_case_once_and_marks_loaded_reuse(self) -> None:
        calls = {"load": 0, "numba": 0, "rtdl": 0}

        def fake_load_case(*args, **kwargs):
            calls["load"] += 1
            return SimpleNamespace(note="loaded once", inputs={"left": (), "right": ()})

        def fake_numba_loaded(*args, **kwargs):
            calls["numba"] += 1
            self.assertTrue(kwargs["case_loaded_by_caller"])
            return {
                "load_case_sec": kwargs["load_case_sec"],
                "case_loaded_by_caller": True,
                "prepare_sec": 0.10,
                "hot_median_sec": 0.20,
                "hot_total_sec": 0.40,
                "row_count": 5,
                "claim_boundary": {"release_authorized": False},
            }

        def fake_rtdl_loaded(*args, **kwargs):
            calls["rtdl"] += 1
            self.assertEqual(kwargs["case"].note, "loaded once")
            return {
                "execution_route": "prepared_optix_left_id_dense_count_loaded_case_reuse",
                "loaded_case_reuse_enabled": True,
                "prepare_sec": {"prepare_static_scene_sec": 0.25},
                "hot_median_sec": 0.01,
                "hot_total_sec": 0.02,
                "row_count": 5,
                "claim_boundary": {"release_authorized": False},
            }

        old_load_case = probe._load_rayjoin_case
        old_numba_loaded = probe.run_numba_baseline_loaded_case
        old_rtdl_loaded = probe.run_rtdl_optix_loaded_case
        try:
            probe._load_rayjoin_case = fake_load_case
            probe.run_numba_baseline_loaded_case = fake_numba_loaded
            probe.run_rtdl_optix_loaded_case = fake_rtdl_loaded
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir)
                (data_dir / "br_county_start256_count512.cdb").write_text("fake", encoding="utf-8")
                (data_dir / "br_soil_start256_count512.cdb").write_text("fake", encoding="utf-8")
                payload = probe.run_probe(
                    data_dir=data_dir,
                    cases=("lsi_county512_soil512",),
                    repeat=1,
                    warmup=0,
                    block_size=128,
                    skip_cupy=True,
                    skip_optix=False,
                )
        finally:
            probe._load_rayjoin_case = old_load_case
            probe.run_numba_baseline_loaded_case = old_numba_loaded
            probe.run_rtdl_optix_loaded_case = old_rtdl_loaded

        self.assertEqual(calls, {"load": 1, "numba": 1, "rtdl": 1})
        self.assertTrue(payload["summary"]["shared_loaded_case_reuse_enabled"])
        row = payload["rows"][0]
        self.assertEqual(row["rtdl_optix"]["execution_route"], "prepared_optix_left_id_dense_count_loaded_case_reuse")
        self.assertTrue(row["rtdl_optix"]["loaded_case_reuse_enabled"])
        self.assertGreaterEqual(row["wrapper_phase_timing_sec"]["shared_load_case_sec"], 0.0)

    def test_loaded_case_helpers_keep_old_standalone_wrapper_available(self) -> None:
        text = Path(probe.__file__).read_text(encoding="utf-8")
        self.assertIn("def run_numba_baseline_loaded_case", text)
        self.assertIn("def run_rtdl_optix_loaded_case", text)
        self.assertIn("shared_loaded_case_reuse_enabled", text)
        self.assertIn("prepared_optix_left_id_dense_count_loaded_case_reuse", text)
        self.assertIn("prepared_optix_shape_pair_active_count_loaded_case_reuse", text)
        self.assertIn("return run_rtdl_optix(workload, dataset", text)


if __name__ == "__main__":
    unittest.main()
