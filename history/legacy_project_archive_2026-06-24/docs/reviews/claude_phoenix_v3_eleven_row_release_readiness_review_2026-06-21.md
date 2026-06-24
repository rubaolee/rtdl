# Claude Review: Phoenix V3 Eleven-Row Release Readiness

Reviewer: Claude Sonnet 4.6 (external, local Windows Claude Code)
Date: 2026-06-21
Files read: all seventeen listed in the call-for-review.

Verdict: `not-release-ready-fix-p0`

---

## Bottom Line

The eleven-row surface is real, honest, and meaningfully stronger than the
prior six-row surface. The active generic-engine queue is correctly closed.
Going from six to eleven M7-qualified row-scoped results — each with
Claude+Codex review, exact row IDs, phase/wall evidence, and oracle parity —
is genuine V3 progress. It is not enough to authorize release.

Three P0 blockers remain genuinely open and require concrete work before any
form of V3 release, even a narrow scoped one:

1. General release installer is not ready.
2. Secondary RT-core performance confirmation is not closed.
3. External release-readiness consensus has not been updated to cover the
   eleven-row surface.

These are not wording problems. They are packaging, hardware-evidence, and
process gaps. Until they close, `--strict-release` must exit nonzero and the
release-readiness gate must read `blocked_not_release`.

---

## Findings

### What is solid

**Row quality.** All eleven rows passed external Claude review, Codex
consensus, exact-row scoping, oracle or parity confirmation, and the M7
classification packet gate. None of them is inflated. The supplemental rows
(grouped_reduction device-column x2, AABB native query-handle x2, RTNN
prepared repeat50 x1) each required a separate call-for-review, evidence
packet, Claude verdict, and Codex consensus before counting.

**Closed queue.** The generic-engine active queue is correctly closed.
Grouped-reduction prepare amortization, AABB native prepared-query-handle
reuse, and RTNN prepared repeat50 are all closed for their exact rows. Spatial
RayJoin is correctly moved to future research after the Claude/Codex closure:
the exact-f64 repair is real internal progress (3.680x RTDL-vs-prior-RTDL),
but the RayJoin author Query timer remains 3.382x faster than the current RTDL
prepared-query median on the same dataset, and no M7 row exists. Barnes-Hut is
correctly retained as future research. Nothing in the queue was prematurely
promoted.

**Wording discipline.** The classification packet, wording gate, runbook, and
negative-route explanations are well-structured. Forbidden-wording lists are
explicit and machine-tested. The geomean V3-vs-V2.14 same-row timing (1.012x)
is disclosed honestly, and the four V3 losses (Barnes-Hut OptiX 32768 at
0.639x, spatial_rayjoin Embree at 0.855x, 0.917x, 0.942x) are not hidden.

**Classification packet.** The JSON packet correctly records
`release_authorized: false`, `broad_v3_faster_than_v2_claim_authorized:
false`, and `phoenix_m7_qualified_release_rows: 11`, with zero
`final_review_blocked_packets` and zero `public_claim_rows` (all eleven are
row-scoped only, not broad claims).

**Control surface.** The aggregate readiness gate script
(`v3_phoenix_release_readiness_gate.py --strict-release`) exiting nonzero is
the correct machine-readable signal. The current six active blockers are
accurately reflected in that gate.

---

### What is still blocking

**Installer.** `v3_phoenix_install_reproducibility_gate.py --pretty` returns
`staged_pod_gate_present_general_release_installer_not_ready`. The staged
installer (`v3_install_gpu_pod_env.sh`) requires
`--accept-experimental-pod-gate` and cannot be used by a user who lacks
project-history knowledge. Until a reviewed general install document or
explicit source-tree/pod-gate release wording (with 2-AI consensus) closes
this, the installer blocker is genuinely P0 — a release that users cannot
reproduce is not a responsible release.

**Secondary hardware.** `v3_phoenix_secondary_platform_gate.py --pretty`
returns `compatibility_confirmed_rt_performance_not_confirmed`. The `lx1` box
(`NVIDIA GeForce GTX 1070`) is correctly classified as compatibility evidence
only. GTX 1070 has no RT cores. Every M7 row was measured on a single RTX
4000 Ada pod. A major release with one-pod-only performance evidence carries
more hardware risk than the eleven-row surface alone would justify. This
blocker requires either a second RTX-class run or an explicit 2-AI-reviewed
hardware-scoped waiver.

