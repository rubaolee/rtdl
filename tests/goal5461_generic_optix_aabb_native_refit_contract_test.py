from __future__ import annotations

import unittest
import inspect
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal5461GenericOptixAabbNativeRefitContractTest(unittest.TestCase):
    def test_mutable_prepare_option_is_only_on_2d_aabb_index(self) -> None:
        from rtdsl.optix_runtime import PreparedOptixAabbIndex2D, PreparedOptixAabbIndex3D

        self.assertIn("allow_update", inspect.signature(PreparedOptixAabbIndex2D.__init__).parameters)
        self.assertNotIn("allow_update", inspect.signature(PreparedOptixAabbIndex3D.__init__).parameters)

    def test_public_contract_separates_refit_from_rebuild(self) -> None:
        contract = rt.MUTABLE_AABB_INDEX_2D_CONTRACT
        self.assertEqual(
            contract["execution_model"],
            "native_fixed_cardinality_refit_or_atomic_snapshot_rebuild",
        )
        self.assertTrue(contract["native_incremental_update"])
        self.assertFalse(contract["native_incremental_insert_delete"])

        cpu = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0),), indexed_ids=(5,), backend="cpu"
        )
        result = cpu.update(((5, (2.0, 2.0, 3.0, 3.0)),))
        self.assertEqual(result["mutation_execution_model"], "atomic_snapshot_rebuild")
        self.assertFalse(cpu.metadata()["native_incremental_update"])
        cpu.close()

    def test_native_abi_and_rollback_are_present(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")

        symbol = "rtdl_optix_refit_prepared_aabb_index_2d"
        sparse_symbol = "rtdl_optix_refit_prepared_aabb_index_2d_slots"
        mutable_prepare_symbol = "rtdl_optix_prepare_mutable_aabb_index_2d"
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn(symbol, runtime)
        self.assertIn(sparse_symbol, prelude)
        self.assertIn(sparse_symbol, api)
        self.assertIn(sparse_symbol, runtime)
        self.assertIn(mutable_prepare_symbol, prelude)
        self.assertIn(mutable_prepare_symbol, api)
        self.assertIn(mutable_prepare_symbol, runtime)
        self.assertIn("OPTIX_BUILD_FLAG_ALLOW_UPDATE", workloads)
        self.assertIn("OPTIX_BUILD_OPERATION_UPDATE", core)
        self.assertIn("rollback could not restore the prepared index", workloads)
        self.assertIn("RTDL_OPTIX_TEST_AABB_REFIT_FAULT", workloads)
        self.assertIn("invalid after failed rollback", workloads)
        self.assertIn("mutation_state_valid = false", workloads)
        self.assertIn("stable ids in prepared slot order", workloads)
        self.assertIn("sparse refit slots must be unique", workloads)

    def test_native_refit_core_is_app_neutral(self) -> None:
        source = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        ).lower()
        begin = source.index("static void refit_prepared_aabb_index_2d_optix")
        end = source.index("struct gpuaabb3d", begin)
        window = source[begin:end]
        for forbidden in ("librts", "rtspatial", "paper", "ray multicast"):
            self.assertNotIn(forbidden, window)

    def test_gate_is_generic_and_keeps_paper_performance_out(self) -> None:
        gate = (
            ROOT / "scripts/goal5461_generic_optix_aabb_native_refit_gate.py"
        ).read_text(encoding="utf-8").lower()
        self.assertIn("same_host_microbenchmark_speedup", gate)
        self.assertIn('"librts_paper_performance_claimed": false', gate)
        self.assertIn('"embree_used": false', gate)
        self.assertNotIn("author_mutation_probe", gate)


if __name__ == "__main__":
    unittest.main()
