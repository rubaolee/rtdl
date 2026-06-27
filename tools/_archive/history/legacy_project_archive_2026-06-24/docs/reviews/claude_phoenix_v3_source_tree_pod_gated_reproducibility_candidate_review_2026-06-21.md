# Claude Review: Phoenix V3 Source-Tree / Pod-Gated Reproducibility Candidate

Reviewer: Claude Sonnet 4.6 (external, local Windows Claude Code)
Date: 2026-06-21
Files read: all nine listed in the call-for-review.

Verdict: `approve-with-amendments-not-release`

---

## Bottom Line

The candidate is concrete, honestly scoped, and well-structured. It correctly
refuses to close the installer blocker, correctly preserves every required
negative boundary, and has a machine-readable gate that verifies its own
properties. It is reviewable as written.

One concrete amendment is required before `source_tree_pod_gated_candidate_reviewed: true`
is warranted: the Numba CUDA path environment exports are documented in the
runbook but are absent from the candidate document. A user who follows only
the candidate would fail the `numba_cuda_jit: pass` step in the GPU partner
gate without knowing why. That gap must be closed in the candidate before it
qualifies as a standalone reproducibility record.

No other blocking amendment was found. The package pins, native build
commands, runtime library exports, GPU env gate, and release gate sequence
are sufficient for a serious user on the documented RTX pod class once the
Numba exports are added.

This review does not authorize release. It does not change any install gate
field. It is external review material for the candidate only. Codex consensus
is still required before any machine-readable field is updated.

---

## Findings

### What is solid

**Scope boundary.** The candidate opens and closes with explicit scope
statements. It names what the path is (source-tree, RTX pod, staged
package set, experimental flag) and names what it is not (general release
installer, package-install wording, release authorization, second-RTX
confirmation, broad V3-over-V2 speedup). These statements appear in the
document prose and are machine-checked by `v3_phoenix_install_reproducibility_gate.py`
via `REQUIRED_CANDIDATE_PHRASES`.

**Package pins.** All six packages are pinned exactly. The candidate, the
install script, and the gate script agree on the same versions:

```text
torch==2.6.0+cu124
cupy-cuda12x==14.1.1
numba==0.65.1
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.9.86
nvidia-cuda-runtime-cu12==12.9.79
```

The gate script checks `gpu_env_requirements_match_installer`, so a future
pin drift will be caught automatically.

**Experimental flag design.** The `--accept-experimental-pod-gate` flag is
load-bearing. The install script refuses invocation without it, the gate
verifies that refusal check exists in the installer source, the candidate
quotes the flag in the install command, and the runbook quotes it again with
the label "Staged installer for the tested pod-style environment." The flag
cannot be accidentally omitted.

**Native backend build.** `make build-embree` and `make build-optix
OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0` are both present and use
the documented OptiX SDK path from the 2026-06-20 pod run. The runtime
library export names (`RTDL_OPTIX_LIBRARY`, `RTDL_OPTIX_LIB`,
`RTDL_EMBREE_LIBRARY`) are all three documented, which matches the known
dual-alias requirement for OptiX.

**Gate sequence.** The candidate lists all five required gate commands in
order and names their expected current output fields. The expected output
includes `status: blocked_not_release` and `installer_closes_release_blocker:
false`, so a reviewer running the gates after reproducing the environment
will see confirming output, not a false green.

**Gate script coverage.** `v3_phoenix_install_reproducibility_gate.py`
checks 15 properties, including all 12 required candidate phrases,
installer refusal logic, package pin consistency, PyTorch cu124 index URL,
and the GPU env dry-run status. The gate hardcodes
`source_tree_pod_gated_candidate_reviewed: False`, which is the correct
value until this review and Codex consensus are recorded. Updating that
field requires Codex to change the gate script, which prevents the field
from being changed by documentation alone.

**Non-closure stance.** The candidate devotes its own `Current Non-Closure`
section to explicitly enumerating why it does not close the installer
blocker. The gate script returns `installer_closes_release_blocker: False`
unconditionally. This is correct design for a review-stage candidate.

**Prior review alignment.** The call-for-review's claim state matches the
prior eleven-row release-readiness review and Codex consensus. The prior
Claude review named `general_release_installer_not_ready` as P0 blocker 4
and described exactly this candidate path as the narrow scoped option. The
current candidate operationalizes that description correctly.

---

### What requires amendment

