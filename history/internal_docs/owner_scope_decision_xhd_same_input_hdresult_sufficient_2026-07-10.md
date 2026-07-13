# Owner Scope Decision - X-HD Same-Input HDResult Is Sufficient

Date: 2026-07-10

## Decision

The owner accepts the following X-HD reproduction scope as sufficient:

```text
For the same input files, RTDL/Python/partner and the author's original
C++/CUDA/OptiX hd_exec produce the same directed HDResult within the accepted
tolerance.
```

This replaces the previous hard requirement that the project must recover the
exact original paper input artifacts before the X-HD line can be considered
useful or closable.

## Meaning

The project no longer treats missing original paper artifacts as a blocker for
the current X-HD reproduction line, provided the claim is stated as same-input
HDResult reproduction.

The accepted core claim is:

```text
same input -> same directed HDResult
```

The accepted evidence already includes bounded fixtures, directed/asymmetric
definition gates, public graphics Level-B candidates, and bounded geo WKT
fixtures where author `hd_exec` and RTDL routes are run on the same inputs and
the scalar HDResult matches within the selected tolerance.

## Still Not Claimed

This decision does not authorize:

```text
exact original paper artifact recovery;
byte-identical paper input identity;
Figure 5 / 7 / 8 / 9 / 10 / 11 reproduction;
author-vs-RTDL speedup ratio without denominator alignment;
author internal worklist / -lb / row-hash parity;
RTDL implementation equivalence to the author's internal RT-core algorithm;
claiming that public reconstructed inputs are the original paper inputs.
```

## Consequence

The next useful work is not another public artifact probe or POD route tuning
from the old exact-artifact blocker.

The next useful work is a scoped closeout packet:

```text
close the X-HD line as same-input directed-Hausdorff scalar-output
reproduction, with explicit boundaries and a performance appendix that reports
only aligned same-input timings / regimes.
```

## Required Wording

Allowed:

```text
X-HD same-input HDResult reproduction is sufficient for the current project
scope.  RTDL and author hd_exec agree on directed HDResult for the tested same
inputs within tolerance.
```

Forbidden:

```text
full paper artifact reproduction is complete;
the original paper datasets were recovered;
all paper figures are reproduced;
RTDL matches author internal implementation artifacts;
RTDL performance parity or speedup is proven.
```
