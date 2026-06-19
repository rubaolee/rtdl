# Addendum: Proposed Resolutions for V4.0 Open Design Decisions (D1–D5)

**Author:** Claude (independent technical reviewer) · **Date:** 2026-06-19
**Companion to:** `docs/engineering/rtdl_v4_0_design_review_packet_2026-06-19.md`
**Purpose:** Drop-in decision text the maintainers can paste into the packet's *Open Design Decisions* section. Each item states the decision, the rationale, and the test/gate that enforces it. Phrased so it can be accepted, amended, or rejected per item.

---

## D1 — Result-size and output-allocation contract

**Decision (proposed):** Support two output modes on every query route, selectable in `rtdl_query_desc`:

1. **RTDL-owned result.** RTDL allocates; caller receives an `rtdl_result` handle and reads count/rows via accessors; caller calls `rtdl_result_destroy`.
2. **Caller-provided output.** Caller passes an output buffer (host or device) plus capacity. RTDL fills up to capacity and always writes the *required* count. If `required > capacity`, RTDL writes nothing past capacity and returns `RTDL_STATUS_RESULT_TRUNCATED` with the required count, enabling a size-then-fill second call.

**Rationale:** Output cardinality is unknown before execution for overlap/neighbor/hit-stream routes. Mode 1 is the simple default; mode 2 is mandatory for the "framework-owned device tensor output" goal — without it, a PyTorch/CuPy host cannot receive results into its own tensor and the embedding value is lost.

**Gate:** every shipped route has tests for both modes, including the truncation path (`required > capacity`) and the exact-fit boundary (`required == capacity`).

---

## D2 — ABI struct extensibility

**Decision (proposed):** Every descriptor struct begins with `size_t struct_size` set by the caller. RTDL reads only fields within the caller-declared size and treats absent trailing fields as defaults. No descriptor field is ever removed or repurposed within a major version; new fields are appended only.

**Rationale:** Fixed structs passed by pointer cannot gain fields after 1.0 without an ABI break. A leading `struct_size` lets minor versions append optional fields while old callers keep working. (A `sType`/`pNext` chain is the alternative; `struct_size` is simpler and sufficient for the current descriptor count — adopt the chain only if a route needs heterogeneous optional extensions.)

**Gate:** a layout-audit test pins `offsetof` of every existing field; a test builds an old-size descriptor against a new-size struct and confirms forward compatibility.

---

## D3 — Capability query mechanism

**Decision (proposed):** Collapse per-question capability symbols into one enum-keyed call:

```c
rtdl_status rtdl_query_capability(
    const rtdl_context* context,
    const rtdl_route_desc* route,   /* nullable: context-level queries */
    rtdl_capability cap,            /* RTDL_CAP_ACCEPTS_DEVICE_BUFFERS, ... */
    uint64_t* value_out);
```

New capabilities are new `rtdl_capability` enum values, not new exported symbols. `rtdl_backend_is_supported` / `rtdl_route_is_supported` may remain as thin convenience wrappers or be retired before 1.0.

**Rationale:** Typed per-question functions make every future capability a permanent ABI symbol. An enum-keyed query grows capabilities without growing the symbol surface, and pairs naturally with D2.

**Gate:** capability enum has a stability policy (values never reused); a test asserts unknown capability values return `RTDL_STATUS_UNSUPPORTED`, not UB.

---

## D4 — Robustness and input validation

**Decision (proposed):** Every descriptor crossing the ABI is validated before use. RTDL returns `RTDL_STATUS_INVALID_ARGUMENT` (never UB) for: null `data` with nonzero `byte_count`; `ndim` beyond the documented max rank; `byte_count` inconsistent with `shape × strides × itemsize`; integer overflow in that product; unsupported dtype/layout/alignment. Borrowed device pointers are **caller-asserted**: RTDL documents that it cannot verify device-pointer validity, residency, or liveness, and that violations are undefined behavior owned by the caller.

**Rationale:** An embeddable native library consuming caller pointers/shapes/strides is a crash and attack surface. "Fail closed on unsupported routes" does not cover malformed input. The borrowed-device-pointer limitation must be explicit so hosts do not assume protection the ABI cannot provide.

**Gate:** negative-test suite for each malformed-input class above; a documented statement of caller-asserted device-pointer responsibility in the ownership/threading contract.

---

## D5 — Freeze timing and first route

**Decision (proposed):**
- **Versioning:** V4.0 ships as a **pre-1.0 (0.x) experimental SDK**. The ABI is not frozen to 1.0 until at least one real (non-toy) external host has driven the device-buffer route end to end. Public docs use "source-tree / experimental SDK" wording until install/package and cross-version gates pass.
- **First routes:** Prove the boundary with the boring **host F32 AABB2 overlap** route (plumbing, packaging, bindings). Commit in the same milestone window to a second, **benchmark-valuable** route — fixed-radius neighbors or ray/triangle any-hit — as the ABI-shaping route, so the descriptor/result/stream design is validated against a workload a real consumer wants.

**Rationale:** D1/D2 shapes cannot be confirmed correct until a framework actually uses them; freezing 1.0 on a host-only AABB2 toy route risks freezing the wrong descriptor. AABB2 proves plumbing but attracts no consumer to stress ownership/stream edges; a benchmark-valuable route does.

**Gate:** release-wording test forbids "stable SDK" and "1.0 ABI" strings until the install/compat gates and one external device-buffer consumer are recorded; the second route appears in the M3–M6 test matrix, not deferred to V4.x.

---

## Summary table

| ID | Decision | Primary gate |
| --- | --- | --- |
| D1 | RTDL-owned + caller-provided output, with `RESULT_TRUNCATED` + required-count | both-mode + truncation tests per route |
| D2 | Leading `struct_size` in every descriptor; append-only fields | `offsetof` pin + old-size forward-compat test |
| D3 | Enum-keyed `rtdl_query_capability`; capabilities are enum values | unknown-capability fail-closed test |
| D4 | Validate all descriptors → `INVALID_ARGUMENT`; device pointers caller-asserted | malformed-input negative suite |
| D5 | Ship 0.x experimental; freeze only after a real device-buffer consumer; AABB2 + one benchmark route | wording gate + second-route in M3–M6 matrix |