**Missing Numba CUDA path exports.** The runbook (section "Python GPU
Partner Gate") documents the following required environment configuration:

```bash
export NUMBA_CUDA_PREFIX=/path/to/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
```

These are required for Numba to locate the NVVM compiler and CUDA libraries.
The GPU env gate checks `numba_cuda_jit: pass`. Without the Numba CUDA
prefix exports, Numba CUDA JIT fails even after `v3_install_gpu_pod_env.sh`
runs successfully. The candidate does not mention these exports. A user
following only the candidate cannot reproduce `numba_cuda_jit: pass` and
therefore cannot confirm the GPU partner gate passes. This is a P0 gap in
the candidate document itself.

**CUDA minor version mix unexplained in the candidate.** The package set
installs `nvidia-cuda-nvcc-cu12==12.4.131` (CUDA 12.4) alongside
`nvidia-cuda-nvrtc-cu12==12.9.86` and `nvidia-cuda-runtime-cu12==12.9.79`
(CUDA 12.9). The install script's comment explains this ordering exists
because CuPy 14.1.1 needs newer CUDA 12.9 NVRTC wheels and resolver
warnings may appear. The candidate document documents the
`cuda-bindings/CUDA 13/driver 12` warning but does not explain the
nvcc-12.4 / nvrtc-12.9 / runtime-12.9 mix or reference the install
script's comment. This is not a blocking amendment — the mix is documented
in the install script and the running pod passed all gates — but adding a
one-line note in the candidate would prevent a reviewer from flagging it as
an unexplained inconsistency.

**Library path is a placeholder.** The candidate shows:
```bash
export RTDL_OPTIX_LIBRARY=/path/to/current/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=/path/to/current/build/librtdl_embree.so
```
A note should indicate that these paths are the output of `make build-optix`
and `make build-embree` respectively, and that the user must substitute the
actual build output path. The runbook does not use a placeholder; it
references the same `/path/to/current/build/` form. This is acceptable as-is
(both use the same placeholder convention) but the candidate should say
explicitly that substitution is required.

---

## Answers To The Six Questions

**Q1: Is the candidate concrete enough to mark
`source_tree_pod_gated_candidate_reviewed: true`, assuming Codex reaches the
same consensus?**

Yes, conditional on the Numba CUDA path exports amendment. Once that is
added to the candidate document, the candidate is concrete enough to mark
reviewed: it names all required package pins, build commands, runtime env
vars, install flag, gate commands, and expected gate outputs. The gate
script would then verify the complete path. Without the Numba exports, a
reproduced environment cannot reach `numba_cuda_jit: pass` from the
candidate alone, and `reviewed: true` would be misleading.

**Q2: Does the candidate close the installer/reproducibility blocker for a
narrow source-tree/pod-gated V3 scope, or must `installer_closes_release_blocker`
remain `false`?**

`installer_closes_release_blocker` must remain `false`. The candidate
correctly says so, the gate enforces it, and the blockers doc is consistent.
Closing that field requires one of: (a) 2-AI consensus that explicitly
accepts source-tree/pod-gated as the release scope and updates the gate, or
(b) a general package installer built and reviewed separately. Neither is
in scope for this candidate review. The candidate's role is to be a concrete
reviewable artifact, not to close the blocker by itself.

**Q3: If it does not close the blocker, what exact missing work is required?**

The installer blocker requires one of two paths:

- **Narrow scoped path:** After this candidate is marked reviewed and Codex
  records consensus, produce explicit scoped release wording of the form
  "V3 performance evidence is reproducible from the source tree on the
  documented RTX pod environment; general package installer not available."
  That wording must receive 2-AI reviewed consensus, the gate's
  `required_next_action` target must be met, and the gate must be updated to
  record `installer_closes_release_blocker: true` under the scoped release
  scope. This is the shorter path given the current evidence base.

- **General installer path:** Build reviewed general release install docs
  and a package install procedure that does not require project-history
  knowledge or an experimental flag. The gate's `general_release_installer_ready`
  field then becomes `true`. This is the longer path.

No other missing work blocks the candidate review itself. The second-hardware
evidence, wording scanner upgrade, and public doc reviews are all open P0/P1
items but are not required to mark this candidate reviewed.

**Q4: Are the required commands, package pins, native backend build steps,
runtime library exports, and GPU environment gate sufficient for a serious user
to rerun the evidence on the documented pod class?**

Sufficient except for the missing Numba path exports. Specifically:

- Package pins: sufficient. Six packages, exact versions, PyTorch from cu124
  index.
- Native build steps: sufficient. `make build-embree` and `make build-optix
  OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0` are correct for the
  2026-06-20 pod.
- Runtime library exports: sufficient for OptiX and Embree. Three variables
  (`RTDL_OPTIX_LIBRARY`, `RTDL_OPTIX_LIB`, `RTDL_EMBREE_LIBRARY`) are
  all documented.
- PYTHONPATH: sufficient. `export PYTHONPATH=src:.` is present.
- GPU environment gate: sufficient. The command and expected pass result are
  documented.
- Numba CUDA compiler path: **not present** in the candidate. Required to
  reach `numba_cuda_jit: pass`.
- Pod hardware: sufficient context. RTX 4000 Ada, driver 550.127.05, OptiX
  SDK 8.0.0 are all in the runbook and are consistent with the candidate.

**Q5: Does the candidate preserve the correct negative boundaries?**

Yes, fully.

| Boundary | Present and enforced? |
| --- | --- |
| Not a general release installer | Yes — stated in candidate, in install script usage, in runbook, in blockers doc; gate checks phrase |
| Not package-install wording | Yes — stated in candidate; `package_install_claim_authorized: false` in expected gate output |
| Not release authorization | Yes — stated in candidate; `release_authorized: false` in expected gate output |
| Not second-RTX confirmation | Yes — stated in candidate; secondary platform gate is separate |
| Not broad V3-over-V2 speedup | Yes — stated in candidate; `blocked_not_release` status preserves this |
| Experimental flag required | Yes — gate verifies installer refuses without flag |
| Candidate itself unreviewed | Yes — `source_tree_pod_gated_candidate_reviewed: false` in expected output; gate hardcodes this |

**Q6: What exact amendments must Codex make before the install gate can record
this candidate as reviewed?**

**Required (P0 amendment):**

Add the following Numba CUDA path exports to the "Required Commands" section
of `docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md`,
after the runtime library export block and before the install script
invocation:

```bash
export NUMBA_CUDA_PREFIX=/path/to/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
```

The path prefix depends on the venv location on the pod; the candidate should
note this. The runbook already documents these exports in its "Python GPU
Partner Gate" section. The amendment brings the candidate into parity with
the runbook for this step.

**Recommended (non-blocking):**

1. Add a note after the library path exports clarifying that the
   `/path/to/current/build/` placeholder must be replaced with the actual
   output path from `make build-embree` and `make build-optix`.
2. Add a one-line note in the "Package Set" section explaining that
   `nvidia-cuda-nvcc-cu12==12.4.131` (CUDA 12.4) intentionally differs in
   minor version from `nvidia-cuda-nvrtc-cu12==12.9.86` and
   `nvidia-cuda-runtime-cu12==12.9.79` (CUDA 12.9), and that resolver
   warnings may appear but gates pass on the tested pod.

No gate script changes are required for the review itself. After Codex
records consensus, Codex should change `source_tree_pod_gated_candidate_reviewed`
from `False` to `True` in `scripts/v3_phoenix_install_reproducibility_gate.py`
and update the gate payload accordingly.

---

## Install Gate Recommendation

| Field | Current value | After this review + Codex consensus |
| --- | --- | --- |
| `source_tree_pod_gated_candidate_present` | `true` | `true` — no change |
| `source_tree_pod_gated_candidate_reviewed` | `false` | `true` — update gate after P0 amendment confirmed by Codex |
| `general_release_installer_ready` | `false` | `false` — no change |
| `package_install_claim_authorized` | `false` | `false` — no change |
| `installer_closes_release_blocker` | `false` | `false` — no change |
| `release_authorized` | `false` | `false` — no change |
| Gate status | `staged_pod_gate_present_general_release_installer_not_ready` | `staged_pod_gate_present_general_release_installer_not_ready` — no change |

Only `source_tree_pod_gated_candidate_reviewed` should change, and only after:

1. The P0 amendment (Numba exports) is added to the candidate.
2. Codex records consensus accepting this review.
3. The gate script is updated to reflect `source_tree_pod_gated_candidate_reviewed: True`.

The overall gate status does not change. The install blocker does not close.
`release_authorized` does not change.

---

## Claim Boundary Check

| Claim | Authorized by this candidate? | Notes |
| --- | --- | --- |
| Phoenix V3 evidence is reproducible from the source tree on the documented RTX pod | Yes, after P0 amendment | Narrow wording only; requires explicit pod class disclosure |
| General package installer available | No | `general_release_installer_ready: false` enforced |
| `pip install rtdl` gives V3 GPU | No | `package_install_claim_authorized: false` enforced |
| V3 release authorized | No | `release_authorized: false` enforced; `blocked_not_release` status maintained |
| Broad V3-over-V2 speedup | No | Not within this candidate's scope; remains blocked by aggregate gate |
| V3 performance confirmed across RT-core hardware | No | Single RTX 4000 Ada pod; secondary platform gate separate |
| Second-RTX confirmation via this candidate | No | Explicitly out of scope; separate gate handles this |
| Source-tree/pod-gated reproducibility candidate reviewed | Yes, after P0 amendment and Codex consensus | `source_tree_pod_gated_candidate_reviewed: true` is the correct next state |

---

## Evidence Gaps Or Weak Sources

**Numba CUDA JIT cannot be confirmed from the candidate alone.** This is the
primary evidence gap for the candidate document itself. The install script
installs `numba==0.65.1` and the gate checks `numba_cuda_jit: pass`, but the
Numba CUDA compiler path setup is absent from the candidate. Until the P0
amendment is applied, a user following the candidate cannot confirm this gate
passes. The runbook covers this, but the candidate is supposed to be the
standalone reproducibility document.

**No git head in the candidate.** The candidate does not record the git commit
at which it was written. This is consistent with other Phoenix artifacts that
record `source_manifest.sha256` instead, but it means the candidate cannot be
independently verified as corresponding to a specific commit without cross-
referencing. This is a pre-existing limitation of the Phoenix artifact chain,
not a flaw specific to this candidate.

**Single pod class.** The candidate's wording correctly limits performance
claims to "the documented RTX pod class." No second pod has run the same
gate sequence. This is not a flaw in the candidate — it is an honest
disclosure — but it means the candidate's reproducibility claim is hardware-
narrow. Any reviewer who acts on this candidate must read the scope as a
single-hardware claim.

**CUDA bindings major version warning.** The candidate documents the warning
(`cuda-bindings was built for CUDA major version 13, but the NVIDIA driver
only supports up to CUDA 12`) and says to keep it visible until resolved. It
does not state why the warning is non-blocking for the current gate set. The
runbook notes "The current Phoenix pod rows passed despite this warning," which
is sufficient context for the runbook; the candidate should carry the same
statement.

---

## Suggested Next Sequence

**Step 1 — Apply the P0 amendment (Codex).**
Add the Numba CUDA path exports to the candidate's "Required Commands" section.
Optionally add the recommended non-blocking notes on the library path
placeholder and CUDA minor version mix.

**Step 2 — Codex records consensus.**
After applying the amendment, Codex records its consensus with this review.
The consensus document should state the verdict (`approve-with-amendments-not-release`),
confirm the amendment was applied, and confirm that `source_tree_pod_gated_candidate_reviewed: true`
is the correct next gate state.

**Step 3 — Update the gate script (Codex).**
In `scripts/v3_phoenix_install_reproducibility_gate.py`, change the hardcoded
`source_tree_pod_gated_candidate_reviewed: False` value to `True` in both the
evidence dict and the top-level payload. All other gate fields remain unchanged.
Run the gate and confirm it still returns status
`staged_pod_gate_present_general_release_installer_not_ready` with
`source_tree_pod_gated_candidate_reviewed: true`.

**Step 4 — Decide installer blocker path.**
This candidate review enables, but does not complete, closing the installer
blocker. The next decision is: narrow scoped release wording (shorter) or
general package installer (longer). The prior Claude eleven-row review and
Codex consensus both describe this choice. Make the product-scope decision and
record it machine-readably.

**Step 5 — Close secondary hardware blocker or write waiver.**
Installer and secondary hardware are both P0 blockers. They can be worked in
parallel. A second RTX-class run or a 2-AI-reviewed hardware-scoped waiver
closes the secondary platform blocker.

**Step 6 — Request a new aggregate release-readiness external review.**
After installer blocker is closed (Step 4) and secondary hardware is closed
(Step 5), request an updated release-readiness review. That review must
explicitly supersede the current `claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0`
consensus.

---

This review does not authorize release. It does not update any machine-readable
gate field. It is candidate review material only. The aggregate release gate
must continue to return `blocked_not_release` until the P0 blockers described
in the prior eleven-row review and in this review are closed by separate work.
