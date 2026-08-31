from __future__ import annotations

import unittest
from unittest import mock

from rtdsl import v4_hierarchy_frontier as hierarchy
from tests.goal5782_canonical_packed_hierarchy_binding_test import (
    _bound_endpoint,
    _row,
)


class Goal5776HierarchySingleMaterializationTest(unittest.TestCase):
    def test_accept_consumes_receipt_bound_rows_without_rehashing(self):
        compiled = mock.Mock()
        compiled.point_count = 1
        compiled.schema.maximum_visits_per_source = 3
        compiled.plan_sha256 = "a" * 64
        endpoint = _bound_endpoint(_row(0))
        rows = endpoint["rows"]
        receipt = {"receipt_sha256": "test-only"}
        binding = hierarchy._bind_canonical_packed_hierarchy_endpoint(
            compiled, endpoint)
        with mock.patch.object(hierarchy, "_verify_receipt") as verify, \
                mock.patch.object(hierarchy, "_digest",
                                  side_effect=AssertionError("packed rows must not use JSON")):
            result = hierarchy._accept_hierarchy_endpoint(
                compiled, endpoint, receipt, binding=binding)
        verify.assert_called_once_with(receipt, binding.output_sha256)
        self.assertEqual(result.rows, rows)
        self.assertEqual(result.output_sha256, binding.output_sha256)


if __name__ == "__main__":
    unittest.main()
