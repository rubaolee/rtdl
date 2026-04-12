### Verdict

Goal 262 represents a technically sound, honest, and mature design decision. By introducing a new explicit predicate rather than mutating the existing ones, the plan correctly balances the need for backward compatibility with the strict requirements of a paper-faithful RTNN reproduction for `v0.5`. 

### Findings

* **Technical Honesty:** The design is highly honest. It explicitly identifies the semantic gap between the current `v0.4.0` features (`fixed_radius_neighbors` lacking rank, and `knn_rows` lacking a radius bound) and the specific 3D RTNN paper requirements. It avoids retroactively changing the definitions of already-shipped features.
* **Preservation of `knn_rows(k=...)`:** Adding `bounded_knn_rows(radius, k_max)` is the optimal way to preserve the released `knn_rows` surface. As seen in `goal203_knn_rows_dsl_surface_2026-04-10.md` and `src/rtdsl/api.py`, `knn_rows` is an established DSL contract. Modifying it to require a radius would introduce silent semantic drift and breaking changes for users relying on pure, unbounded K-nearest neighbor searches.
* **Paper-Consistent Design:** The introduction of `bounded_knn_rows(radius: float, k_max: int)` accurately models the RTNN paper's constraints. It explicitly demands both a spatial boundary (`radius`) and a neighbor count limit (`k_max`), while guaranteeing a ranked output (`neighbor_rank`). 
* **Setup for Implementation:** The contract is unambiguous. It clearly specifies the required output fields (`query_id`, `neighbor_id`, `distance`, `neighbor_rank`) and the exact grouping and sorting rules (ascending `query_id`, then ascending `neighbor_rank`). This leaves no ambiguity for the downstream lowering, reference path, and native backend implementation goals.

### Risks

* **API Surface Expansion:** Introducing a third distinct neighbor-search predicate (`fixed_radius_neighbors`, `knn_rows`, `bounded_knn_rows`) slightly increases the cognitive load for end-users. The documentation will need to be very clear about when to use which predicate to prevent confusion.
* **Backend Divergence:** The new precise ordering requirements (ascending `distance`, then `neighbor_id` for rank tie-breaking) will place a strict sorting burden on the hardware-accelerated backends (OptiX, Vulkan). Ensuring these backends perform this bounded, ranked sort efficiently without diverging from the CPU oracle's results will be a critical hurdle in later implementation goals.

### Conclusion

Goal 262 is a strong, well-reasoned design slice. It successfully charts a path for `v0.5` to achieve true RTNN paper consistency while keeping the `v0.4.0` legacy intact. The new `bounded_knn_rows` contract is thoroughly defined and ready to serve as a solid foundation for the upcoming API, lowering, and backend execution goals.
