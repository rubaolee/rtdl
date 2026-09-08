# Expected results

The verifier must reconstruct exactly:

- 240 distinct workers;
- 80 valid three-arm cells;
- 1,248 retained timed samples and 120 warmups;
- zero retries, discards, timeouts, output mismatches, or affinity mismatches;
- ten valid complete/prepared evaluations;
- ten engineering-envelope passes at paired median at most 1.20 and every
  paired block at most 1.35.

The largest paired median is about 1.099512 for com-dblp prepared, and the
largest block is about 1.243333 for LibRTS range prepared. The cit-Patents/4M
prepared row is about 1.057361, with about 9.348 seconds for RTDL and 8.802
seconds for public PyOptiX.
