# Goal5216 Level-B Representative Consolidation Result

Date: 2026-07-09

## Verdict

```text
completed_level_b_representative_packet__full_paper_still_blocked_on_exact_inputs
```

## Purpose

After Goals5211-5215, the project has enough evidence for a strong Level-B
same-source representative X-HD reproduction packet, but not enough evidence
for Level-C exact paper dataset reproduction or full paper reproduction.

This goal consolidates the evidence into one packet.

## Machine-Readable Packet

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5216_level_b_representative_consolidation_2026-07-09.json
```

## Scope

Workload:

```text
target = graphics_dragon_happy_buddha
input1 = public Stanford Dragon / dragon_vrip.ply
input2 = public Stanford HappyBuddha / happy_vrip.ply
point_counts = [437645, 543652]
level = Level B same-source representative
```

This workload bridges the paper-branch author-log pair:

```text
/local/storage/shared/HDDatasets/graphics/dragon.ply
/local/storage/shared/HDDatasets/graphics/happy_buddha.ply
```

to public Stanford source files with matching point counts and matching author
HDResult. The files are not proved byte-identical to the author
`/local/storage/shared/HDDatasets` inputs.

## Author Reference

Source:

```text
Goal5186
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
```

Values:

```text
author hd_exec HDResult = 0.12572988867759705
paper-branch log HDResult = 0.12572969496250153
abs diff = 1.9371509552001953e-07
tolerance = 1e-6
matched = true
author Running.AvgTime = 7.823 ms
```

Boundary:

```text
Running.AvgTime is author internal timing. It is not directly comparable to
RTDL route wall or full gate wall without a denominator-alignment review.
```

## Current RTDL Route

Current route ingredients:

```text
generic nearest/witness/max-nearest pipeline
generic cell-MBR frontier / inline-nearest route
initial_state = local-grid-cell
max_inline_points = 512
global_bound_early_break = true
all-source no-copy app runner selection
```

Fresh long-lived process evidence:

```text
Goal5212 fresh artifact with Goal5211 route
matched author HDResult = true
distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
route_wall = 0.8517371863126755s
case_total = 0.851749412715435s
full_total_including_load = 1.5306707620620728s
load_full_inputs = 0.6782490611076355s
initial_state_seed = 0.21856994181871414s
frontier_rows = 0.4279836565256119s
native_total = 0.269847296s
OptiX launch = 0.038939636s
global_bound_early_break_count = 409376
source_subset_materialized = false
source_subset_selection_contract = all_source_no_copy_view
per_source_witness_exact = false
```

Explicit warm protocol evidence:

```text
measured matched author HDResult = true
measured route_wall = 0.2880803421139717s
measured case_total = 0.2880931422114372s
warmup_excluded_from_summary_statistics = true
full_total_including_load_warmup_and_measured = 1.8082116544246674s
```

Warm numbers are valid only with the explicit warmup protocol and must not
replace the fresh headline.

## Why This Is A Real Reproduction Packet

This packet demonstrates:

```text
the author binary runs on the public same-source Dragon/HappyBuddha pair;
the author run matches the author paper-branch log HDResult;
the RTDL route runs all Dragon sources against the full HappyBuddha target;
the RTDL route matches the author HDResult;
the route uses generic RTDL spatial / nearest / reduction machinery rather
than an X-HD-specific core primitive;
performance phases are recorded separately.
```

## Why This Is Not Full Paper Reproduction

Goals5214 and 5215 show:

```text
current POD lacks /local/storage/shared/HDDatasets;
author paper-branch logs provide paths and HDResult metadata, not input bytes;
public GitHub repository branches track no paper input datasets;
GitHub releases/packages/tags do not provide a dataset bundle;
no deterministic reconstruction provenance proves byte identity.
```

Therefore:

```text
exact paper dataset identity is not proved;
Level-C exact paper dataset reproduction remains unsupported;
full X-HD paper reproduction remains incomplete.
```

## Current Best Supported Status

```text
Level A bounded same-input correctness:
  complete and externally reviewed through Goal5126

System extraction:
  complete and externally reviewed through Goals5127-5128

Level B same-source representative reproduction:
  implemented through Goal5216, review pending

Level C exact paper dataset reproduction:
  blocked on exact input files / hashes / deterministic provenance

Level D full paper figures / denominator-aligned performance:
  not complete
```

## Review Status

```text
bounded_goals_5111_5126 = externally reviewed and approved
system_extraction_goals_5127_5128 = externally reviewed and approved
route_goals_5211_5215 = implemented; external review pending
goal5216 = implemented; external review pending
```

## Claim Boundary

Allowed:

```text
RTDL has a Level-B same-source representative X-HD route on public Stanford
Dragon -> HappyBuddha. The author binary and RTDL route both match the author
paper-branch HDResult for the corresponding workload name. The current RTDL
fresh route wall is about 0.852s and full gate wall including input load is
about 1.531s; explicit-warm measured route wall is about 0.288s with warmup
reported separately.
```

Not authorized:

```text
full X-HD paper reproduction is complete;
exact paper dataset reproduction is complete;
author-vs-RTDL performance ratio;
author parity;
warm-only headline;
X-HD-specific RTDL primitive claim;
exact paper figure reproduction.
```

## Next Recommendation

Send this packet with Goals5211-5215 for strict review.

If approved:

```text
close the current Level-B representative packet;
publish / document the current route only under Level-B status;
continue Level-C only if exact input files, hashes, or deterministic author
conversion provenance become available.
```

Do not spend the next goal on route micro-tuning unless review rejects the
current route or a new generic execution-model opportunity appears.
