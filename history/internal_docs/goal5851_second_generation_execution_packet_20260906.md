# Goal5851 Second-Generation Execution Packet

Date: 2026-09-06

Status: `READY__NON_AMPERE_GPU_REQUIRED`

This packet is operational documentation. It does not change the experiment
source, protocol, workload, arms, timers, estimators or thresholds.

## Frozen Identity

- experiment source commit:
  `a4dd1d5d32b962b81a29e560ac8845e9c508101c`;
- experiment source tree:
  `424a88cd806f76737ae3aec0d3238ebced833bfc`;
- predecessor commit:
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`;
- runbook SHA-256:
  `5d4665d059f0339c4f79f79e2b7936e9dc65f0b811fd15201eaf7d513a92548d`;
- cross-generation builder SHA-256:
  `aaf4bfbe8162ca536bd3bb5b507e33d32bda0608bd8eb5cb8f759ccc0f853fb0`.

A later documentation commit is not an experiment-source substitute. The pod
must detach at the exact commit above and show an empty porcelain status.

## Existing Generation

The retained passing generation is NVIDIA GeForce RTX 3090, Ampere, compute
capability 8.6, UUID
`GPU-4c3be278-841f-27ce-6a4e-02ca58147d16`, driver 580.159.03.

- authority/recount file SHA-256:
  `873230497dc81b2c9013695804278915fe35fd2c76130a0077fa2da2c7a0bcfe`;
- authority internal seal:
  `29f60d68c904aad9163f8a2faf21245d29aedd55d71bf8a8a9eb98bcff4056bf`;
- complete archive SHA-256:
  `a1b8300ab32ec8a846e82d1e6efde29c234718748415287293d76a903b25d824`;
- local retained directory:
  `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_a4dd1d5d_pass/`.

This authority cannot be paired with another Ampere 8.6 GPU. The old Ada pass
at source `c4351f612...` cannot be paired because its source identity differs.

## Required GPU

Use exactly one idle NVIDIA GPU from a different accepted generation:

| Compute capability | Architecture | Eligible for generation 2 |
| --- | --- | --- |
| 7.5 | Turing | yes |
| 8.6 | Ampere | no; already used |
| 8.9 | Ada | yes; preferred |
| 12.0 | Blackwell | yes |

The GPU UUID must differ from the retained RTX 3090 UUID. The host needs a
driver accepted by the committed OptiX compatibility registry, outbound Git
and Python package access, one visible idle GPU, and sufficient uninterrupted
time and disk. The runbook discovers or installs its own compatible CUDA and
Python environment; no fixed pod image or preinstalled toolkit version is
required.

## Single-Attempt Command

Choose a new absolute output root outside the checkout. It and both possible
archive names must not exist before launch.

```bash
git clone --no-checkout --branch codex/cgo-goal5836-handoff \
  https://github.com/rubaolee/rtdl.git /workspace/rtdl-goal5851-a4dd1d5-clean
git -C /workspace/rtdl-goal5851-a4dd1d5-clean checkout --detach \
  a4dd1d5d32b962b81a29e560ac8845e9c508101c
git -C /workspace/rtdl-goal5851-a4dd1d5-clean status \
  --porcelain=v1 --untracked-files=all
cd /workspace/rtdl-goal5851-a4dd1d5-clean
scripts/goal5848_pod_prepare_and_run.sh \
  a4dd1d5d32b962b81a29e560ac8845e9c508101c \
  /workspace/goal5848-generation2-a4dd1d5d-transaction1
```

The status command must print nothing. This is one transaction attempt for
this source/GPU pair. Do not rerun a failed formal transaction, delete its
archive, or pool any row with another attempt.

## Generation-2 Acceptance

The run must print `GOAL5848_SINGLE_GENERATION_COMPLETE` and preserve:

1. exactly 512 instrumentation workers and 80 formal workers;
2. zero retry and zero discard;
3. passing timer-free correctness, baseline competence, instrumentation,
   public/Direct, implementation-entry and successor/predecessor gates for both
   registered tasks;
4. exact source and predecessor identities above;
5. byte-identical `single-generation-authority.json` and
   `single-generation-authority.recount.json`;
6. the original output directory, archive, adjacent SHA-256 file and terminal
   transcript.

If the run fails at any stage, retain the generated failure archive and stop.
Goal5851 then remains incomplete; no local retry or threshold change is
allowed for that source/GPU transaction.

## Download Verification

After downloading the archive, reproduce its SHA-256 locally, list every tar
entry successfully, extract the two generation authority files, and require
byte identity with `cmp`. Keep the evidence outside Git under a new immutable
directory adjacent to the retained Ampere directory.

## Cross-Generation Closure

Place generation 2's authority and recount together. Ensure the intended new
cross-generation output path does not exist and is outside the source Git,
then run:

```bash
PYTHONPATH=src:. python3 \
  scripts/goal5848_build_cross_generation_authority.py \
  --first /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_a4dd1d5d_pass/single-generation-authority.json \
  --second <generation-2-directory>/single-generation-authority.json \
  --output <new-external-directory>/goal5848-cross-generation-authority.json
```

The builder must independently reject source/predecessor drift, the same
architecture, a repeated UUID, an adverse task, absent or nonidentical recount
bytes, retry/discard, or a pre-existing/symlinked output. It compares only
within-machine gate direction and must report
`cross_machine_raw_time_ratio_computed: false`.

The expected success status is
`PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`.
Even that status does not authorize public or manuscript wording: external
review and the Goal5852 claim ledger remain separate gates.
