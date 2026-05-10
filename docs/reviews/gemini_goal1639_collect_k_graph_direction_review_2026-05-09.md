Based on the recent diagnostic evidence in **Goal 1637** and **Goal 1638**, here is the engineering verdict:

**CUDA Graph Replay Direction**
You should **avoid** reviving the old per-level CUDA graph replay path. Goal 1638 demonstrated that the old compact-level graph replay only provides a marginal benefit at bounded diagnostic scales and cannot cover the required final-pair target scale (`segment_capacity=131072`). You should only pursue a production-relevant, prepared end-to-end stable-topology graph for the real final-pair scale rather than a blind re-enablement of the old path.

**Next Safest Probe**
Goal 1637 revealed that the final-pair mark kernel execution time itself is tiny, and the dominant cost is the host-visible wait around stream dependencies and dispatch accounting. 

The next safest probe should avoid blind kernel optimization and instead **restructure the stream-dependency structure** for the final `merge -> mark -> prefix -> compact` chain to reduce the host-observed stream wait. Alternatively, you can measure a prepared end-to-end stable-topology graph for the final-pair scale.
