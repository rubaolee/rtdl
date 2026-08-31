from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.goal5751_v4_callback_artifact_cache_test import key
from rtdsl.v4_callback_artifact_cache import (
    CallbackArtifactCacheError,
    materialize_callback_artifact,
)
from rtdsl.v4_prepared_provider import open_v4_callback_provider


class Goal5773V4PreparedProviderTest(unittest.TestCase):
    def test_provider_rehashes_exact_cached_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            current = key()
            materialize_callback_artifact(
                directory,
                current,
                composed_ptx=".version 8.0\n",
                construction_receipt={"leaf_count": 7},
            )
            provider = open_v4_callback_provider(directory, current)
            metadata = provider.to_metadata()
            self.assertEqual(metadata["provider_key_sha256"], current.key_sha256)
            self.assertTrue(metadata["cache_rehashed_before_session_prepare"])
            self.assertFalse(metadata["application_algorithm_selected"])

    def test_post_open_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            current = key()
            materialize_callback_artifact(
                directory,
                current,
                composed_ptx=".version 8.0\n",
                construction_receipt={"leaf_count": 7},
            )
            provider = open_v4_callback_provider(directory, current)
            payload = Path(directory) / current.key_sha256 / "composed.ptx"
            payload.write_text("mutated", encoding="utf-8")
            with self.assertRaises(CallbackArtifactCacheError):
                provider.to_metadata()

    def test_missing_provider_never_compiles_or_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(CallbackArtifactCacheError):
                open_v4_callback_provider(directory, key())


if __name__ == "__main__":
    unittest.main()
