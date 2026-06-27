## Goal 28A Re-Review

### Findings Ordered by Severity

**[Medium] Staged ArcGIS item files are suspiciously small (1146 bytes each)**
All four ArcGIS item pages (`uscounty_item.html`, `zipcode_item.html`, `blockgroup_item.html`, `waterbodies_item.html`) staged at exactly 1146 bytes. ArcGIS public item pages are substantially larger than that — 1146 bytes is consistent with a redirect, a login wall, or a minimal error response, not actual item metadata. The report treats these as successfully staged "source documentation," but the content was not verified. This overstates the staging result. It does not break the feasibility conclusions, but "public raw-source pages are reachable" should be "public raw-source URLs return HTTP 200 with unverified content."

**[Minor] Dryad 404 not assessed for transient vs. permanent**
The report records the 404 as a current blocking fact but does not distinguish "temporarily unavailable" from "share was removed or URL rotated." If transient, the exact-input strategy is not actually blocked — it is merely paused. The report should at minimum state whether the URL was previously confirmed working or is being probed for the first time.

**[Minor] No dataset size estimates for the designated first-target family**
`County ⊲⊳ Zipcode` is called the "best first target" and judged feasible for a 15 GiB host, but no size estimate for the converted CDB/input pair is given. The policy of keeping 4 GiB free headroom is stated, but without a baseline memory-usage measurement for the idle host, the effective experiment budget is unanchored. This is acceptable at the feasibility stage as long as Goal 28B includes a pilot-size measurement before a full run.

**[Minor] Continent-scale families are all classified identically without differentiation**
Africa, Asia, Australia, Europe, North America, South America are all `not yet feasible to promise` for the same stated reason. North America is noted as especially high risk in one cell but the classification rows are otherwise uniform. A brief size-order ranking (even qualitative: "SA/Australia likely smallest, NA likely largest") would strengthen the triage.

---

### Acceptable As-Is

Yes. The medium finding (staging content unverified) is a documentation overstatement, not a false conclusion — the feasibility judgment does not depend on what the staged HTML files contain. The Dryad 404 is the real structural finding and is stated clearly. The closure condition asks for a report that says which paper-scale or exact-input cases are truly runnable; the report does say this: exact-input universally blocked, County/Zipcode as the viable near-exact-input first target, continent-scale not yet honest to promise.

---

APPROVED
