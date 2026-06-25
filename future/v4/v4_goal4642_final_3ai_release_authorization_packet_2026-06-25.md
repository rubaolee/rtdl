# V4 Goal4642 Final 3-AI Release Authorization Packet

Status: packet ready; final release not authorized yet.

Packet status:

`goal4642_final_authorization_packet_ready_not_authorized`

## Requested Publication Label

Requested label:

`RTDL v4.0.0 formal high-performance generic RT-core operator release`

This label is intentionally narrow. It asks for formal release authorization for
the measured V4 generic RT-core operator surface. It does not ask for broad
whole-application speedup wording, all-benchmark speedup wording, public
true-zero-copy support, Tier-3 callback support, CuPy performance, C ABI,
embedding, non-Python host bindings, or app-specific native kernels.

## Scope

V4.0 is a Python-facing RT-core operator release. The public product is a set of
measured generic Tier-2 fused operator surfaces exposed through the V4 front
door and catalog.

In scope:

- generic RT-core operator surfaces;
- Python-facing front door;
- measured Torch CUDA, Numba, and RTDL-native partner scopes where explicitly
  recorded;
- fail-closed planning for unsupported callbacks;
- scorecard-backed release wording for the documented measured surfaces.

Out of scope:

- C ABI, embedding, or non-Python host language support;
- public true-zero-copy claim;
- raw OptiX callback support;
- Tier-3 custom callback support;
- CuPy performance claims;
- app-specific native kernels;
- broad whole-application speedup or all-benchmark speedup claims.

## Measured Operators

The Goal4639 frozen scorecard passed with eight measured surfaces:

| Surface | Representative ratio |
| --- | ---: |
| `v4_fixed_radius_count_threshold_2d_device_arrays` | `1.69721x` |
| `v4_closest_hit_grouped_argmin_3d_device_arrays` | `1.25677x` |
| `v4_ray_triangle_any_hit_flags_2d_device_arrays` | `5.67055x` |
| `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | `1.38362x` |
| `v4_point_group_nearest_witness_2d_device_arrays` | `389.707x` |
| `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | `1.48181x` |
| `v4_fixed_radius_graph_component_union_3d_device_arrays` | `1.20294x` |
| `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | `164.716x` |

Measured partner scopes:

- Torch CUDA: fixed-radius, closest-hit/grouped argmin, any-hit flags,
  weighted-sum, point-group front-door examples;
- Numba: grouped-i64 and component-union evidence;
- RTDL native: AABB all-ops prepared runner evidence.

CuPy performance remains unmeasured and must not be claimed.

## Scorecard Result

Goal4639 ran the frozen Goal4638 scorecard on the RTX A5000 POD.

Result:

- strong release-in-scope families passed: `4/4`;
- measured surfaces passed: `8/8`;
- partial controls passed: `4/4`;
- deferred/excluded rows recorded: `2`;
- failed surfaces: `0`;
- strong representative ratio geomean: `5.1848067367961095x`.

Strong release-in-scope families:

- `rt_dbscan`;
- `raydb_style`;
- `triangle_counting`;
- `librts_spatial_index`.

Partial controls:

- `hausdorff_xhd`;
- `robot_collision`;
- `contact_manifold`;
- `rtnn`.

Deferred/excluded rows:

- `spatial_rayjoin`;
- `barnes_hut`.

The deferred rows are not silently dropped. They are excluded by the frozen
scorecard and must not be used in V4.0 coverage or speedup claims.

Primary evidence:

- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/run.log`

## Public Docs And Examples

Goal4640 cleaned the public V4 front door:

- root README presents V4 as the current user surface;
- docs index current V4 only;
- tutorials teach V4 front-door use and performance boundaries;
- `examples/v4/` contains runnable V4 entrypoints;
- stale `docs/current_v3_status.md` was archived under history;
- public docs avoid current-V3 and stale development-preview wording.

Verification:

- targeted docs group: `24 tests OK`;
- full local V4 group after Goal4640: `165 tests OK`;
- final local V4 group after Goal4641: `168 tests OK`;
- `examples/v4/v4_frontdoor_quickstart.py`: passed;
- `scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16`: passed.

Primary evidence:

- `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`
- `tests/v4_goal4640_public_docs_cleanup_test.py`

## Clean-Tree Reproducibility

Goal4641 validated the committed package from a clean worktree:

- clean worktree: `C:/Users/Lestat/Desktop/work/rtdl_v4_goal4641_clean_tree_check`;
- first clean-tree attempt caught a missing committed dependency;
- missing dependency was fixed by adding
  `scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`;
- clean worktree full V4 group passed;
- clean worktree catalog dry-run passed;
- clean worktree quickstart passed;
- clean worktree status was empty after validation.

After the Goal4641 commit, the clean worktree was rechecked at:

`884aeda8084d4c84bae8ec858f4b7436461ee783`

Goal4641 revalidation from that commit:

- full V4 tests: `168 tests OK`;
- catalog dry-run: `status: passed`, `example_count: 11`, `failed_examples: []`;
- quickstart: `status: ok`;
- post-validation `git status --short`: empty.

After this Goal4642 authorization packet was committed, the clean worktree was
rechecked again at:

`437b79a2a382082e269d0d0ee128528caf0ae112`

Goal4642 packet revalidation from that commit:

- full V4 tests: `171 tests OK`;
- catalog dry-run: `status: passed`, `example_count: 11`, `failed_examples: []`;
- quickstart: `status: ok`;
- post-validation `git status --short`: empty.

Primary evidence:

- `future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md`
- `tests/v4_goal4641_clean_tree_reproducibility_test.py`
- `future/v4/reviews/goal4641_clean_tree_reproducibility_review_record_2026-06-25.md`

## Review Debt

Historical scorecard debt through Goal4632 was closed by Antigravity in:

- `future/v4/reviews/antigravity_v4_goal4626_4632_scorecard_debt_review_2026-06-24.md`
- `future/v4/reviews/v4_remaining_debt_after_antigravity_scorecard_review_and_forward_message_2026-06-24.md`

Open review debts intentionally carried into this packet:

- `external_review_debt_remains_for_antigravity_goal4633_backfill`;
- `external_review_debt_remains_for_goal4635_component_union_completion`;
- `external_review_debt_remains_for_goal4637_aabb_frontdoor_catalog_completion`;
- `external_review_debt_antigravity_goal4638_formal_scorecard_freeze`;
- `external_review_debt_antigravity_goal4639_serious_release_scorecard`;
- `external_review_debt_goal4640_public_docs_cleanup`;
- `external_review_debt_goal4641_clean_tree_reproducibility`.

Goal4642 asks reviewers to explicitly decide whether these debts are closed,
waived for the requested narrow release label, or release-blocking.

## Forbidden Claims

The following claims remain forbidden unless a later release explicitly earns
them:

- broad V4 speedup;
- whole-application speedup;
- all-benchmark speedup;
- public true-zero-copy;
- Tier-3 callback support;
- raw OptiX callback support;
- CuPy performance;
- C ABI / embedding / non-Python host;
- app-specific native kernels;
- Barnes-Hut covered by V4.0;
- Spatial RayJoin covered by V4.0;
- LibRTS paper reproduction.

## Release Notes

Proposed release-note wording if Goal4642 is authorized:

RTDL v4.0.0 is the first formal V4 release of the Python-facing generic RT-core
operator layer. It ships a measured V4 front door and catalog for eight generic
operator surfaces, backed by a frozen scorecard on RTX A5000 / OptiX 8.0 class
hardware. The release supports high-performance operator-level claims for the
documented measured surfaces only. It does not claim broad whole-application
speedup, public true-zero-copy, Tier-3 callbacks, raw OptiX callbacks, CuPy
performance, C ABI, embedding, non-Python host bindings, or app-specific native
kernels.

## Requested Verdict

Each reviewer must choose one:

- `authorize_formal_v4_0_high_performance_operator_release`
- `authorize_with_amendments_before_publication`
- `no_go_do_not_release_v4_0`

Authorization requires explicit acceptance of the narrow publication label and
explicit handling of review debt.

## Goal-Level Decision Audit

Was I stupid?

No for preparing this packet. The packet asks the hard release question directly
instead of hiding behind another preview label.

If yes, what actions made the decision stupid?

Not applicable. A stupid action here would be to declare release without the
3-AI authorization this packet requests.

Was there another possibility that avoids getting stuck on a bad path?

Yes. The tempting bad path is to keep refining docs and tests forever. The
correct path is to ask reviewers for an explicit release or no-go verdict.

Can I start a different path that actually solves the problem?

Yes. If reviewers no-go the packet, the next path is not more wording polish; it
is to fix the concrete release-blocking finding they identify.

## Non-Authorization

This packet does not authorize final V4 release. It is the packet submitted for
3-AI release authorization.