**External release-readiness consensus.** The prior Claude+Codex consensus
(`codex_phoenix_v3_six_row_release_readiness_2ai_consensus_2026-06-21.md`)
was recorded for a six-row surface. Its blockers — installer, second machine,
wording scanner, product scope — remain unclosed. That document is still the
current release-readiness authority, and it says `release_authorized: false`.
Eleven rows do not automatically supersede a six-row consensus. A new
consensus must explicitly review the current eleven-row state and either
supersede the old document or close each of its named blockers.

**Broad V3-over-V2 claim.** The same-hardware paired run found 46 rows with
1.012x geomean, 10 wins over 5%, 32 parity rows, and 4 losses over 5%. The
broad V3-over-V2 speedup claim remains unauthorized, and this constraint does
not change with queue closure or row count. It can only be addressed by
targeted tuning of the losing rows plus a new paired run, or by explicitly
positioning V3 as a runability-first release without a performance-first
headline.

---

## Answers To The Five Questions

**Q1: Does the current eleven-row M7 packet, with the active generic-engine
queue closed, supersede the prior six-row release-readiness blocker?**

No. The prior six-row consensus named installer, second machine, wording
scanner, and product scope as the next blockers after row breadth. None of
those are closed. Closing the queue removes the `generic_engine_work_queue_open`
release blocker and advances the row count from 6 to 11, but the
infrastructure/process blockers — which the prior consensus explicitly called
the next priority — are all still open. The six-row consensus document is still
the current external release-readiness authority and has not been superseded.

**Q2: What exact P0 blockers remain before any V3 major release?**

The current aggregate readiness gate records these six:

1. `release_authorization_false` — no explicit release decision has been made.
2. `eleven_row_surface_still_too_narrow_for_major_release` — eleven exact
   row-scoped results, while real, do not constitute the broad reusable surface
   expected of a major release.
3. `broad_v3_faster_than_v2_claim_not_authorized` — 1.012x same-row geomean
   does not support this claim.
4. `general_release_installer_not_ready` — staged pod gate only.
5. `secondary_rt_performance_confirmation_not_closed` — one RTX pod only.
6. `external_release_readiness_consensus_blocks_major_release_wording` — prior
   six-row consensus not superseded.

Blockers 4, 5, and 6 are the actionable P0s: they require concrete new work,
not just a counter increment. Blockers 1, 2, and 3 are consequential: they
follow from the current evidence state and cannot be independently resolved
without addressing 4–6 and making a product-scope decision.

**Q3: Can V3 be responsibly positioned as a narrow source-tree/pod-gated,
row-scoped performance release, without claiming broad V3-over-V2 speedup?**

Yes, in principle — but not in the current state. The eleven rows are honest
and externally reviewed. Scoped wording of the form "eleven exact row-scoped
OptiX/Embree speedups on an RTX 4000 Ada pod, reproducible from the source
tree with the documented pod environment" is factually supportable. But
responsible scoped release requires at minimum: (a) the installer or pod-gate
is explicitly documented as the release reproducibility path with 2-AI
reviewed wording, (b) the single-hardware constraint is disclosed and
acknowledged (either via second-machine run or 2-AI-reviewed hardware-scoped
waiver), and (c) a new external release-readiness consensus covers the
eleven-row surface and this scoped positioning explicitly. None of those three
conditions is currently met.

**Q4: Are the remaining blockers mainly engineering blockers, release
packaging blockers, secondary-hardware evidence blockers, public-doc wording
blockers, or product-positioning blockers?**

Breakdown:

- **Release packaging blockers (P0):** installer not ready — requires writing
  reviewed general install docs or explicit pod-gate scoped release wording.
- **Secondary-hardware evidence blockers (P0):** RT performance not confirmed
  on second machine — requires either a second RTX run or a 2-AI-reviewed
  hardware-scoped waiver.
- **Product-positioning blockers (P0):** eleven-row surface narrow for a major
  release; external consensus must be updated; broad speedup claim blocked.
- **Engineering blockers:** none. The generic-engine queue is closed. No
  engine work is required before a scoped release can be reviewed.
- **Public-doc wording blockers (P1):** wording scanner is first-pass only,
  not final-gate level; tutorials need final review; app catalog, backend
  maturity, and performance model external reviews are blocked.

There is no remaining generic-engine work on the critical path to release.
All remaining P0 blockers are packaging, hardware, and process.

**Q5: What concrete improvement sequence should Codex do next?**

See the Suggested Next Sequence section below.

---

## P0 Blockers

