from __future__ import annotations

import os
from pathlib import Path
import pickle
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.action_api import ActionTargetProfile, compile_action_source  # noqa: E402
from rtdsl.action_ray_triangle_scalar_summary import (  # noqa: E402
    CompiledRayTriangleScalarSummary,
    PreparedCompiledRayTriangleScalarSummary,
    RayTriangleScalarProducerKind,
    RayTriangleScalarSummaryError,
)


class _FakeScene:
    def __init__(self, triangles) -> None:
        self.triangle_count = len(triangles)
        self.closed = False
        self.binding_epoch = 1
        self.calls = []

    def compiler_native_resource_binding_metadata(self):
        return {
            "native_context_identity_digest": "1" * 64,
            "native_context_binding_digest": "2" * 64,
            "handle_value": 17,
            "binding_epoch": self.binding_epoch,
        }

    def ray_hit_count_sum(self, rays):
        self.calls.append(("count", tuple(rays)))
        return {"hit_count_sum": 7, "native_symbol": "fake_count"}

    def ray_any_hit_weighted_sum(self, rays, weights):
        self.calls.append(("weighted", tuple(rays), tuple(weights)))
        return {"weighted_hit_sum": 11, "native_symbol": "fake_weighted"}

    def close(self):
        self.closed = True


def _compiled_plan(producer_kind):
    from Paper_reproduction_apps_shim import action_contract, ACTION_SOURCE

    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    target = ActionTargetProfile(
        optix_available=True,
        cpu_reference_available=True,
        profile_source="runtime_capability_probe",
        device_memory_limit_bytes=8 << 30,
        production_selection_policy="compiler_owned_default",
    )
    template = {
        RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D:
            "prepared_optix_triangle_scene_ray_hit_count_sum_3d",
        RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D:
            "prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d",
    }[producer_kind]
    return CompiledRayTriangleScalarSummary(
        compiled=compiled,
        producer_kind=producer_kind,
        backend="optix",
        template=template,
        target_profile=target,
        canonical_resolution={"receipt_sha256": "3" * 64},
        canonical_production_authority={"authority_receipt_sha256": "4" * 64},
    )


class Goal5774PreparedV3TriangleWrapperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        migration_path = (
            ROOT / "Paper-reproduction-apps" / "triangle-counting-paper"
            / "rtdl3_action_migration.py"
        )
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "Paper_reproduction_apps_shim", migration_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load Triangle V3 migration")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    def _owner(self, producer_kind):
        plan = _compiled_plan(producer_kind)
        scene = _FakeScene(("t0", "t1"))
        patcher = patch(
            "rtdsl.action_ray_triangle_scalar_summary."
            "prepare_optix_static_triangle_scene_3d",
            return_value=scene,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        owner = PreparedCompiledRayTriangleScalarSummary(
            plan, triangles=("t0", "t1"))
        self.addCleanup(owner.close)
        return plan, scene, owner

    def test_count_and_weighted_producers_reuse_one_scene(self):
        _, count_scene, count_owner = self._owner(
            RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D)
        first = count_owner.execute(rays=("r0",))
        second = count_owner.execute(rays=("r1", "r2"))
        self.assertEqual((7, 7), (first["scalar_sum"], second["scalar_sum"]))
        self.assertEqual(2, count_owner.lifecycle_receipt["run_count"])
        self.assertEqual(
            [("count", ("r0",)), ("count", ("r1", "r2"))],
            count_scene.calls,
        )

        _, weighted_scene, weighted_owner = self._owner(
            RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D)
        weighted = weighted_owner.execute(rays=("r3", "r4"), ray_weights=(5, 6))
        self.assertEqual(11, weighted["scalar_sum"])
        self.assertEqual(
            [("weighted", ("r3", "r4"), (5, 6))], weighted_scene.calls)

    def test_prepared_execute_never_calls_cold_execute(self):
        plan, _, owner = self._owner(
            RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D)
        with patch.object(
            type(plan), "execute", side_effect=AssertionError("cold execute called")
        ):
            self.assertEqual(7, owner.execute(rays=("r0",))["scalar_sum"])

    def test_lifetime_and_identity_attacks_fail_closed(self):
        _, scene, owner = self._owner(
            RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D)
        with self.assertRaises(TypeError):
            pickle.dumps(owner)
        with patch(
            "rtdsl.action_ray_triangle_scalar_summary.os.getpid",
            return_value=os.getpid() + 1,
        ):
            with self.assertRaisesRegex(
                RayTriangleScalarSummaryError, "PROCESS_MISMATCH"):
                owner.execute(rays=("r0",))
        with patch(
            "rtdsl.action_ray_triangle_scalar_summary.threading.get_ident",
            return_value=owner._owner_thread_id + 1,
        ):
            with self.assertRaisesRegex(
                RayTriangleScalarSummaryError, "THREAD_MISMATCH"):
                owner.execute(rays=("r0",))
        scene.binding_epoch = 2
        with self.assertRaisesRegex(
            RayTriangleScalarSummaryError, "IDENTITY_INVALID"):
            owner.execute(rays=("r0",))
        scene.binding_epoch = 1

    def test_invalid_inputs_reentrancy_and_close_fail_closed(self):
        _, _, owner = self._owner(
            RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D)
        with self.assertRaisesRegex(
            RayTriangleScalarSummaryError, "ONE_WEIGHT_PER_RAY"):
            owner.execute(rays=("r0",), ray_weights=None)
        with self.assertRaisesRegex(
            RayTriangleScalarSummaryError, "RAY_WEIGHT_U64"):
            owner.execute(rays=("r0",), ray_weights=(-1,))
        owner._executing = True
        with self.assertRaisesRegex(
            RayTriangleScalarSummaryError, "REENTRANT"):
            owner.execute(rays=("r0",), ray_weights=(1,))
        owner._executing = False
        owner.close()
        self.assertTrue(owner.closed)
        with self.assertRaisesRegex(
            RayTriangleScalarSummaryError, "CLOSED"):
            owner.execute(rays=("r0",), ray_weights=(1,))

    def test_core_has_no_application_identity_dispatch(self):
        source = (SRC / "rtdsl" / "action_ray_triangle_scalar_summary.py").read_text()
        body = source.split("class PreparedCompiledRayTriangleScalarSummary:", 1)[1]
        body = body.split("def prepare_compiled_ray_triangle_scalar_summary", 1)[0]
        lowered = body.lower()
        for forbidden in (
            "triangle_counting", "rt-1a2", "rt-2a1", "paper_algorithm",
            "dataset", "lane_id",
        ):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
