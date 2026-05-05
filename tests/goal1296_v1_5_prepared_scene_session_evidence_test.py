from __future__ import annotations

import unittest

from scripts import goal1296_v1_5_prepared_scene_session_evidence as goal1296


class _PreparedScene:
    enter_count = 0
    exit_count = 0

    def __enter__(self):
        type(self).enter_count += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        type(self).exit_count += 1

    def count(self, rays) -> int:
        return int(rays.count // 2)


class _PreparedRays:
    enter_count = 0

    def __init__(self, rays) -> None:
        self.count = len(rays)

    def __enter__(self):
        type(self).enter_count += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


class Goal1296V15PreparedSceneSessionEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        _PreparedScene.enter_count = 0
        _PreparedScene.exit_count = 0
        _PreparedRays.enter_count = 0

    def test_payload_records_one_scene_for_multiple_batches(self) -> None:
        payload = goal1296.build_payload(
            copies=4,
            query_repeats=3,
            prepare_scene=lambda _triangles: _PreparedScene(),
            prepare_rays=lambda rays: _PreparedRays(rays),
        )

        self.assertEqual(_PreparedScene.enter_count, 1)
        self.assertEqual(_PreparedScene.exit_count, 1)
        self.assertEqual(_PreparedRays.enter_count, 2)
        self.assertTrue(payload["scene_prepare_paid_once"])
        self.assertTrue(payload["all_batches_match_cpu"])
        self.assertEqual(payload["fixture"]["batch_count"], 2)
        self.assertEqual(payload["fixture"]["query_repeats_per_batch"], 3)
        self.assertEqual([row["query_batch_index"] for row in payload["batch_results"]], [1, 2])
        self.assertEqual([row["hit_count"] for row in payload["batch_results"]], [2, 2])
        self.assertFalse(payload["public_wording_authorized"])
        self.assertEqual(payload["frozen_backends_before_v2_1"], ["vulkan", "hiprt", "apple_rt"])

    def test_rejects_invalid_scale_and_repeats(self) -> None:
        with self.assertRaisesRegex(ValueError, "copies must be greater than 1"):
            goal1296.build_payload(copies=1, query_repeats=1)
        with self.assertRaisesRegex(ValueError, "query_repeats must be positive"):
            goal1296.build_payload(copies=2, query_repeats=0)


if __name__ == "__main__":
    unittest.main()
