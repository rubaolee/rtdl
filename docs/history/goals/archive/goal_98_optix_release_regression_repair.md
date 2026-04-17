# Goal 98: OptiX Release Regression Repair

## Objective

Repair the clean-clone OptiX prepared exact-source regression found during
Goal 94 release validation.

This is now the blocking technical goal before RTDL v0.1 release closure can
continue.

## Problem statement

The clean Linux clone at release head `c43f538` passed the broad release test
matrix, but the fresh exact-source OptiX prepared rerun on the accepted long
`county_zipcode` positive-hit `pip` surface failed both correctness and
performance expectations.

Observed failure summary:

- PostGIS row count:
  - `39073`
- OptiX row count:
  - `38799`
- parity:
  - `false`
- OptiX backend timing:
  - slower than PostGIS on both reruns

This contradicts the previously accepted OptiX package-level claims, so the
release must stop until the regression is explained and repaired.

## Required work

The goal must produce all of the following:

1. diagnosis report
- clearly identify the regression surface
- compare prior accepted OptiX claims against the fresh clean-clone failure
- identify the likely code path and failure mode

2. solution proposal
- explicit repair direction
- explicit non-goals
- explicit risk list

3. code repair
- minimal necessary code change set
- no unrelated cleanup

4. rerun result package
- fresh clean-clone Linux rerun on the same accepted surface
- updated summary artifacts
- explicit statement of whether parity and performance claims are restored

## Consensus requirement

This goal requires **3-way consensus**, not only 2-AI consensus.

Required reviewers:

- Codex
- Gemini
- Claude

Each of the following must be reviewed:

- diagnosis report
- solution proposal
- final code package
- final rerun result package

The goal is not done unless all four review surfaces have usable review
artifacts and the final package has a 3-way approval record or an explicit
documented split decision.

## Acceptance

Goal 98 is done only if:

- the root cause is diagnosed clearly
- the repair is implemented
- the clean Linux clone rerun restores:
  - parity on the accepted long exact-source prepared OptiX surface
  - the accepted claim boundary for OptiX
- Codex, Gemini, and Claude have all reviewed:
  - the diagnosis/proposal
  - the code
  - the rerun package

If parity is not restored, the goal can still close only as an explicit claim
retraction/degradation package, also with 3-way consensus.
