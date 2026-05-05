from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1291V15EmbreePreparedParityStatusTest(unittest.TestCase):
    def test_status_keeps_optix_implemented_and_embree_blocked(self) -> None:
        rows = rt.generic_prepared_anyhit_count_backend_status()
        by_backend = {row["backend"]: row for row in rows}

        self.assertEqual(by_backend["optix"]["status"], "implemented")
        self.assertEqual(by_backend["optix"]["role"], "nvidia_rt_target")
        self.assertEqual(by_backend["embree"]["status"], "blocked_pending_scene_probe_split")
        self.assertEqual(by_backend["embree"]["role"], "cpu_rt_baseline_and_fallback")

    def test_frozen_backends_remain_inactive(self) -> None:
        rows = rt.generic_prepared_anyhit_count_backend_status()
        by_backend = {row["backend"]: row for row in rows}

        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                self.assertEqual(by_backend[backend]["status"], "frozen_before_v2_1")
                self.assertEqual(by_backend[backend]["role"], "compatibility_or_inactive")
                self.assertEqual(by_backend[backend]["api"], "not_applicable")

    def test_status_does_not_authorize_public_wording(self) -> None:
        for row in rt.generic_prepared_anyhit_count_backend_status():
            with self.subTest(backend=row["backend"]):
                self.assertFalse(row["public_wording_authorized"])

    def test_blockers_capture_embree_and_pod_requirements(self) -> None:
        blockers = "\n".join(rt.generic_prepared_anyhit_count_blockers())

        self.assertIn("Embree", blockers)
        self.assertIn("scene/probe split", blockers)
        self.assertIn("pod run", blockers)
        self.assertIn("frozen before v2.1", blockers)


if __name__ == "__main__":
    unittest.main()
