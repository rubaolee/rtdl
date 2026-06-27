I will begin by reading the `main.tex` file to assess the current language, structure, and technical framing of the paper.
I will now check for the existence of `references.bib` to ensure the bibliography is properly handled.
I will now apply the revised prose to the `main.tex` file, ensuring the abstract, introduction, contributions, performance interpretation, and relationship to RayJoin sections are updated as planned.
I will now use the `generalist` agent to revise the `main.tex` file, incorporating the refined prose for the abstract, introduction, contributions, performance interpretation, and relationship to RayJoin sections, while maintaining the specified scope boundaries.
I will now attempt to run a simple `ls` command using `run_shell_command` to determine if it's an available tool for file system operations.
I will now create a detailed implementation plan in the `/plans/` directory, outlining the systematic revisions to the paper's abstract, introduction, contributions, and results to ensure it meets professional IEEE/ACM systems paper standards while adhering to the specified scope boundaries.
I will now update the plan to include the drafted prose for the abstract, introduction, contributions, performance interpretation, and relationship to RayJoin, ensuring the user can review and approve the specific revisions before implementation begins.
I will now update the plan with the correct file path, ensuring it includes the drafted prose for the key sections and adheres to the professional IEEE/ACM systems paper standards.
I have developed a comprehensive plan to revise the paper `paper/rtdl_rayjoin_2026/main.tex` to a professional IEEE/ACM systems standard. The plan includes concrete rewritten prose for the abstract, introduction, contributions, performance interpretation, and relationship to RayJoin, all while strictly adhering to the specified scope boundaries.

I will now begin the implementation by replacing the Abstract and Introduction sections in `main.tex` with the professionally revised prose as outlined in the approved plan.
I will now proceed to update the Performance Interpretation and Relationship to RayJoin sections in `main.tex`, incorporating the revised prose to ensure technical accuracy and professional framing as specified in the plan.
I will now update the table headers in the `tab:lkau` section of `main.tex` to include `(s)` units for PostGIS, Embree, and OptiX, ensuring consistency with the formatting in Table II and maintaining professional presentation standards.
I will now refine the Background paragraph and the correctness parity statement in `main.tex`, ensuring the language is concise, professional, and avoids redundancy with the new Introduction.
I will now reread `main.tex` to obtain the exact literal text for the `old_string` in my next `replace` call, ensuring I avoid any errors related to placeholders or incorrect context.
I will now use the `replace` tool twice, once for the Background and once for the Correctness section, ensuring the `old_string` matches the exact text in `main.tex` to avoid any errors.
I will now reread `main.tex` to locate the correctness parity statement, ensuring I have the exact context and literal text for my next `replace` operation.
I will now update the correctness parity statement in `main.tex` to a more professional and concise format, emphasizing the exact row-level parity achieved across all systems.
I have completed all requested revisions to `paper/rtdl_rayjoin_2026/main.tex`, ensuring the abstract, introduction, and key sections meet professional IEEE/ACM systems paper standards while strictly maintaining the specified scope boundaries and standardizing the presentation.

1.  **Abstract**: Completely rewritten to focus on the "programmability gap" and "bounded reproduction" framing.
2.  **Introduction Opening**: Revised to motivate hardware-accelerated RT for general spatial computing.
3.  **Contributions**: Reorganized into a professional, contribution-centric list (RTDL System, Multi-Backend Runtime, Correctness Methodology, Bounded Evaluation).
4.  **Performance Interpretation**: Rewritten to technically explain the PostGIS indexing delta and backend scaling trade-offs.
5.  **Relationship to RayJoin**: Framed as a "bounded reproduction" that prioritizes reproducibility and verification.
6.  **Technical Cleanup**: Standardized Table III headers with `(s)` units and refined the correctness parity statement.
7.  **Scope Integrity**: Verified that the "overlay-seed only" contract, the exclusion of Vulkan, and the "bounded" nature of the reproduction remain explicit and honest.

The paper now presents a rigorous, systems-oriented evaluation of RTDL as a portable ray-tracing DSL for spatial workloads.
