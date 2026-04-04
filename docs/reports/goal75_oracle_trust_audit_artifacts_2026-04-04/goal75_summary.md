# Goal 75 Oracle Trust Audit

Host label: `lx1`
Database: `rtdl_postgis`

- Python reference oracle is audited on deterministic mini cases only
- native C oracle is accepted here on deterministic small cases
- native-oracle mini-case agreement is retained only as supporting evidence, not as the accepted trust boundary
- PostGIS is the external truth source for `lsi`, `pip`, and overlay-seed semantics

## Result

- mini Python all-pass: `True`
- small native all-pass: `True`

## Mini Python Envelope

- `lsi` cases: `15` pass `15`
- `pip` cases: `15` full pass `15` positive pass `15`
- overlay cases: `15` pass `15`

## Small Native Envelope

- `lsi` cases: `12` pass `12`
- `pip` cases: `12` full pass `12` positive pass `12`
- overlay cases: `12` pass `12`
