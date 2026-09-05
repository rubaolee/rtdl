# Goal5848 GPU execution runbook

Date: 2026-09-05

Status: `READY_FOR_TWO_SINGLE_ATTEMPT_GENERATIONS__NO_GPU_RESULT_YET`

## 1. Required evidence

Goal5848 requires two complete runs on distinct supported RTX architecture
generations. Any pair among Turing (`7.5`), Ampere (`8.6`), Ada (`8.9`) and
Blackwell (`12.0`) is valid if each run passes independently. No cloud vendor,
GPU model or fixed driver branch is required. An RTX A4000 is Ampere `8.6` and
is one valid generation, but it cannot supply both generations alone.

The host must expose one idle NVIDIA GPU to the process, a Linux driver accepted
by the frozen OptiX 7.6--9.1 compatibility registry, outbound Git/Python package
access, adequate disk space, and enough uninterrupted time for builds plus the
80 fresh-process formal cells. The runner probes the actual host, repairs
ordinary apt-based prerequisites where possible, and otherwise fails before
formal worker zero.

## 2. One-generation command

Start from the committed Goal5848 source. Do not edit it on the pod.

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
git checkout --detach <GOAL5848_COMMIT>
scripts/goal5848_pod_prepare_and_run.sh \
  <GOAL5848_COMMIT> \
  /root/goal5848-<generation>-attempt1
```

The output root must be absolute, absent before the run, and outside the Git
checkout. Use exactly one attempt for a committed source identity. Do not
rerun a failed formal transaction and do not delete its failure archive.

## 3. What the runner performs

The runner validates a clean exact checkout, probes GPU/driver/compute
capability, selects or installs a compatible CUDA toolkit, creates an isolated
Python environment, selects the newest driver-compatible frozen OptiX stack,
and builds the pinned unmodified PyOptix source.

It then materializes the exact Goal5847 predecessor, builds current and
predecessor minimal native libraries, derives Direct OptiX independently,
builds and seals shared PTX/CUBIN, creates test-only signing roots, performs a
cold AOT build and fresh-process exact-hit qualification, and unlinks private
key paths.

Before formal timing it freezes preregistration and runs timer-free exactness,
strong-baseline competence and instrumentation-overhead gates. It then runs
exactly one balanced 80-cell formal transaction. Finally it constructs the
single-generation authority twice, requires byte-identical outputs, captures
post-run machine state, creates an evidence manifest, and packages the result.

The experiment sets both `CUDA_CACHE_DISABLE=1` and
`RTDL_OPTIX_DISK_CACHE_POLICY=disabled`. The latter is a generic explicit
engine policy; production defaults remain cache-enabled. All four primary arms
therefore avoid uncontrolled cross-process cache history.

## 4. Success and failure outputs

Success prints:

```text
GOAL5848_SINGLE_GENERATION_COMPLETE
archive=<OUTPUT_ROOT>.tar.gz
sha256_file=<OUTPUT_ROOT>.tar.gz.sha256
authority=<OUTPUT_ROOT>/single-generation-authority.json
```

Preserve the archive, SHA-256 file, original output directory and terminal
transcript. The archive includes both
`single-generation-authority.json` and
`single-generation-authority.recount.json`; they must be byte-identical.

Failure prints the failing stage and creates
`<OUTPUT_ROOT>.failure.tar.gz` when possible. A failure is evidence, not a
request to rerun. Diagnose it locally, commit a versioned repair, and run a new
attempt under a new output root.

## 5. Cross-generation closure

After two distinct generations succeed and their archives are verified, place
each authority and its adjacent `.recount.json` companion in stable locations
and run:

```bash
python scripts/goal5848_build_cross_generation_authority.py \
  --first <generation-one>/single-generation-authority.json \
  --second <generation-two>/single-generation-authority.json \
  --output <new-path>/goal5848-cross-generation-authority.json
```

The builder rejects the same architecture twice, the same GPU UUID twice, any
failed task gate, source/predecessor drift, retries/discards, missing recounts
or nonidentical recount bytes. It compares only independent within-machine
gate direction and never divides raw times across GPUs.

Even a passing cross-generation authority authorizes only internal technical
completion. External review must inspect the committed source and complete
evidence before any public or manuscript performance wording.
