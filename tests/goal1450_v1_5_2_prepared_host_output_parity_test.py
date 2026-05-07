from __future__ import annotations

import ctypes
import unittest
from types import SimpleNamespace

from scripts import goal1450_v1_5_2_prepared_host_output_parity as parity


class _CollectKBoundedI64Symbol:
    def __call__(
        self,
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        error,
        error_size,
    ):
        rows = []
        for row_index in range(int(candidate_count)):
            row = tuple(
                int(candidate_rows[row_index * int(row_width) + column_index])
                for column_index in range(int(row_width))
            )
            rows.append(row)
        canonical = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(canonical)
        if len(canonical) > int(row_capacity):
            ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1
            return 0
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for row_index, row in enumerate(canonical):
            for column_index, value in enumerate(row):
                rows_out[row_index * int(row_width) + column_index] = int(value)
        return 0


def _fake_library(symbol_name: str):
    return SimpleNamespace(**{symbol_name: _CollectKBoundedI64Symbol()})


class Goal1450V152PreparedHostOutputParityTest(unittest.TestCase):
    def test_acceptance_package_accepts_matching_embree_and_optix_symbols(self) -> None:
        report = parity.run_acceptance_package(
            backends=("embree", "optix"),
            required_backends=("embree", "optix"),
            backend_libraries={
                "embree": _fake_library("rtdl_embree_collect_k_bounded_i64"),
                "optix": _fake_library("rtdl_optix_collect_k_bounded_i64"),
            },
        )

        self.assertTrue(report["accepted"])
        self.assertEqual(report["backend_summary"]["embree"], {"pass": 4, "fail": 0, "skipped": 0})
        self.assertEqual(report["backend_summary"]["optix"], {"pass": 4, "fail": 0, "skipped": 0})
        self.assertEqual(report["skipped_required"], ())
        self.assertEqual(report["failed"], ())

    def test_acceptance_package_rejects_required_backend_skip(self) -> None:
        report = parity.run_acceptance_package(
            backends=("optix",),
            required_backends=("optix",),
            backend_libraries={},
        )

        if report["backend_summary"]["optix"]["skipped"] == 0:
            self.skipTest("local OptiX backend is available; skip-path rejection is not applicable")
        self.assertFalse(report["accepted"])
        self.assertEqual(len(report["skipped_required"]), 4)

    def test_markdown_keeps_claim_boundary_closed(self) -> None:
        report = parity.run_acceptance_package(
            backends=("embree",),
            backend_libraries={
                "embree": _fake_library("rtdl_embree_collect_k_bounded_i64"),
            },
        )

        rendered = parity.render_markdown(report)

        self.assertIn("## Verdict", rendered)
        self.assertIn("## Run Scope", rendered)
        self.assertIn("## Parity Outcome", rendered)
        self.assertIn("## Claim Boundary", rendered)
        self.assertIn("not a public promotion", rendered)
        self.assertIn("not a performance claim", rendered)
        self.assertIn("not a zero-copy claim", rendered)

    def test_markdown_records_required_skip_reason(self) -> None:
        report = parity.run_acceptance_package(
            backends=("optix",),
            required_backends=("optix",),
            backend_libraries={},
        )

        if report["backend_summary"]["optix"]["skipped"] == 0:
            self.skipTest("local OptiX backend is available; skip-path rendering is not applicable")
        rendered = parity.render_markdown(report)

        self.assertIn("Required backend skips", rendered)
        self.assertIn("Required skip detail: backend=optix", rendered)
        self.assertIn("reason=", rendered)


if __name__ == "__main__":
    unittest.main()
