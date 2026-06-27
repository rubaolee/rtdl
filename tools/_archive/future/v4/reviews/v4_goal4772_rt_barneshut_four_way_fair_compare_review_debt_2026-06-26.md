# Review Debt: Goal4772 RT-BarnesHut Four-Way Fair Compare

Date: 2026-06-26

Status: **open review debt**

Goal4772 produced a same-POD RT-BarnesHut four-way comparison protocol and
evidence for Author / V2.14 / V3.0.2 / V4.0. It has not yet received the
required external 3-AI completion audit.

## Artifact Under Review

- `future/v4/v4_goal4772_rt_barneshut_four_way_fair_compare_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4772_four_way_fair_compare_pod_2026-06-26.json`
- `scripts/v4_goal4772_rt_barneshut_four_way_fair_compare.py`
- `tests/v4_goal4772_rt_barneshut_four_way_fair_compare_test.py`

## Key Facts

- Dataset:
  `/root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt`.
- Contract:
  theta `0.5`, bucket size `32`, 3D author z-order tree, author force checksum
  required.
- Author binary phases:
  sort `6.87096s`, tree build `1.71362s`, RT-force `1.12905s`, total program
  `10.4391s`.
- V4 phases:
  sort `6.16351s`, preprocessing `6.503060236s`, RT-force `0.886653679s`,
  internal program including input download `7.513309154s`.
- V4 checksum:
  native `53.746751351154444`, author `53.7468`, relative error
  `9.051486889720442e-7`, tolerance pass.
- Fair Author-vs-V4 ratios:
  full internal program `1.3894144092875964x`, RT-force `1.27338331384739x`,
  sort `1.1147803767658364x`, author sort+tree vs V4 preprocessing
  `1.3200831129438122x`.
- V2.14 and V3.0.2:
  legacy Barnes-Hut adapters exist, but the Goal4760 author-semantics contract
  module and native author ABI symbols are absent. Timing ratios against the
  authors' binary are therefore forbidden.
- Local validation:
  `py -m unittest tests.v4_goal4772_rt_barneshut_four_way_fair_compare_test`
  ran 1 test and passed.

## Questions For Reviewer

1. Is the Goal4760 author-semantics contract the correct fairness boundary for
   RT-BarnesHut Author/V2.14/V3.0.2/V4.0 comparison?
2. Is it correct to report V2.14 and V3.0.2 as explicit route-absence findings
   rather than `n/a` or fake timing ratios?
3. Is Author-vs-V4 timing authorized by the checksum and same-input evidence?
4. Are the allowed and blocked public claims stated tightly enough?
5. Does this debt need any code changes before it can be closed, or only
   independent review?

## Requested Verdict Labels

Use one:

- `accept_goal4772_complete_four_way_fair_compare`
- `accept_with_required_amendments`
- `reject_requires_rework`
- `blocked_need_more_evidence`

## Non-Authorization

This review debt does not authorize:

- public V4 tag;
- RT-BarnesHut paper-reproduction wording;
- broad V4 speedup wording;
- public V2/V3/V4 RT-BarnesHut speed table;
- no-copy/device-resident tree-build claims.
