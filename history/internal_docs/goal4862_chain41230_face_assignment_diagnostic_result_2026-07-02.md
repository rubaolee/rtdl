# Goal4862 Result: Chain 41230 Face Assignment Diagnostic

Date: 2026-07-02

## Verdict

Goal4862 localized the Section 5.7 County x Zipcode first difference.

The mismatch is **not** a final dynamic face-id renumbering-only difference.
It is a **midpoint / other-map face-selection mismatch** inside output-chain
assembly.

## Evidence

Probe script:

- `history/internal_docs/goal4862_chain41230_face_assignment_probe.py`

Evidence file:

- `history/internal_docs/goal4862_chain41230_face_assignment_probe_summary.json`

The probe reran the bounded helper path, monkeypatched only the in-process
output-chain assembly function, and stopped at chain `41230`.

Runtime:

- `479.299129486084` seconds.

This high runtime confirms that the present debugging path still pays for full
CDB packing / LSI / PIP precomputation before a localized output-chain probe can
run.  That is a debugging-efficiency problem, but not a correctness conclusion.

## First Difference

AuthorPatch:

```text
41230 2 42104 42105 280 290
```

RTDL fallback helper:

```text
41230 2 42104 42105 294 295
```

The chain id, point ids, and length match.  Only the final face ids differ.

## Reverse Mapping

The probe recorded the dynamic final face-id mapping:

| final id | raw key | first seen chain |
| ---: | --- | ---: |
| 280 | `(5, 10950)` | 37849 |
| 290 | `(22, 10950)` | 37963 |
| 294 | `(5, 10938)` | 39105 |
| 295 | `(22, 10938)` | 39105 |

The author expects final ids `280/290`, which correspond in RTDL's dynamic map
to raw keys:

- `(5, 10950)`;
- `(22, 10950)`.

RTDL generated final ids `294/295`, corresponding to raw keys:

- `(5, 10938)`;
- `(22, 10938)`.

Therefore this is not merely a final numbering offset.  The underlying
`other_map_polygon_id` differs.

## Local Context

The immediately preceding chains match:

| chain | author | RTDL | raw key |
| ---: | --- | --- | --- |
| 41226 | `280 290` | `280 290` | `(5,10950)/(22,10950)` |
| 41227 | `280 290` | `280 290` | `(5,10950)/(22,10950)` |
| 41228 | `280 290` | `280 290` | `(5,10950)/(22,10950)` |
| 41229 | `280 290` | `280 290` | `(5,10950)/(22,10950)` |
| 41230 | `280 290` | `294 295` | `(5,10938)/(22,10938)` |

Target chain metadata:

```json
{
  "map_index": 0,
  "dataset_chain_index": 43212,
  "edge_id": 43212,
  "flush_kind": "between_adjacent_intersections",
  "local_point_index": 0,
  "xsect_count_on_edge": 2,
  "xsect_eid0": 43212,
  "xsect_eid1": 8522815,
  "next_xsect_eid0": 43212,
  "next_xsect_eid1": 8522816,
  "xsect_index": 0
}
```

This says the mismatch occurs on a span between two adjacent intersections on
map0 edge `43212`, not on a normal unsplit chain tail.

## Classification

This result narrows the bug:

- **not LSI row materialization**:
  - target chain and point ids exist and align;
  - Goal4860 already proved LSI row count equality.
- **not ordinary vertex PIP Section 5.3**:
  - Goal4861 showed County x Zipcode vertex PIP count/hash consistency.
- **not dynamic face-id renumbering only**:
  - the raw underlying other-map face differs: `10950` expected vs `10938`
    generated.
- **current best classification**:
  - Section 5.7 midpoint point-location / midpoint face-selection mismatch.

## Next Goal

Recommended next goal:

- **Goal4863: chain 41230 midpoint point-location contract probe and repair**

The goal should:

1. extract the exact two adjacent intersections around map0 edge `43212`;
2. compute the midpoint using the same scaled/rational rule as the author;
3. query the opposite map through RTDL point-location;
4. compare the selected face against the author-implied expected face `10950`;
5. if the mismatch is confirmed, repair the generic directed point-location /
   midpoint contract, not a RayJoin-only output shortcut;
6. add a small synthetic regression test for the midpoint face-selection case;
7. rerun the chain 41230 probe before any full Section 5.7 rerun.

No Section 5.7 correctness or performance claim is authorized by Goal4862.
