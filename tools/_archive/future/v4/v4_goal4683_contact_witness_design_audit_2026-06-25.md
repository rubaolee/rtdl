# V4 Goal4683 Contact/Witness Design Audit

Date: 2026-06-25

Status: `goal4683_no_go_contact_witness_target_reuses_v2_14_collect_k_and_partner_witness`

## Decision

`AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D` is killed as a V4.0 high-performance target.

This is not a POD failure and not a performance-tuning failure. It fails the design gate before implementation: the core ingredients already exist as V2.14/current work.

## Evidence

V2.14 already has bounded collect-k / i64 row collection primitives:

- `rtdl_optix_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64_device`
- `rtdl_embree_collect_k_bounded_i64`
- `collect_native_i64_rows_with_backend_symbol`
- `collect_native_i64_rows_into_prepared_output_buffer`
- `run_native_collect_k_bounded_rows_with_prepared_result_buffer`

The current tree already has exact-witness / witness-column partner surfaces:

- `allocate_segment_polygon_witness_partner_device_output_columns`
- `segment_polygon_exact_witness_pair_page_optix_partner_columns`
- `segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns`
- `ray_primitive_witness_pair_page_optix_prepared_partner_columns`
- `bounded_collect_finalize_i64_partner_columns`
- `collect_k_bounded_i64_device`

The contact app history also says the primitive route is a generic `COLLECT_K_BOUNDED i64` collector, not native collision/contact logic. That means this target is very likely V2.14 collect-k plus partner exact-witness plumbing under a new V4 name.

## Why This Is No-Go

V4 speed credit needs a new generic runtime lever or a material same-primitive improvement over V2.14. This target currently offers neither.

If implemented as contact-specific exact witness, it risks violating the V4 rule against app-identity kernels. If implemented generically, the available evidence says it reuses collect-k / witness-column assets that already exist.

Therefore:

- no implementation is authorized;
- no POD run is authorized;
- no release or speed claim is authorized;
- no partner-migration speed credit is authorized.

## Goal-Level Decision Audit

1. Was I being stupid?

No, because I stopped at the design audit before writing code or running POD.

2. If yes, what action made it stupid?

The risk would have been continuing into implementation after seeing V2.14 collect-k and current exact-witness partner columns. That would have repeated the old pattern: rebranding existing primitives as V4 progress.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. Kill this target now and reset target selection around a genuinely absent Tier-2 fused primitive or an explicitly material same-primitive improvement with frozen bars.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4684 must be a high-performance V4 feasibility checkpoint, not another wrapper target. It must either identify a real absent generic lever or stop the formal high-performance V4 path.

## Next Goal

Goal4684: reset the high-performance V4 search.

Allowed outcomes:

- identify one genuinely absent, app-name-free Tier-2 fused primitive with a material-speed hypothesis and frozen bars;
- or conclude that formal high-performance V4 is blocked and keep the current bounded-operator/productization truth.

Disallowed:

- another app wrapper;
- another partner migration counted as speed;
- another same-primitive POD run without a material-speed hypothesis;
- any app-specific native kernel.
