Here are my answers to the seven reviewer questions.

---

## Goal 1394 — Public v1.5 Wording Review: Reviewer Answers

### Q1. Is the proposed wording supported by the cited Goal1393 evidence?

**Yes.** Every specific factual claim in the proposed wording is directly traceable to `stable_primitive_evidence.json` (source commit `c0b57ae`, platform Linux x86_64, Python 3.12.3):

| Proposed claim | Evidence field | Value |
|---|---|---|
| CPU hit count 256 | `direct_anyhit_count.cpu.hit_count` | 256, status ok |
| Embree hit count 256 | `direct_anyhit_count.embree.hit_count` | 256, status ok |
| OptiX hit count 256 | `direct_anyhit_count.optix.hit_count` | 256, status ok |
| Prepared OptiX hit count 256 | `prepared_optix_anyhit_count.hit_count` | 256, status ok |
| Parity (Embree, OptiX vs CPU) | `parity.embree`, `parity.optix`, `parity.optix_prepared_count` | all hit_count_matches true |
| All scalar reductions ok | `scalar_reductions.*` | COUNT_HITS, REDUCE_FLOAT(MIN/MAX/SUM), REDUCE_INT(COUNT/SUM) all status ok |
| Linux x86_64, Python 3.12.3 | `platform` block | system Linux, machine x86_64, python 3.12.3 |

No claim in the proposed wording exceeds or contradicts the evidence record.

---

### Q2. Does the wording avoid public speedup claims and whole-application claims?

**Yes.** The proposed wording contains no timing comparisons, no "faster than" language, no application names, and no GPU/NVIDIA speedup framing. It explicitly states: *"The public v1.5 scope is generic primitive readiness, not a universal compute engine and not a whole-application speedup claim."* The evidence JSON itself carries per-field `claim_boundary` annotations confirming the same: *"no app-specific visibility, graph, DB, polygon, or public speedup claim."* No violation of the prohibition on speedup or whole-application claims.

---

### Q3. Does the wording preserve source-tree usage and avoid package/install claims?

**Yes.** The proposed wording makes no reference to `pip install`, package distribution, or any install mechanism. It states "Python remains the app-specific control and lowering layer," which is consistent with source-tree usage. The wording does not assert that packages are available; the allowed-claims list separately records that the correct usage statement (`PYTHONPATH=src:. python ...`) is permissible to include when published. No package/install claim is introduced.

---

### Q4. Does the wording correctly keep `COLLECT_K_BOUNDED` experimental?

**Yes.** The proposed wording states verbatim: *"`COLLECT_K_BOUNDED` remains experimental."* This directly reflects the scope boundary declared in both Goal1393 (`COLLECT_K_BOUNDED` is not promoted by this packet) and the evidence JSON (`boundary` field). No stable promotion is implied.

---

### Q5. Does the wording correctly keep Vulkan, HIPRT, and Apple RT frozen before v2.1?

**Yes.** The proposed wording states verbatim: *"Vulkan, HIPRT, and Apple RT remain frozen before v2.1."* This matches the evidence JSON field `frozen_backends_before_v2_1: ["vulkan", "hiprt", "apple_rt"]` exactly. No active implementation or engineering activity for those backends is implied.

---

### Q6. Does the wording avoid implying a release/tag action has already happened?

**Yes, with a minor note.** The phrase *"RTDL v1.5 introduces a reviewed generic traversal-plus-reduction primitive layer"* uses present-tense "introduces," which in isolation could be read as an announcement of a current release. However, the wording contains no explicit release claim, no version-tag reference, no "now available" language, and no publication date. The packet header makes clear this is *"proposed for later public use only if 3-AI consensus accepts it,"* and the review packet's own Status section states that release/tag actions remain blocked. The proposed wording does not cross the line into asserting a release has occurred. When this wording is eventually published, authors should confirm that surrounding context does not frame the "introduces" verb as a live release announcement.

---

### Q7. Overall verdict

All six guardrails are intact:
- Every factual claim is directly evidenced.
- No speedup, whole-app, NVIDIA-broad, or GPU-performance claim is made.
- No package/install mechanism is claimed.
- `COLLECT_K_BOUNDED` is correctly held experimental.
- Vulkan, HIPRT, and Apple RT are correctly held frozen before v2.1.
- No release/tag action is implied (minor "introduces" ambiguity noted but not blocking, given packet framing).

**Verdict: ACCEPTABLE**
