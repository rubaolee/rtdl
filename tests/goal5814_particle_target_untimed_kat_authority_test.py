from __future__ import annotations

import inspect
import unittest
from unittest import mock

from experiments.goal5814_particle import untimed_dual_arm_kat as base
from experiments.goal5814_particle import untimed_dual_arm_kat_rtxa5000_cc86 as target


class Goal5814ParticleTargetUntimedKatAuthorityTest(unittest.TestCase):
    def test_target_authority_is_exact_and_not_lx1(self):
        self.assertEqual(target.TARGET_EXECUTABLE_MANIFEST_BYTES, 6_316)
        self.assertEqual(
            target.TARGET_EXECUTABLE_MANIFEST_SHA256,
            "9b0f0bfb783df30a0799c6943b7623e797ccdc4e4d213fe5500be90db6093145",
        )
        self.assertNotEqual(
            target.TARGET_EXECUTABLE_MANIFEST_SHA256,
            base.FORMAL_EXECUTABLE_MANIFEST_SHA256,
        )

    def test_target_authority_cannot_come_from_cli(self):
        parser_actions = {
            option
            for action in base._argument_parser()._actions
            for option in action.option_strings
        }
        self.assertNotIn("--expected-executable-manifest-sha256", parser_actions)
        self.assertNotIn("--expected-executable-manifest-bytes", parser_actions)

    def test_target_entry_delegates_exact_source_literals(self):
        observed = {}

        def delegate(argv):
            observed["argv"] = argv
            observed["bytes"] = base.FORMAL_EXECUTABLE_MANIFEST_BYTES
            observed["sha256"] = base.FORMAL_EXECUTABLE_MANIFEST_SHA256
            return 0

        prior = (
            base.FORMAL_EXECUTABLE_MANIFEST_BYTES,
            base.FORMAL_EXECUTABLE_MANIFEST_SHA256,
        )
        with mock.patch.object(
                target._base, "main_exact_core_boundary",
                side_effect=delegate) as exact_main, \
                mock.patch.object(target._base, "main") as compatibility_main:
            self.assertEqual(target.main(["--not-parsed-by-test"]), 0)
        exact_main.assert_called_once_with(["--not-parsed-by-test"])
        compatibility_main.assert_not_called()
        self.assertEqual(observed, {
            "argv": ["--not-parsed-by-test"],
            "bytes": 6_316,
            "sha256": (
                "9b0f0bfb783df30a0799c6943b7623e797ccdc4e4d213fe5500be90db6093145"),
        })
        self.assertEqual(
            (base.FORMAL_EXECUTABLE_MANIFEST_BYTES,
             base.FORMAL_EXECUTABLE_MANIFEST_SHA256),
            prior,
        )

    def test_target_wrapper_contains_no_clock_or_dynamic_authority_read(self):
        source = inspect.getsource(target)
        for forbidden in (
                "perf_counter", "monotonic", "time.time", "os.environ",
                "sys.argv", "read_text", "read_bytes"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
