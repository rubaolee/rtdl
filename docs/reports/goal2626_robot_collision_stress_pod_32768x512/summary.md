# Goal2626 Robot Collision Stress

- Scenario: 32768 poses, 512 obstacles, 2 links, repeats=3 warmup=1
- Embree steady-state median: 0.0568973 sec
- OptiX steady-state median: 0.00643277 sec
- OptiX speedup vs Embree: 8.84x
- Embree traversal median: 0.0199478 sec
- OptiX traversal median: 0.000260056 sec
- Embree prepared-query build phase: 2.37448 sec
- OptiX prepared-query build phase: 2.55474 sec

Interpretation: this is a reusable prepared-query backend timing. The app still performs a CPU probe-reference oracle before timing, so process wall time is not a clean RT backend metric at this stress scale.
