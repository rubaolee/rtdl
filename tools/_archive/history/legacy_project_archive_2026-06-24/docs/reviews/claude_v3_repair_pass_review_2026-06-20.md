# Claude V3 Repair Pass Review

Date: 2026-06-20.

Reviewer: Claude Code, compact no-tools review packet.

Review packet:

```text
docs/reviews/v3_repair_pass_compact_review_packet_2026-06-20.md
```

## Verdict

```text
accept-with-P0
```

Claude accepts the Repair Pass 1 evidence as real and internally consistent,
but does not authorize public release.

## Findings

### P0: External review must be recorded and acted on

This review is the missing external-review gate. It must be recorded, and the
P0 findings must be addressed before release.

### P0: Public docs are not fully rebuilt

The rebuild tutorial path and evidence docs exist, but the full public doc set
is not yet a finished release surface.

### P0: Release wording gate is missing

The current tests block obvious overclaims, but there is not yet a dedicated
release wording gate for public docs. Public claim flags remain false.

### P0: Setup/install path is not packaged

The runbook and GPU environment gate are reproducible, but they are not yet a
polished install path for users.

### P0: Second-machine confirmation is not done

Repair Pass 1 evidence is single-pod evidence. A second compatible Linux GPU
confirmation remains required or must be explicitly waived with rationale.

### High: Two negative or mixed rows must stay prominent

Two rows prevent broad OptiX speedup wording:

- `librts_spatial_index`: OptiX speedup vs Embree is `0.065x`.
- standard all-workload `spatial_rayjoin`: OptiX speedup vs Embree is `0.034x`.

Any public speedup story must either explain these rows prominently or scope
claims away from them.

### High: Broad V3-over-V2.14 speed is not proven

The strongest supported V3-over-V2.14 claim is route health and runability,
especially triangle-counting OptiX rows that fail in v2.14 and pass in current
V3. Broad speed superiority over V2.14 is not supported.

### Medium: App classification wording is unresolved

The non-uniform classifications are appropriate, but each classification needs
public wording that survives a wording gate.

### Low: RayDB and RTNN need careful language

RayDB is dependency-gated. RTNN is mixed. Neither should ship with broad,
unqualified claims.

## Final Release Authorization Answer

```text
release_authorized: false
```

Repair Pass 1 is accepted as valid evidence work. V3 publication remains blocked
until P0 findings are closed.

## Post-Review Action Taken By Codex

After this review, Codex added a first-pass release wording gate:

```text
scripts/v3_release_wording_gate.py
tests/v3_release_wording_gate_test.py
```

Latest local result:

```text
py -3 scripts\v3_release_wording_gate.py --pretty
status: pass
violations: []
```

This reduces, but does not fully close, the release-wording P0. A final release
authorization scanner and full public-doc review are still required before V3
publication.
