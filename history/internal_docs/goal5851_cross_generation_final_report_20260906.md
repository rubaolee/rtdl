# Goal5851 Cross-Generation Final Report

Date: 2026-09-06

Status:
`PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`

This report closes the internal implementation and performance gates for
Goal5848/Goal5851. It does not authorize public or manuscript performance
wording; independent external review remains unavailable and is a separate
claim gate.

## Frozen Contract

- exact experiment source:
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`;
- exact source tree:
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`;
- frozen predecessor:
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`;
- unchanged public/Direct median limit: `1.20x`;
- unchanged public/Direct worst-block limit: `1.35x`;
- each generation: 512 instrumentation workers, 80 formal process cells,
  10,240 retained steady samples, zero retry and zero discard;
- no workload, arm, timer, estimator, threshold or result row was changed
  between generations.

The cross-generation authority compares only preregistered within-machine gate
directions. It explicitly reports
`cross_machine_raw_time_ratio_computed: false`.

## Passing Results

| Generation | Task | Public RTDL / Direct median | Worst block | Successor / predecessor | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Ada, RTX 4090, CC 8.9 | Triangle weighted all-hit | `1.175066x` | `1.211025x` | `0.903016x` | pass |
| Ada, RTX 4090, CC 8.9 | Closed AABB relation count | `1.076852x` | `1.092253x` | `0.584438x` | pass |
| Ampere, RTX 3090, CC 8.6 | Triangle weighted all-hit | `1.133636x` | `1.142675x` | `0.922388x` | pass |
| Ampere, RTX 3090, CC 8.6 | Closed AABB relation count | `1.094795x` | `1.118811x` | `0.608228x` | pass |

For descriptive context, the median of the eight per-block steady medians was:

| Generation | Task | RTDL | Direct OptiX |
| --- | --- | ---: | ---: |
| Ada | Triangle | 59,811.5 ns | 50,977.0 ns |
| Ada | Relation | 280,976.5 ns | 261,218.5 ns |
| Ampere | Triangle | 60,822.5 ns | 53,613.5 ns |
| Ampere | Relation | 240,213.0 ns | 219,804.0 ns |

These descriptive medians are not substituted for the registered median of
within-block ratios in the first table.

Implementation-entry RTDL/strong-PyOptix medians also passed:

| Generation | Triangle | Relation |
| --- | ---: | ---: |
| Ada | `0.642180x` | `0.653826x` |
| Ampere | `0.618362x` | `0.681393x` |

The old unequal-lifecycle post-import diagnostic remains adverse and is
retained as required:

| Generation | Triangle | Relation |
| --- | ---: | ---: |
| Ada | `1.559788x` | `1.749327x` |
| Ampere | `1.637468x` | `1.837415x` |

It starts after pinned PyOptix has created CUDA state during excluded import
while RTDL remains lazy. It is mandatory non-gating evidence, not a passing
equivalent-lifecycle comparison.

## Hardware And Evidence

Ada generation:

- GPU: NVIDIA GeForce RTX 4090;
- UUID: `GPU-01a12a86-b470-30ee-c81c-272e3b8fb6d7`;
- driver: 580.159.04;
- authority/recount file SHA-256:
  `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7`;
- authority internal seal:
  `ce6a959fc6897ec3ff1732552f8fa94fde95ee54e63173424d80500bdca5ef04`;
- archive SHA-256:
  `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced`;
- local evidence:
  `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/`.

Ampere generation:

- GPU: NVIDIA GeForce RTX 3090;
- UUID: `GPU-eda7acdc-0cc5-6c7f-689f-e8c6831f3b63`;
- driver: 580.159.03;
- authority/recount file SHA-256:
  `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3`;
- authority internal seal:
  `6181e93c77526eaf8d6592a42698b0f5b67830db693b84afc60e88960185cdaa`;
- archive SHA-256:
  `7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2`;
- local evidence:
  `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass/`.

Each downloaded archive passed SHA-256 and gzip integrity. Each contains 2,405
manifest-bound files. Mac-side portable manifest recount found zero mismatches:

- Ada: 125,718,265 payload bytes, manifest seal
  `8cbd609118b3b2c634a1a3dbec4c10ebd585fc527452083ae6f7ba650222fe06`;
- Ampere: 125,646,793 payload bytes, manifest seal
  `c0ff8626df78ac7039b3182de8e025d7d5ac440e1a135d9cb0235a9dffa7c240`.

Cross-generation authority:

- schema: `rtdl.goal5848.cross_generation_authority.v2`;
- status:
  `PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`;
- independently rebuilt files are byte-identical with SHA-256
  `99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692`;
- internal authority seal:
  `0ec93d9e529a3ff3dc4a09a178b3c1c5eaf2aa930352777917c8753a7b748d9b`;
- local authority directory:
  `/Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete/`.

## Operational Disclosure

The first Ampere launcher invocation supplied the runbook by absolute path but
did not change the remote current directory into the clean checkout. The
runbook failed closed at `validate_exact_git_checkout` before creating the
requested output root, preparing dependencies or executing any worker. There
were no performance samples or evidence rows to pool. The corrected invocation
used a new output-root name and GNU `env -C` to bind the checkout directory.
This invocation error is disclosed here and is not represented as a formal
transaction failure.

All earlier adverse archives remain retained, including the `a4dd1d5d...`
Ampere pass/Ada failure pair. None was pooled with the final source.

## Claim Boundary

The evidence supports the bounded internal statement that, for the two frozen
tasks and exact public prepared-replay contracts, RTDL stayed within the
preregistered overhead limits relative to Direct OptiX on one Ampere and one
Ada GPU while passing the pinned baseline and regression gates.

It does not establish arbitrary-callback performance, all-app performance,
hardware-independent raw speedup, cold-start parity, human usability, external
consensus or a public paper claim. The authority itself keeps
`public_or_manuscript_claim_authorized: false` and
`external_review_complete: false`.
