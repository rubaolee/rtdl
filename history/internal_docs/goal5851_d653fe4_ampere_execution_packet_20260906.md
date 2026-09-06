# Goal5851 `d653fe4` Ampere Execution Packet

Date: 2026-09-06

Status: `READY__AMPERE_GPU_REQUIRED`

This packet executes the frozen Goal5848 protocol. It does not change source,
workload, arms, timers, estimators, thresholds or claim gates.

## Exact Source Identity

- final experiment source commit:
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`;
- final experiment source tree:
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`;
- frozen predecessor commit:
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`;
- runbook SHA-256:
  `5d4665d059f0339c4f79f79e2b7936e9dc65f0b811fd15201eaf7d513a92548d`;
- cross-generation builder SHA-256:
  `aaf4bfbe8162ca536bd3bb5b507e33d32bda0608bd8eb5cb8f759ccc0f853fb0`.

A later documentation commit is not an experiment-source substitute. The pod
must detach at exactly `d653fe4...` and show an empty porcelain status.

## Existing Passing Generation

The final source has one retained passing generation:

- GPU: NVIDIA GeForce RTX 4090;
- architecture and compute capability: Ada, 8.9;
- UUID: `GPU-01a12a86-b470-30ee-c81c-272e3b8fb6d7`;
- driver: 580.159.04;
- authority/recount SHA-256:
  `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7`;
- authority internal seal:
  `ce6a959fc6897ec3ff1732552f8fa94fde95ee54e63173424d80500bdca5ef04`;
- complete archive SHA-256:
  `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced`;
- local evidence directory:
  `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/`.

The remaining transaction must use Ampere compute capability 8.6 and a
different UUID. The earlier RTX 3090 pass used source `a4dd1d5d...`; it cannot
be paired with this final source.

## Pod Acceptance

Use one idle RTX 3090, RTX A4000, RTX A5000 or RTX A6000 with compute
capability 8.6. A different Ampere model is acceptable; the protocol compares
gate direction within each machine and does not compute cross-machine raw-time
ratios. The host needs outbound Git and package access, enough free disk, and
an uninterrupted execution window. The committed runbook discovers or
installs its compatible CUDA/Python dependencies.

Reject before the formal run if the GPU is not compute capability 8.6, if its
UUID equals the retained Ada UUID, if another compute process is active, or if
the exact source checkout is dirty.

## One-Shot Command

Choose a previously absent absolute output root outside the checkout. Do not
reuse an old checkout, output directory, archive or SHA file.

```bash
git clone --no-checkout --branch codex/cgo-goal5836-handoff \
  https://github.com/rubaolee/rtdl.git /workspace/rtdl-goal5851-d653fe4-clean
git -C /workspace/rtdl-goal5851-d653fe4-clean checkout --detach \
  d653fe4ad170c5b51fee309d653c9565944dcf2e
git -C /workspace/rtdl-goal5851-d653fe4-clean status \
  --porcelain=v1 --untracked-files=all
cd /workspace/rtdl-goal5851-d653fe4-clean
scripts/goal5848_pod_prepare_and_run.sh \
  d653fe4ad170c5b51fee309d653c9565944dcf2e \
  /workspace/goal5848-ampere86-d653fe4-transaction1
```

The status command must print nothing. This is one formal transaction attempt
for the final source/GPU pair. A failure must be retained and must not be
rerun, relabeled or pooled.

## Acceptance Criteria

The run must print `GOAL5848_SINGLE_GENERATION_COMPLETE` and preserve:

1. exactly 512 instrumentation workers and 80 formal workers;
2. exactly 10,240 retained steady samples;
3. zero retry and zero discard;
4. passing timer-free, competence, instrumentation, public/Direct,
   implementation-entry and successor/predecessor gates for both registered
   tasks;
5. exact final-source and predecessor identities above;
6. byte-identical `single-generation-authority.json` and
   `single-generation-authority.recount.json`;
7. original output directory, deterministic archive, adjacent SHA-256 file and
   terminal transcript.

No threshold, workload, arm, timer or estimator change is permitted. If a
formal stage fails, retain the failure evidence and stop that transaction.

## Download And Closure

Download the archive and SHA file to a new immutable directory under
`/Users/rl2025/RTDL_evidence/goal5848/`. Reproduce the archive SHA-256, pass
gzip/tar integrity, verify every manifest row, and require byte-identical
authority/recount hashes.

Then create a previously absent output directory and run:

```bash
PYTHONPATH=src:. python3 \
  scripts/goal5848_build_cross_generation_authority.py \
  --first /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/single-generation-authority.json \
  --second <ampere-d653-directory>/single-generation-authority.json \
  --output <new-external-directory>/goal5848-cross-generation-authority.json
```

The builder must independently reject source/predecessor drift, equal compute
capability, repeated UUID, adverse tasks, missing or nonidentical recount,
retry/discard, or pre-existing/symlinked output. It must report
`cross_machine_raw_time_ratio_computed: false`.

The expected success status is
`PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`.
External review and manuscript claim authorization remain later, separate
gates.
