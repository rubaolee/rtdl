# RTDL Audit Flow

This document defines the live audit contract for RTDL code, docs, experiments,
and publication artifacts.

It is stricter than an ordinary code-review checklist because RTDL is not only
an implementation project. It also publishes:

- executable runtimes
- correctness claims
- benchmark claims
- paper-facing artifacts
- multi-AI consensus records

The purpose of this flow is to make acceptance decisions reproducible and to
make audit accountability explicit.

## 1. Audit Actions

Every serious audit should follow these steps in order.

### Step 1: Define the audit surface

State exactly what is being audited:

- code
- tests
- live docs
- historical/archive material
- experiment scripts
- reports
- slides
- paper source
- built PDF

The audit must also state what is explicitly out of scope.

### Step 2: Build the evidence set

Collect the exact artifacts that support the audited claim:

- source files
- tests
- commands run
- generated reports
- review memos
- commits
- PDFs or figures when presentation quality matters

An audit is weak if it relies on memory instead of concrete artifacts.

### Step 3: Check the implementation surface

Review the code for:

- correctness
- safety
- maintainability
- hidden assumptions
- failure modes
- portability boundaries

When the goal involves a backend, the audit must also check:

- ABI compatibility
- runtime loading behavior
- result-shaping semantics
- cleanup/lifecycle behavior

### Step 4: Check the documentation surface

Review the live docs for:

- factual correctness
- current-status accuracy
- absence of stale claims
- alignment with the accepted repo state
- correct links and references

Historical documents are not rewritten unless the task is specifically about
archive repair.

### Step 5: Check code/doc consistency

Audit whether the live docs describe the current code truthfully.

Common failure patterns:

- docs describe a feature that is not shipped
- code changed but the docs still describe an older design
- reports overstate what the test harness actually proves
- slides claim stronger maturity than the repo evidence supports

### Step 6: Check validation evidence

Run the appropriate verification layer:

- unit
- integration
- system
- full matrix

For correctness-sensitive goals, include parity checks against the relevant
reference:

- native C/C++ oracle
- PostGIS when the goal uses the external database checker

### Step 7: Record findings and classify them

Every finding must be classified as one of:

- blocking
- non-blocking
- informational

The classification must match the actual risk.

### Step 8: Seek cross-AI review

The primary auditor prepares an audit record.

Then the other AI reviewers check:

- whether the findings are real
- whether severity is correct
- whether the claims are honest
- whether the acceptance boundary is appropriate

### Step 9: Revise and rerun

If blocking issues are found:

- fix the code or docs
- rerun the affected verification
- update the audit record
- send the revised state back for review

### Step 10: Close only after consensus

A result becomes accepted repo state only after the required consensus rule for
that round is satisfied.

## 2. Required Status Checks

The following status checks are mandatory unless the goal explicitly scopes one
out.

### Code status

- builds successfully on the relevant host(s)
- passes the appropriate test layer
- matches the claimed runtime behavior

### Doc status

- live docs are current
- live docs do not overclaim
- links resolve correctly
- examples match the real API

### Code/doc consistency status

- public docs match the real code path
- performance claims match actual measured reports
- correctness claims match actual parity evidence

### Experiment/report status

- dataset identity is clear
- fairness boundary is explicit
- result tables match the actual run outputs
- non-claims are stated honestly

### Paper/PDF status

- source builds successfully
- layout is readable
- figures/tables correspond to actual repo evidence
- wording matches bounded/accepted claims

## 3. Tolerance For Differences

Not every difference is a failure. The audit must distinguish acceptable drift
from unacceptable drift.

### No tolerance

These differences are not allowed:

- code says one thing, live docs say another
- published result claims parity without parity evidence
- experiment report misstates the tested dataset or host
- paper claims a stronger result than the repo actually supports
- broken links in canonical live docs

### Limited tolerance

These can be accepted if stated explicitly:

- minor wording differences across reviewers
- small formatting differences in reports or slides
- bounded analogue wording instead of paper-identical wording
- minor TeX box warnings when the PDF remains readable
- non-blocking technical debt that is recorded as residual risk

### Historical tolerance

Historical artifacts may differ from the current state if:

- they were correct when written
- they remain archived as immutable history
- live docs do not present them as current truth

### Numerical tolerance

When the audited surface includes numeric parity:

- use the tolerance already defined by the relevant backend/test contract
- never silently widen tolerances just to obtain closure
- any tolerance change must be documented as a real design decision

## 4. AI-Specific Rules

### Codex

Codex is responsible for:

- defining the audit scope
- collecting evidence
- running commands and tests
- implementing fixes
- deciding whether the repo can move forward

Codex owns final repo-state responsibility and must not hide uncertainty behind
other reviewers.

### Gemini

Gemini is used as an independent reviewer focused on:

- correctness of claims
- consistency
- overclaim detection
- report quality
- paper/story quality

Gemini should not be treated as a rubber stamp. Its value is independent
critique.

### Claude

Claude may act as:

- independent reviewer
- external implementer
- manuscript/style reviewer

Any Claude-authored code or artifact must still be reviewed before it is
accepted into the main repo.

### Multi-AI consensus rules

- use the round-specific consensus rule
- when a user requires 3-AI consensus, do not collapse to 2-AI consensus
  without an explicit user override
- when one reviewer is unavailable, record that operational fact explicitly
- consensus does not erase residual risks; it only means the accepted boundary
  is honest enough to proceed

## 5. Audit Responsibility And Cost

Audit is not free. It carries accountability.

If a later issue is found in a surface that was previously accepted, the audit
owners must bear the remediation cost in process terms.

That means:

- reopen the affected goal or create a repair goal
- write the correction report
- rerun the affected validation
- update the live docs if they were wrong
- update the paper/report if the published claim was wrong
- record where the original audit failed

### Responsibility model

- implementation owner pays the first remediation cost for implementation bugs
- audit owner pays the first remediation cost for audit misses
- if a consensus reviewer approved a clearly unsupported claim, that reviewer's
  approval must be recorded as part of the failure chain

This is not a financial penalty rule. It is an accountability rule:

- the same people who accepted the surface must help repair it when the audit
  was not strong enough

### What “pay cost” means in RTDL

In this repo, “pay cost” means:

- additional debugging time
- additional reruns
- additional review loops
- additional report/doc correction work
- possible downgrade of previously claimed status

## 6. Closure Standard

An audit is complete only if:

1. the scope is explicit
2. the evidence is explicit
3. the required status checks passed
4. differences are classified honestly
5. the required AI consensus is recorded
6. the accepted boundary and residual risks are both written down

## 7. Boundary

This is the live audit policy.

Historical execution details remain in:

- `history/`
- per-goal reports
- accepted consensus memos
