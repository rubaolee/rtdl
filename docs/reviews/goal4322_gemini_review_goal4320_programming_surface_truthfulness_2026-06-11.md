# External Review: Goal4320 Programming Surface Truthfulness

Date: 2026-06-11
Reviewer: Gemini CLI

## Verdict

`accept-with-boundary`

## Summary

Goal4320 successfully addresses the Fable5 review finding regarding documentation truthfulness for RTDL's programming surfaces. The documentation now clearly distinguishes between the teaching-oriented `@rt.kernel` DSL and the performance-oriented primitive/prepared front doors and partner continuations used in benchmarks. This change improves learner clarity by aligning documentation with the actual implementation and performance characteristics of the system.

## Check Results

1.  **Distinguishes Three Surfaces:** **PASS**. `docs/learn/programming_surfaces.md` explicitly names and defines the roles of `@rt.kernel`, primitive/prepared front doors, and partner continuation.
2.  **No Sole Performance Implication:** **PASS**. Updated docs (including `README.md`, `docs/rtdl/programming_guide.md`, and tutorials) now characterize the kernel shape as a "mental model" rather than the exclusive or guaranteed path to high performance.
3.  **App-Agnostic Engine and Primitive-First Rule:** **PASS**. The documentation maintains the core design principle that the native engine must remain app-agnostic and strongly encourages users to "start with primitive discovery."
4.  **Clean Public-Doc Scan:** **PASS**. `tests/goal4248_current_public_docs_claim_boundary_scan_test.py` passes, and the `docs/reports/goal4248_current_public_docs_claim_boundary_scan.json` artifact confirms that no unauthorized release, speedup, or packaging claims have been introduced.
5.  **Honest Scope Reporting:** **PASS**. The goal report (`docs/reports/goal4320_programming_surface_truthfulness_2026-06-11.md`) clearly states that this is a truthfulness and clarity step and does not implement a new lowering bridge or change runtime behavior.

## Observations

- The link structure for the new `programming_surfaces.md` page is comprehensive across the documentation front doors.
- The distinction between "teaching programs" and "promoted performance paths" in the `README.md` is a significant improvement in managing user expectations.
- The `Goal4320ProgrammingSurfaceTruthfulnessTest` provides good regression coverage for the core truthfulness phrases and link requirements.

## Boundaries

As noted in the goal report, this acceptance is bounded by the following:
- No new public claim surface is authorized.
- No runtime behavior changes or lowering improvements are part of this goal.
- Future work to make the kernel DSL the primary performance route will require separate engineering and evidence.