| Blocker | Current status | Required to close |
| --- | --- | --- |
| `general_release_installer_not_ready` | Staged pod gate requires `--accept-experimental-pod-gate`; not a general installer | Write reviewed install docs or explicit source-tree/pod-gate release scope with 2-AI wording; `installer_closes_release_blocker: true` in the gate |
| `secondary_rt_performance_confirmation_not_closed` | `lx1` is GTX 1070, no RT cores; RT performance not confirmed on second machine | Run eleven M7 rows (or a validated subset) on a second RTX/RT-core machine, OR explicit 2-AI-reviewed hardware-scoped waiver stating single-hardware scope |
| `external_release_readiness_consensus_blocks_major_release_wording` | Prior six-row Claude+Codex consensus not superseded; its named blockers (installer, second machine, scanner, product scope) still open | New external release-readiness review of the eleven-row surface that explicitly supersedes the prior consensus, OR close each of its named blockers individually with 2-AI review |
| `eleven_row_surface_still_too_narrow_for_major_release` | 11 exact rows across 10 apps, one hardware point, no general installer, one-sided V3/V2 parity | Close together with installer + second machine + product-scope decision; if positioning as scoped/pod-gated preview, this can be resolved via explicit scope agreement in the new consensus |
| `broad_v3_faster_than_v2_claim_not_authorized` | Same-row geomean 1.012x; 4 V3 losses over 5% | Tune losing rows + new paired run, OR explicitly position V3 as runability-first with exact-row performance and 2-AI agreement; the board claim must remain false regardless |
| `release_authorization_false` | Explicit product release decision not made | Follows from all above; resolved when product-scope decision is recorded and all other P0s close |

---

## P1/P2 Improvements

**P1:**

- Wording scanner (`v3_release_wording_gate.py`) is described as
  "first-pass gate" throughout all documents. Upgrade it to a final
  release-authorization scanner before the release wording is finalized.
- App catalog, backend maturity, and performance model external reviews are
  blocked (`external_review_blocked_phoenix_v3_public_docs_rebuild_surface_2026-06-21.md`).
  Unblock these before any public-facing release doc is signed off.
- Tutorial surface (tutorials 07–15 covering grouped_sum through Contact
  Manifold) needs a final reviewer acceptance that it is coherent enough for
  a V3 release-review surface.
- The `lx1` / GTX 1070 secondary-compatibility evidence is well-documented,
  but the write-up of "compatibility-only, not performance" must appear in
  the actual release docs so a reader cannot infer RT-core evidence from the
  second-machine citation.

**P2:**

- The V2.14-vs-V3 paired run's four V3 losses (Barnes-Hut OptiX 32768 at
  0.639x; Spatial RayJoin Embree rows at 0.855x, 0.917x, 0.942x) are
  currently documented as requiring tuning or explanation before any
  performance-first V3 release wording. If V3 is positioned as
  runability-first with no broad speedup claim, these losses must be visible
  in release docs rather than buried; if performance-first, tuning is needed.
- CUDA major version warning (`cuda-bindings was built for CUDA major version
  13, but the NVIDIA driver only supports up to CUDA 12`) should be resolved
  or explicitly documented as harmless before public release.
- System Python packaging gap (`phoenix_m4_system_python_missing_cupy_numba`)
  should be noted in install docs even if V3 requires the pod venv.

---

## Suggested Next Sequence

The following sequence unblocks V3 release in the shortest path that remains
honest:

**Step 1 — Product-scope decision (no code).**
Decide: full major release (broad surface, general installer, second RTX) or
source-tree/pod-gated narrow release (eleven exact rows, documented pod
requirement, hardware-scoped wording). This decision gates the rest of the
sequence. Both paths are defensible; neither is currently authorized.

**Step 2 — Close installer/reproducibility blocker.**
If pod-gated: write reviewed release docs that explicitly scope the release as
"source-tree, RTX pod required, exact pod setup documented," get 2-AI consensus,
and update `v3_phoenix_install_reproducibility_gate.py` to reflect
`installer_closes_release_blocker: true` under that scope. If general: build
a general install package and document it with a reviewer pass.

