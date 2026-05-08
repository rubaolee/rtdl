# Goal 1522: Targeted Cross-Platform Regression

## Verdict

The targeted v1.5.4 non-pod regression slices are green on both Windows and the
local Linux validation host after the Goal1520/Goal1521 collect and
reduced-copy hardening.

Full Windows unittest discovery was attempted but did not finish inside the
10-minute command timeout, so this report does not claim full-suite discovery
success.

## Windows Result

Embree evidence and collect/reduced-copy hardening slice:

```text
Ran 26 tests in 0.011s
OK
```

App docs, classification, pod-intake, and Embree CPU promotion slice:

```text
Ran 36 tests in 0.010s
OK
```

Full discovery attempt:

```text
Timed out after 604033 ms.
```

## Linux Result

Host: `192.168.1.20`

Embree evidence and collect/reduced-copy hardening slice:

```text
Ran 26 tests in 0.004s
OK
```

App docs, classification, pod-intake, and Embree CPU promotion slice:

```text
Ran 36 tests in 0.003s
OK
```

## Claim Boundary

Goal1522 is targeted local Windows plus Linux regression evidence only. It does
not authorize public speedup wording, broad RTX wording, broad polygon/GIS
wording, whole-app claims, true zero-copy wording, stable `COLLECT_K_BOUNDED`
promotion, full-suite pass claims, or release action.
