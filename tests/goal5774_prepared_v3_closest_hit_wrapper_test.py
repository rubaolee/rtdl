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

from rtdsl.generic_primitives import (  # noqa: E402
    GenericPreparedRayTriangleClosestHit3D,
    Ray3D,
    Triangle3D,
)


TRIANGLES = (
    Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
)
RAYS_A = (Ray3D(0, 0.1, 0.1, -1.0, 0.0, 0.0, 1.0, 2.0),)
RAYS_B = (Ray3D(1, 0.2, 0.2, -1.0, 0.0, 0.0, 1.0, 2.0),)


class _FakeScene:
    def __init__(self):
        self.binding_epoch = 1
        self.closed = False
        self.calls = []
        self.last_closest_hit_metadata = {}

    def compiler_native_resource_binding_metadata(self):
        return {
            "native_context_identity_digest": "5" * 64,
            "native_context_binding_digest": "6" * 64,
            "handle_value": 29,
            "binding_epoch": self.binding_epoch,
        }

    def ray_closest_hit_rows(self, rays):
        self.calls.append(tuple(ray.id for ray in rays))
        self.last_closest_hit_metadata = {
            "native_symbol": "fake_closest_hit",
            "prepared_scene_used": True,
        }
        return tuple(
            {"ray_id": ray.id, "triangle_id": 0, "t": 1.0}
            for ray in rays
        )

    def close(self):
        self.closed = True


class Goal5774PreparedV3ClosestHitWrapperTest(unittest.TestCase):
    def _owner(self):
        scene = _FakeScene()
        patcher = patch(
            "rtdsl.optix_runtime.prepare_optix_static_triangle_scene_3d",
            return_value=scene,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        owner = GenericPreparedRayTriangleClosestHit3D(TRIANGLES)
        self.addCleanup(owner.close)
        return scene, owner

    def test_compiler_contract_and_two_dynamic_calls_share_scene(self):
        scene, owner = self._owner()
        first = owner.execute(RAYS_A)
        second = owner.execute(RAYS_B)
        self.assertEqual((0,), scene.calls[0])
        self.assertEqual((1,), scene.calls[1])
        self.assertEqual(2, owner.lifecycle_receipt["run_count"])
        contract = first["compiler_contract"]
        self.assertEqual("ray_triangle_closest_hit", contract["predicate"])
        self.assertEqual(("ray_id", "triangle_id", "t"), tuple(contract["emit_fields"]))
        self.assertEqual(
            "prepared_optix_static_triangle_scene_3d_closest_hit_rows",
            contract["canonical_provider"],
        )
        self.assertEqual(0, first["rows"][0]["triangle_id"])
        self.assertEqual(1.0, second["rows"][0]["t"])

    def test_prepared_execute_never_calls_cold_generic_frontdoor(self):
        _, owner = self._owner()
        with patch(
            "rtdsl.generic_primitives.run_generic_ray_triangle_closest_hit",
            side_effect=AssertionError("cold generic front door called"),
        ):
            self.assertEqual(1, len(owner.execute(RAYS_A)["rows"]))

    def test_lifetime_identity_and_type_attacks_fail_closed(self):
        scene, owner = self._owner()
        with self.assertRaises(TypeError):
            pickle.dumps(owner)
        with patch(
            "rtdsl.generic_primitives.os.getpid", return_value=os.getpid() + 1
        ):
            with self.assertRaisesRegex(RuntimeError, "process mismatch"):
                owner.execute(RAYS_A)
        with patch(
            "rtdsl.generic_primitives.threading.get_ident",
            return_value=owner._owner_thread_id + 1,
        ):
            with self.assertRaisesRegex(RuntimeError, "thread mismatch"):
                owner.execute(RAYS_A)
        with self.assertRaisesRegex(TypeError, "Ray3D"):
            owner.execute((object(),))
        scene.binding_epoch = 2
        with self.assertRaisesRegex(RuntimeError, "identity invalid"):
            owner.execute(RAYS_A)
        scene.binding_epoch = 1

    def test_reentrancy_close_and_use_after_close_fail_closed(self):
        _, owner = self._owner()
        owner._executing = True
        with self.assertRaisesRegex(RuntimeError, "reentrant"):
            owner.execute(RAYS_A)
        owner._executing = False
        owner.close()
        self.assertTrue(owner.closed)
        with self.assertRaisesRegex(RuntimeError, "closed"):
            owner.execute(RAYS_A)

    def test_core_has_no_application_identity_dispatch(self):
        source = (SRC / "rtdsl" / "generic_primitives.py").read_text()
        body = source.split("class GenericPreparedRayTriangleClosestHit3D:", 1)[1]
        body = body.split("def prepare_generic_ray_triangle_closest_hit_scene_3d", 1)[0]
        lowered = body.lower()
        for forbidden in (
            "particle_tracking", "paper_algorithm", "dataset", "lane_id",
            "triangle_counting", "rayjoin", "arkade",
        ):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