**Step 3 — Close secondary-hardware blocker.**
If a second RTX-class machine is available: run the eleven M7 rows (or a
reviewed subset) and intake the evidence. If not: write an explicit
hardware-scoped waiver ("V3 performance evidence is on a single NVIDIA RTX
4000 Ada pod; second-machine RT core confirmation not available at release"),
obtain 2-AI consensus, and update `v3_phoenix_secondary_platform_gate.py` to
reflect the waiver.

**Step 4 — Obtain a new external release-readiness consensus.**
Request a new external review of the current eleven-row state using a call-for-
review structured like this one, after Steps 2 and 3 are complete. The new
consensus document must explicitly supersede
`codex_phoenix_v3_six_row_release_readiness_2ai_consensus_2026-06-21.md`.

**Step 5 — Upgrade wording scanner to final-gate level.**
Extend `v3_release_wording_gate.py` so it is a complete release-authorization
scanner, not a first-pass gate, and passes the new scoped release docs.

**Step 6 — Unblock public-doc external reviews.**
Get the app catalog, backend maturity, and performance model reviewed before
any release candidate is tagged.

**Step 7 — Make the release product-scope decision machine-readable.**
Record the product-scope decision in `v3_phoenix_release_readiness_gate.py`
(e.g., `release_scope: source_tree_pod_gated_eleven_row` or `full_major`).
Run `--strict-release` and confirm it exits zero only after all the above
steps are confirmed closed.

---

## Claim Boundary Check

| Claim | Authorized | Notes |
| --- | --- | --- |
| Eleven exact row-scoped M7 results with Claude+Codex review | Yes, row-scoped only | Each row ID must be quoted exactly; no generalization to whole-app, paper, or broad V3 |
| Broad V3-over-V2 speedup | No | 1.012x geomean; four losses; explicitly blocked in all documents |
| RTDL beats RayJoin author | No | Author Query 1.866 ms vs RTDL 6.309 ms; 3.382x author advantage |
| Single-pod performance evidence | Yes, if disclosed | Must disclose "NVIDIA RTX 4000 Ada Generation, driver 550.127.05, single pod" |
| RTNN repeat50 prepared-session win | Yes, row-scoped | 7.889x hot-query only with 1.315x cold-plus-query and repeat50 scope mandatory; float32 vs float64 CuPy grid disclosure required |
| AABB native query-handle 1.719x/1.637x | Yes, row-scoped | OptiX prepare remains slower; speedup is cold-prepare-plus-collect end-to-end |
| Grouped-reduction device-column 3.599x/73.586x host-packed OptiX vs device-column | Yes, row-scoped | Must disclose Embree is host-packed; 218.248x cold-prepare phase ratio must not be headline |
| Package-install claim | No | `package_install_claim_authorized: false` in gate |
| V3 release authorization | No | Gate returns `blocked_not_release`; `--strict-release` exits nonzero |

---

## Evidence Gaps Or Weak Sources

**Single-hardware point.** All eleven M7 rows were produced on one RTX 4000
Ada pod (root@213.173.108.14 -p 11592, driver 550.127.05). The secondary
platform (`lx1`, GTX 1070) provides compatibility evidence only. A single-pod
evidence base is not a strong foundation for a public major release claim.

**No git head in several evidence packets.** The RTNN repeat50 packet, the
AABB native query-handle packet, and the grouped-reduction device-column
packet all record `fatal: not a git repository` for `git_head`. Provenance
rests on SHA-256 source manifests only. The manifests are accepted by both
Claude and Codex, but this is weaker than committed-head provenance. Each
packet correctly names the manifest path; release docs must cite the SHA-256
basis explicitly.

**RTNN baseline is CuPy uniform-grid CUDA-core, not state-of-the-art NN.**
The approved RTNN row uses a CuPy uniform-grid CUDA-core reference, not FAISS,
cuML, or the RTNN paper implementation. The row is honest about this, but the
wording must never generalize to "beats nearest-neighbor methods" or omit the
baseline identity.

**1.012x same-row geomean.** The V2.14-vs-V3 paired run produced 46 same-
metric rows with 1.012x geomean and 4 V3 losses over 5%. This is disclosed
honestly throughout, but it means V3 cannot claim broad performance leadership
over V2.14. Any release wording that implies a broad speedup narrative would be
unsupported.

**Wording scanner is first-pass only.** The current `v3_release_wording_gate.py`
passes, but it is explicitly described as a first-pass scanner in all
documents, not a final release-authorization scanner. It has not been upgraded
to catch every possible overclaim path. Passing the first-pass gate is not the
same as having a complete release wording audit.

**External doc reviews blocked.** The app catalog, backend maturity, and
performance model have been rebuilt and pass local tests, but external review is
blocked at
`docs/reviews/external_review_blocked_phoenix_v3_public_docs_rebuild_surface_2026-06-21.md`.
These docs have not been independently verified.

---

This review does not authorize release. It does not supersede the prior six-row
Claude+Codex consensus. The aggregate release-readiness gate must remain
`blocked_not_release` until the P0 blockers above are closed by concrete work
and a new 2-AI consensus.
