from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from goal5838_preregister_generic_core_exam import (  # noqa: E402
    Goal5838PreregistrationError,
    OUTPUT,
    build_authority,
    verify_authority,
)


class Goal5838PreregistrationTest(unittest.TestCase):
    def test_stored_authority_rebuilds_exactly(self) -> None:
        stored = json.loads(OUTPUT.read_text("utf-8"))
        self.assertEqual(verify_authority(stored), build_authority())

    def test_counts_and_order_are_frozen(self) -> None:
        authority = build_authority()
        self.assertEqual(authority["baseline"]["stable_v4_fixed_constructor_count"], 2)
        self.assertEqual(authority["baseline"]["prospective_frozen_core_new_shape_success_count"], 0)
        self.assertLess(
            authority["stage_order"].index(
                "B_IMPLEMENT_MIGRATE_AND_FREEZE_GENERIC_CORE"),
            authority["stage_order"].index("C_INDEPENDENTLY_SELECT_CHALLENGE"),
        )

    def test_engineering_bug_cannot_be_promoted_to_exam_failure(self) -> None:
        authority = build_authority()
        self.assertTrue(
            authority["before_core_seal"]["ordinary_defects_are_engineering_repairs"]
        )
        self.assertFalse(
            authority["before_core_seal"]["deadline_can_trigger_scientific_failure"]
        )
        self.assertEqual(
            authority["challenge_selection"]["temporary_selector_unavailability"],
            "PENDING_NOT_FAILURE",
        )

    def test_goal5837_cannot_be_relabelled(self) -> None:
        authority = build_authority()
        self.assertFalse(authority["challenge_selection"]["goal5837_can_be_reused"])

    def test_coordinated_reseal_attack_is_rejected(self) -> None:
        changed = copy.deepcopy(build_authority())
        changed["baseline"]["prospective_frozen_core_new_shape_success_count"] = 1
        body = dict(changed)
        body.pop("authority_sha256")
        import hashlib

        body_bytes = json.dumps(
            body, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
        changed["authority_sha256"] = hashlib.sha256(body_bytes).hexdigest()
        with self.assertRaisesRegex(
            Goal5838PreregistrationError, "G5838P009_AUTHORITY_MISMATCH"
        ):
            verify_authority(changed)


if __name__ == "__main__":
    unittest.main()
