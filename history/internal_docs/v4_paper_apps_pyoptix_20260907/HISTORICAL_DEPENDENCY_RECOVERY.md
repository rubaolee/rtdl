# Historical dependency recovery for local regression

The expanded local regression initially produced 65 passes and three file-not-
found errors. The missing files were historical custody dependencies, not
generated application code. No file was reconstructed from a report.

## Restored exact bytes

| Repository path | Selected read-only source | SHA-256 | Corroboration |
| --- | --- | --- | --- |
| `history/internal_docs/goal5753_held_out_selection_20260811.json` | `/home/lestat/work/goal5802_final_home_untimed_20260825_a551fd12/source_a551fd12/history/internal_docs/goal5753_held_out_selection_20260811.json` | `6f9b73a171c32c99eaea5f7d7ba28ac0cc9c64c088bbd54d1449d3d52006f3e6` | Byte-identical copy at sibling `source_07006b8eb`. |
| `history/internal_docs/goal5753_frozen_core_seal_audit_postselection_20260811.json` | `/home/lestat/work/goal5802_final_home_untimed_20260825_a551fd12/source_a551fd12/history/internal_docs/goal5753_frozen_core_seal_audit_postselection_20260811.json` | `a654c1d1d94a00dcbdba8352b184f6f9d7de3e680f4c041b462c820fc75b5cff` | Byte-identical copy at sibling `source_07006b8eb`. |
| `history/internal_docs/goal5814_particle_executable_v2_20260828/4bf983fdc07f5f6e48b8fcd32482ea23dc14a50a3083cdaa4fe0923142acba63.particle_descriptor.json` | `/home/lestat/work/goal5814_particle_native_compile_20260828/history/internal_docs/goal5814_particle_executable_v2_20260828/4bf983fdc07f5f6e48b8fcd32482ea23dc14a50a3083cdaa4fe0923142acba63.particle_descriptor.json` | `4bf983fdc07f5f6e48b8fcd32482ea23dc14a50a3083cdaa4fe0923142acba63` | Byte-identical copy in `freeze_v2/build`; filename equals byte digest. |

Older Goal5759 copies of the two Goal5753 JSON documents have the same parsed
content but CRLF bytes and different SHA-256 values. They were not selected.
The later Goal5802 LF bytes were used because two independent source projections
agree exactly and match the current repository line-ending convention.

This restoration repairs repository completeness for historical tests. It does
not create new historical authority, modify the embedded claims, or authorize
application performance wording.

## Expanded regression outcome

After restoration, the selected 11-module historical regression ran 68 tests:
67 passed and one stopped because the current and all inspected historical Git
object stores lack abbreviated commit `b8058860f`. `origin` also has no ref by
that name. The remaining test asks `git show b8058860f` to establish that the
selected app was absent from that commit; this is a historical Git-custody
dependency, not an application execution dependency. It is retained as an open
custody gap rather than weakened, skipped, or rewritten. The 25-test new
experiment suite remains fully passing.
