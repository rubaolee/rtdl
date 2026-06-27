# Goal2988 Consensus: Goals 2984-2985 Second-Architecture Bounded Packet

Date: 2026-06-01

Status: Codex + Gemini + Claude consensus; no release authorization

## Purpose

Goal2988 records the external-review consensus for:

- Goal2984 Barnes-Hut second-architecture profile policy;
- Goal2985 RTX 4000 Ada second-architecture bounded seven-app packet.

Review files:

- `docs/reviews/goal2986_gemini_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md`
- `docs/reviews/goal2987_claude_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md`

## Consensus Verdict

Consensus verdict: **accept-with-boundary**.

The consensus is:

- Goal2984 successfully makes the bounded Barnes-Hut second-architecture profile
  explicit, named, fail-closed, and non-silent.
- Goal2985 provides a valid clean 7/7 RTX 4000 Ada packet for the bounded
  second-architecture scope.
- The operational part of the Goal2977 gap is closed.
- The release-scope policy question remains open and must be explicit in any
  future release packet.
- No public release, public speedup, broad RT-core speedup, whole-app speedup,
  true zero-copy, package-install, paper-reproduction, or app-specific-engine
  claim is authorized.

## Reviewer Findings

| Reviewer | Verdict | Key finding |
| --- | --- | --- |
| Gemini | `accept-with-boundary` | The bounded profile is explicit, the packet is clean 7/7 for that scope, and release-scope policy remains open. |
| Claude | `accept-with-boundary` | The runner default is not weakened, the packet is valid, and the profile/validation scope must be carried into release text. |
| Codex | `accept-with-boundary` | Implementation, pod evidence, and tests are coherent; release remains blocked until a user-requested release packet and fresh 3-AI release consensus. |

## Carry-Forward Conditions

Any future v2.5 release packet that uses Goal2985 evidence must carry these
conditions:

1. **Profile scope:** second-architecture Barnes-Hut evidence uses
   `second_arch_bounded`; the 8192-body Embree CPU baseline remains unmeasured
   on RTX 4000 Ada.
2. **Validation scope:** the 2048-body Barnes-Hut row uses the established
   first-case-reference plus all-case shape-parity validation policy, not full
   value/reference validation for every case.
3. **Release wording:** internal RT-core ratios and speedup numbers must stay
   internal evidence unless a future release packet explicitly scopes and
   reviews them.
4. **Partner wording:** CuPy winning the Barnes-Hut vector-sum continuation by
   same-contract timing is a measured partner-selection result, not a broad
   partner superiority claim.

## Boundary

Goal2988 does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.

The next valid release-lane action is to decide whether to prepare a
user-requested v2.5 release packet. If the user asks for that packet, it must
include Goal2988's carry-forward conditions and then go through fresh final
3-AI release consensus.
