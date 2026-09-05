from __future__ import annotations

import unittest

from experiments.goal5848_strong_baseline.aot_requests import (
    request_for_task,
    target_sha256,
)
from experiments.goal5848_strong_baseline.contracts import (
    RELATION_TASK,
    TRIANGLE_TASK,
)


class Goal5848AOTRequestTest(unittest.TestCase):
    @staticmethod
    def _request(task):
        return request_for_task(
            task,
            source_commit="a" * 40,
            source_tree="b" * 40,
            native_library_sha256="1" * 64,
            native_build_manifest_sha256="2" * 64,
            optix_sdk="9.0.0",
            compute_capability="8.9",
            python_version="3.12.14",
            numba_version="0.65.1",
            numpy_version="2.4.4",
            llvmlite_version="0.47.0",
            cuda_toolkit_version="12.9",
            build_roots={"link_options": ["max_trace_depth=1"]},
            trust_root_file_sha256="3" * 64,
        )

    def test_relation_and_triangle_requests_are_distinct_and_stable(self):
        relation = self._request(RELATION_TASK)
        triangle = self._request(TRIANGLE_TASK)
        self.assertNotEqual(relation.identity_sha256, triangle.identity_sha256)
        self.assertEqual(
            relation.identity_sha256,
            self._request(RELATION_TASK).identity_sha256,
        )
        self.assertEqual(relation.family, "custom_aabb_bounded_relation_v1")
        self.assertEqual(triangle.family, "builtin_triangle_reduction_v1")

    def test_target_identity_matches_frozen_profile_projection(self):
        first = target_sha256(
            native_library_sha256="1" * 64,
            optix_sdk="9.0.0",
            compute_capability="8.9",
        )
        second = target_sha256(
            native_library_sha256="1" * 64,
            optix_sdk="9.0.0",
            compute_capability="8.9",
        )
        changed = target_sha256(
            native_library_sha256="1" * 64,
            optix_sdk="9.0.0",
            compute_capability="8.6",
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_trust_root_file_identity_changes_exact_request(self):
        request = self._request(RELATION_TASK)
        changed = request_for_task(
            RELATION_TASK,
            source_commit="a" * 40,
            source_tree="b" * 40,
            native_library_sha256="1" * 64,
            native_build_manifest_sha256="2" * 64,
            optix_sdk="9.0.0",
            compute_capability="8.9",
            python_version="3.12.14",
            numba_version="0.65.1",
            numpy_version="2.4.4",
            llvmlite_version="0.47.0",
            cuda_toolkit_version="12.9",
            build_roots={"link_options": ["max_trace_depth=1"]},
            trust_root_file_sha256="4" * 64,
        )
        self.assertNotEqual(request.identity_sha256, changed.identity_sha256)


if __name__ == "__main__":
    unittest.main()
