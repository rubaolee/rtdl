# Prepared-batch successor diagnostic

This is an unregistered exploratory successor at exact commit
`63a6cc6abcbe0074ce735a400f68dd7563caa36a`, tree
`97aba41b6b99a686215ba80b0ac537b6a24d22fb`. It ran on the same RTX 4000 Ada
and exact input/native identities recorded by the preceding `e63773191`
diagnostic. It must not be pooled with that diagnostic or a later formal run.

The source-authored RTDL arm used the new public owner-bound immutable prepared
query batch and the opaque compact-receipt validation path. Both arms retained
two warmups and 20 timed calls. They produced the same complete 5,000-by-3 U32
output digest. RTDL's median was 433,299 ns; PyOptiX's median was 346,236 ns;
their unregistered ratio was `1.2514556545246596`. The engineering target was
not met, so this is preserved as an adverse result.

The worker still expanded last-execution evidence inside each timed callable.
That conflicts with the established timer-free detailed-evidence convention.
A successor moves evidence serialization outside both arm timers while keeping
execution, synchronization, status checks, complete output return, and oracle
comparison inside. This protocol repair requires a new source identity and
fresh samples; this result is not relabeled.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `RTDL_DIAGNOSTIC.json` | 1,887 | `c03e44f4e0044d6ccff063ed23ad7c5091078212349213634c9588ecc028b1fb` |
| `PYOPTIX_DIAGNOSTIC.json` | 2,158 | `ccb6be48d3286a6bbd73330621613cd11f99c101db692fa17a433c4101e8217f` |
| `TESTS.log` | 124 | `934b6021db4632ebaedbb7c7bb421d3cddb4546b7cc4d9d1a17680f079723ef9` |
