# Review of Gemini PostGIS Performance Investigation

Date: `2026-04-04`

Reviewed source:

- Gemini-generated performance investigation on PostGIS vs RTDL timing gaps for
  the accepted bounded packages

## Overall Judgment

Useful and directionally correct.

Keep it as a planning/input document.

## What Gemini Got Right

1. PostGIS is faster largely because it is using:
   - spatial indexes
   - query-planner pruning
   - short-circuit execution
   - in-engine execution with no GPU transfer overhead

2. RTDL is paying for:
   - richer row/result semantics
   - full-matrix behavior in important paths
   - host-side exact finalization
   - backend-agnostic runtime structure

3. The biggest non-apples-to-apples timing gap is PIP, not LSI.

That is the right reading of the accepted bounded results.

## What Should Be Narrowed

Some Gemini recommendations are too aggressive as immediate project actions.

### 1. “Move exact finalization to device”

This is interesting long-term, but it is not the first practical fix.

Why:

- it is a major architecture step
- it would materially change backend contracts
- it is larger than the current project’s immediate performance repair scope

### 2. “Adopt columnar materialization” / Arrow-like redesign

This may be worthwhile later, but it is broader than the next actionable fix.

Immediate value is more likely to come from:

- better workload-aware semantics
- better candidate/refine contracts
- less unnecessary full-matrix work

### 3. “Device-side AABB pruning”

That may help, but it is not the first-order bottleneck relative to current:

- semantics
- materialization
- host exact finalization

## Accepted Action Order

The practical order should be:

1. query-aware fast paths for boolean or positive-hit PIP cases
2. less full-matrix materialization where contracts allow it
3. make GPU candidate output drive exact refine, rather than recomputing broad
   spaces on the host
4. only later consider larger architectural changes such as device-side exact
   finalization or broader runtime representation redesign

## Final Conclusion

The Gemini investigation is worth preserving.

The core diagnosis is strong.

Its solution section should be read as:

- a good long-range direction set

not as:

- an immediate implementation queue in its original order
