from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import rtdsl
from rtdsl.canonical_physical_resolution import (
    CanonicalPhysicalResolutionError,
    bind_canonical_provider_to_direct_provider,
    current_canonical_provider_registry,
    resolve_canonical_standalone_provider_for_contract,
)


def _resolve(*, memory_limit_bytes: int = 1 << 30):
    return resolve_canonical_standalone_provider_for_contract(
        statement_stable_id="metric_knn.filter_refine_linf_3d.v1",
        backend_contract_id="nvidia.optix_traversal.v1",
        action_identity={"test_contract": "exact_linf_knn"},
        output_contract={"kind": "exact_ordered_u32_topk"},
        work_domain={"dimensions": 3, "metric": "linf"},
        input_bytes=4096,
        output_bytes=512,
        prepared_bytes=8192,
        logical_cardinality_bound=128,
        pair_cardinality_bound=16_384,
        logical_item_bytes_bound=32,
        pair_item_bytes_bound=8,
        target_identity={"platform": "release-test", "backend": "optix"},
        available_providers=("optix",),
        memory_limit_bytes=memory_limit_bytes,
    )


class V3ReleaseSurfaceTest(unittest.TestCase):
    def test_release_version_is_consistent(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION").read_text(encoding="utf-8").strip(), "v3.0.0")
        self.assertIn('version = "3.0.0"', (root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(rtdsl.__version__, "3.0.0")
        self.assertIn("RTDL 3.0.0", (root / "README.md").read_text(encoding="utf-8"))

    def test_current_registry_has_unique_nonfallback_statement_backend_pairs(self) -> None:
        registry = current_canonical_provider_registry()
        pairs = [
            (row.statement_stable_id, row.backend_contract_id)
            for row in registry.bindings
            if not row.compatibility_fallback
        ]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertGreaterEqual(len(registry.statements), 22)
        self.assertGreaterEqual(len(registry.standalone_providers), 10)

    def test_linf_statement_resolves_to_source_bound_optix_provider(self) -> None:
        receipt = _resolve()
        self.assertEqual(receipt["status"], "RESOLVED")
        self.assertEqual(receipt["provider_namespace"], "standalone_provider")
        self.assertIn("metric_knn_linf_filter_refine_3d/optix", receipt["provider_candidate_stable_id"])
        self.assertFalse(receipt["candidate_executed"])
        self.assertFalse(receipt["cost_or_latency_order_used"])
        self.assertTrue(receipt["behavioral_traversal_receipt_still_required"])

    def test_insufficient_memory_fails_closed(self) -> None:
        with self.assertRaises(CanonicalPhysicalResolutionError):
            _resolve(memory_limit_bytes=1)

    def test_materializer_cannot_substitute_a_different_provider(self) -> None:
        receipt = _resolve()
        with self.assertRaisesRegex(
            CanonicalPhysicalResolutionError,
            "DIRECT_PROVIDER_DIFFERS_FROM_CANONICAL_PROVIDER",
        ):
            bind_canonical_provider_to_direct_provider(
                receipt,
                direct_provider_stable_id="forged/provider",
                direct_execution_contract_sha256="0" * 64,
            )

    def test_application_cannot_supply_provider_or_cost_to_direct_resolver(self) -> None:
        parameters = set(
            inspect.signature(resolve_canonical_standalone_provider_for_contract).parameters
        )
        self.assertNotIn("provider", parameters)
        self.assertNotIn("candidate", parameters)
        self.assertNotIn("cost", parameters)
        self.assertNotIn("latency", parameters)
        self.assertNotIn("callback", parameters)


if __name__ == "__main__":
    unittest.main()
