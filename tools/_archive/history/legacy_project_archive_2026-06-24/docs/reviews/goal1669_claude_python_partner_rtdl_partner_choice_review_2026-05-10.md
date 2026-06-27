---

## Verdict

**Ship the design with three pre-implementation clarifications.** The architecture is sound: DLPack-as-contract, CuPy-first, switchable adapter registry, explicit fallback modes, and tiered claim boundaries are all correct calls. The app-agnostic engine boundary is well-specified and consistent with the Goal1668 gate. No structural rework needed. Three issues below need resolution before coding starts; the rest are documentation or deferral notes.

---

## Strengths

**Protocol-first is the right abstraction.** Using DLPack as the stable RTDL partner contract — rather than tying the engine to CuPy or PyTorch's object model — keeps future adapter additions from touching the engine ABI. This is the non-obvious right call, and the document explains it clearly.

**CuPy-first rationale is well-argued.** The reasoning in "Why CuPy First" (lines 115–136) is precise: CuPy tests exactly the ownership and device-residency problem without dragging in autograd, module/device conventions, or heavyweight install requirements. Proving the architecture on the simpler partner before adding PyTorch is disciplined sequencing.

**`RtdlTensorDescriptor` is explicit about what is forbidden.** Naming banned terms — `table`, `graph`, `polygon`, `robot`, `pose`, `database`, `BFS`, `KNN`, `Jaccard`, `Hausdorff` — is unusually good hygiene for a design doc. That list should go directly into a code review checklist.

**Claim-boundary rules are tiered correctly.** The three-stage progression (designing → functional-with-fallback → measured-device-resident) and the blocked-wording list (lines 338–343) are the strongest part of the document. They directly prevent the overclaim pattern that typically appears in release notes.

**Fallback policy is operationally concrete.** The `error`/`copy`/`host_stage` table (lines 251–258) with the requirement that benchmarks use `error` mode is exactly right. Most designs leave fallback implicit until a performance claim gets contested.

**Ownership and lifetime section is rare and valuable.** Most zero-copy designs skip this entirely. Calling out DLPack one-consumer rules, async CUDA lifetime, and explicit deallocation ownership before implementation is the correct order.

---

## Blocking Issues

**1. `partner=partner` on `rt.geometry.triangles()` is semantically underspecified (line 289).**
The public API sketch passes `partner=partner` to geometry construction, implying the geometry object is partner-tagged at creation time. The design does not answer: what happens if `rt.any_hit()` is called with a different partner than the one used to build the geometry? Is partner membership checked at the primitive call, at import, or at geometry creation? If geometry is partner-tagged, switching adapters mid-pipeline is silently broken. Clarify whether partner belongs on the geometry call or only on the primitive call, and define what a mismatch produces.

**2. `partner="auto"` detection is unspecified (line 175).**
The mode is listed but not defined. Both CuPy and PyTorch implement `__dlpack__` and `__cuda_array_interface__`. If auto-detection uses `hasattr(obj, '__dlpack__')`, selection is ambiguous for any object that satisfies both. The detection heuristic — priority order, tiebreak rule, behavior on unknown objects — must be defined before the registry is implemented, or `auto` will be a latent ordering bug.

**3. DLPack capsule vs. `__dlpack__` protocol is conflated (lines 236–241).**
The ownership section mentions "DLPack capsules" (strict one-consumer v0 semantics) and `__dlpack__`/`__dlpack_device__` (v1 PyCapsule protocol, different lifecycle rules) without distinguishing them. An adapter that mixes both paths without a canonical choice will have lifetime bugs that only appear under specific partner versions. The implementation must pick one path as primary, document it, and treat the other as a named fallback.

---

## Nonblocking Risks

**`stream_handle` in `RtdlTensorDescriptor` is untyped (line 199).** It is listed in the descriptor but has no type, no CUDA context mapping, and no validation spec. A wrong stream handle is a silent race condition. For the synchronous-first v1 implementation this is safe to leave unused, but it should be explicitly tagged as `/* reserved; must be 0 in v1 */` in both the design and code, so reviewers know it is intentional rather than forgotten.

**`lifetime_token` is a placeholder (line 201).** Same pattern: listed in the descriptor but undefined. Who creates it, who consumes it, and what RTDL does when it expires is not specified. Mark it reserved-for-v2 or define its type before implementation proceeds past Step 3 of the roadmap.

**CuPy test suite will not be sufficient for PyTorch (roadmap Step 6).** The roadmap says "same tests as CuPy, no engine ABI change." PyTorch tensors carrying autograd require `.detach()` before DLPack export; grad-enabled tensors will fail or produce incorrect descriptors. The CuPy tests cannot catch this. Add a PyTorch-specific test category covering grad-enabled inputs, leaf tensors, and `.detach()` behavior before claiming the PyTorch adapter is complete.

**`partner.empty()` allocation alignment is not enforced (line 292).** If CuPy allocates an output buffer but OptiX requires a specific alignment or pitch, RTDL can only validate after allocation, not control it. `allocate_output(spec)` needs a `spec` definition that includes alignment requirements, or RTDL needs a post-allocation validation step that fails loudly before launch.

**Embree partner path is thin (lines 217–220).** The OptiX+CuPy path is fully specified; the Embree+CPU partner path is two bullet points. Many users will hit Embree first on CPU-only systems. Add at least a sketch of the NumPy/Arrow host descriptor acceptance path and one named acceptance test, so the CPU partner story is not left open-ended at release.

**`rtdsl` vs. `rtdl` naming inconsistency.** The public API sketch uses `import rtdsl as rt` (lines 163, 283, 296) while the project is named RTDL throughout the document. If this is a real module name decision, note it explicitly. If it is a typo, fix it before external distribution.

---

## Recommendation

Resolve the three blocking issues — geometry `partner=` semantics, `auto` detection priority order, and canonical DLPack vs. `__dlpack__` path — in a short addendum or inline before implementation starts. These are design decisions, not code decisions, and resolving them now prevents a class of bugs that are expensive to find in adapter code.

The claim-boundary rules and fallback policy are production-ready as written. Gate them in CI from day one: the Step 5 "claim-boundary report" should be a generated artifact, not a manual document, so it cannot be skipped under release pressure.

The Goal1668 gate reference (line 48) is correct and should remain a hard dependency. The app-agnostic native internals claim must not advance independently of what Goal1668 controls.
