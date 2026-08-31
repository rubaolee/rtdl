"""Version-bounded hostile matrix for the frozen Goal5803 v14 runtime.

The successor deliberately changes only the v14 ``v4_rtdlexe.py`` core.  The
later ProviderReady wrapper is absent from that frozen source identity, so its
wrapper-specific forwarding check is explicitly N/A rather than silently
deleted.  The inherited cases still exercise the complete direct public
``PreparedRTDLExecutable.execute`` overflow/status path and the central receipt
validator used by v14.
"""

import unittest

from tests import goal5803_runtime_overflow_hostile_test as _hostile


class Goal5803V14RuntimeOverflowHostileTest(
        _hostile.Goal5803RuntimeOverflowHostileTest):

    @unittest.skip(
        "N/A_VERSION_ABSENT: frozen v14 predates ProviderReadyRTDLExecutable")
    def test_provider_ready_path_preserves_exact_overflow_translation(self):
        raise AssertionError("skip decorator must prevent execution")


if __name__ == "__main__":
    unittest.main()
