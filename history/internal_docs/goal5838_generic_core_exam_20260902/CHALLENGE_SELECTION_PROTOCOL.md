# Goal5838 prospective challenge selection protocol

Date frozen: 2026-09-02

Status: `PRETARGET_PROTOCOL__NO_CHALLENGE_SELECTED`

## Purpose

The Goal5838 generic family core must be frozen before the project learns which
admissible full protocol shape it must execute. The project defines the finite
challenge universe and pass criteria; it does not choose a favorable row.

## Complete table

The generator crosses the four primitive kinds already exercised by V4
provider paths with three declared callback/result topologies. It excludes only
an exact pre-Goal5838 callback topology, never a difficult or inconvenient
row. Every exclusion names its pre-existing source and symbol. Rows are sorted
by `candidate_id` UTF-8 bytes and receive their stable indices mechanically.

Near matches do not trigger exclusion. For example, the curve Boolean path is
closest-hit rather than any-hit terminate; owner-grouped curve output is per
owner rather than per query; bounded relation has custom intersection plus a
different multi-role/result contract. These remain visible distinctions rather
than being relabelled as unseen code.

## Independent entropy

The exact target is the NIST Randomness Beacon 2.0 pulse at
`2026-09-02T19:00:00.000Z` (`1788375600000` milliseconds). The only accepted
target URI is
`https://beacon.nist.gov/beacon/2.0/pulse/time/1788375600000`; a next-closest
timestamp is rejected. The immediately previous exact pulse is also required.

The signing certificate identity is frozen before the target as SHA-512 of its
X.509 DER bytes:
`528943a555f5f8ca54423be6dfb95925a35c7b552046420e7d7cd072058a14d6536ad3a8e9754b6582f164a90b0cd86a65d659f5426a2659a947595d1c816c8c`.
HTTPS retrieval uses platform CA validation. Both adjacent pulse signatures
must verify with the pinned certificate.

The live service's cipher-suite-0 signing serialization is frozen before the
target: four-byte big-endian length prefixes for non-integer fields, u32
`cipherSuite`, `period`, external status and pulse status, and u64 chain/pulse
indices. This is deliberately explicit because the live API's DER certificate
identifier and serialization differ from one interpretation of draft NISTIR
8213. No variant may be selected after observing the target.

Selection entropy is the target pulse's signed 512-bit `localRandomValue`, not
the API's derived `outputValue`. The previous pulse must both link to the
target's predecessor output and contain `SHA512(target.localRandomValue)` as its
precommitment. This makes the selected entropy independently generated,
signed, and committed before disclosure.

## Mapping

The mapping hashes a domain separator followed by eight-byte-length-framed
ASCII fields: challenge-table seal, generic-core seal, exact target timestamp,
exact target URI, target local random value, and counter. SHA-256 outputs at or
above `2^256 - (2^256 mod N)` are rejected; the first accepted value selects
`value mod N`. This avoids modulo bias and binds selection to this exact core
and table.

## Failure handling and claim boundary

The target is never replaced. Temporary HTTP, certificate, or tooling failure
leaves selection `PENDING`; it is not scientific failure and does not authorize
an alternate pulse or author-selected row. Ordinary post-selection defects in
the provider, app, oracle, runner, or environment must be repaired through the
allowed extension layers. Scientific failure retains the exact five-part test
in the Goal5838 preregistration, including a minimal witness that a semantic
core byte change is necessary.

Selection alone is not a successful exam. Success additionally requires the
selected protocol to pass schema/IR/provider admission, the public lifecycle,
an independent CPU oracle, hostile tests, and true-GPU execution with zero
change to every frozen-core byte.
