from __future__ import annotations

import unittest

from rtdsl.numba_partner_continuation import _NUMBA_KERNEL_CACHE
from rtdsl.numba_partner_continuation import _cached_numba_kernel


class Goal3139NumbaKernelCacheContractTest(unittest.TestCase):
    def test_cache_reuses_kernel_for_same_cuda_module_and_factory(self) -> None:
        class FakeCuda:
            pass

        calls: list[int] = []

        def fake_kernel_factory(cuda):
            calls.append(id(cuda))
            return {"cuda_id": id(cuda), "kernel_index": len(calls)}

        cuda = FakeCuda()
        before = dict(_NUMBA_KERNEL_CACHE)
        try:
            _NUMBA_KERNEL_CACHE.clear()
            first = _cached_numba_kernel(cuda, fake_kernel_factory)
            second = _cached_numba_kernel(cuda, fake_kernel_factory)

            self.assertIs(first, second)
            self.assertEqual(calls, [id(cuda)])
        finally:
            _NUMBA_KERNEL_CACHE.clear()
            _NUMBA_KERNEL_CACHE.update(before)


if __name__ == "__main__":
    unittest.main()
