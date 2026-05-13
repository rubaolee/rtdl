# Handoff: Goal1819 Direct Device-Pointer Descriptor Review

Please independently review Goal1819:

- `src/rtdsl/partner.py`
- `src/rtdsl/__init__.py`
- `tests/goal1819_partner_direct_device_pointer_descriptor_test.py`
- `docs/reports/goal1819_partner_direct_device_pointer_descriptor_2026-05-13.md`
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`

Context:

- Goal1814/1818 made v2.0 stricter. v2.0 remains blocked until true zero-copy,
  direct device-pointer handoff, broad RT-core evidence, whole-app evidence,
  arbitrary PyTorch/CuPy acceleration boundaries, and package-install/source-tree
  scope are resolved or removed by new 3-AI consensus.
- Goal1819 is a narrow implementation step for the direct device-pointer
  blocker only.
- It adds `RtdlDevicePointerHandoff` and
  `prepare_direct_device_pointer_handoff`.
- The API observes CUDA data pointer metadata from partner descriptors but must
  not claim native direct handoff or true zero-copy yet.

Review questions:

1. Does the API expose useful CUDA pointer metadata without authorizing native
   execution from the pointer?
2. Does it reject CPU tensors, zero/missing pointers, non-zero stream handles,
   and any attempt to set claim flags true?
3. Do the report and release gate clearly say Goal1819 does not satisfy the
   v2.0 blocker yet?
4. Are there any design risks before the next native OptiX device-pointer slice?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. State explicitly that this is Gemini and distinct from Codex.

Write the review to:

`docs/reviews/goal1820_gemini_review_goal1819_direct_device_descriptor_2026-05-13.md`
