# Proposal: RTDL Front Page Refresh (Goal 255)

Date: 2026-04-11
Author: Gemini CLI

## Diagnosis

The current `README.md` is a high-integrity "project log" that has evolved through several major milestones (v0.1 through v0.4). While it is technically exhaustive and honest, it suffers from several issues for a new user:

1.  **Historical Density:** The "Trust Anchor" (v0.1) and version-layering explanations dominate the first-screen real estate. A new user needs to know what the tool *is* before they care about its 2024 lineage.
2.  **Defensive Positioning:** The visual demo is introduced with a bold "**not**" (not a graphics engine), which creates a slightly negative first impression. The demo should be a "proof of versatility" rather than a disclaimer.
3.  **Terminology Overload:** Phrases like "row-oriented geometric-query work," "exact-source county_zipcode," and "pathology/unit-cell contract" are scattered throughout without immediate context.
4.  **Buried Action:** The "Start Fast" section is 50% down the page, preceded by complex installation notes and version identity facts.

## Proposed Structure

The new front page should follow a "Layered Disclosure" pattern:

1.  **Hero Section:**
    *   **Headline:** RTDL: Ray Tracing for Spatial Data.
    *   **Sub-headline:** A high-performance research runtime that uses ray-tracing traversal machinery for non-graphical geometric queries.
    *   **Visual Proof:** A high-quality thumbnail/link to the Visual Demo Video, framed as "RTDL in action: A Python application powered by the RTDL query core."

2.  **At a Glance (What is RTDL?):**
    *   Three columns/bullets:
        *   **Standard Workloads:** Out-of-the-box spatial joins, hit counting, and nearest-neighbor search.
        *   **Programmable DSL:** Write custom geometric kernels in Python that compile to native hardware.
        *   **Multi-Backend:** Run the same code on CPU (Embree), NVIDIA GPU (OptiX), or portable GPU (Vulkan).

3.  **Quick Start (The 30-Second Path):**
    *   Minimalist installation (`pip install -r requirements.txt`).
    *   Single "Hello World" command.
    *   Clear pointer to the **Quick Tutorial**.

4.  **The Workload Surface (The "What"):**
    *   Simplified table of supported query types (Point-in-Polygon, Jaccard, KNN, etc.).
    *   Direct links to the corresponding examples.

5.  **The Engineering Story (The "How"):**
    *   Brief explanation of the core idea: "Traverse once, Refine exactly."
    *   The backend matrix (Embree, OptiX, Vulkan, Oracle).

6.  **Research Foundations (The "Why"):**
    *   The RayJoin lineage (ICS 2024).
    *   Condensed bibliography (chronological list of papers).
    *   The "Trust Anchor" concept mentioned here as a link to v0.1 for researchers.

7.  **Documentation Hub:**
    *   Categorized links (Tutorials, User Guide, Release Reports, Architecture).

## Style Notes

*   **Action-Oriented:** Use verbs like "Execute," "Author," "Validate."
*   **Visual Hierarchy:** Use H2/H3 tags and horizontal rules to break up the dense text.
*   **Integrated Demo:** Instead of saying RTDL is "not a renderer," say "RTDL powers spatial queries. While not a graphics engine, its performance allows for real-time applications like this 3D demo."
*   **Consistent Naming:** Standardize on "RTDL" (the runtime) and "rtdsl" (the Python package) with a single, clear callout for the `PYTHONPATH` requirement.

## Risks

*   **Diluting Rigor:** Moving the v0.1 "Trust Anchor" details to the bottom might be seen as de-emphasizing the academic reproducibility that is central to the project.
*   **Version Confusion:** v0.2, v0.3, and v0.4 are all "live" in different ways. The proposal must clarify that `main` is v0.4 without making the user feel they are missing v0.2.
*   **Backend Expectations:** Highlighting "Multi-Backend" might lead users to expect identical performance across all three, which is not the case (e.g., Vulkan is slower).

## Recommendation

I recommend a complete rewrite of `README.md` following the "Proposed Structure" above. The current content of `README.md` is valuable as a "Project Status and History" document; I suggest moving the historical/version-specific "Trust Anchor" narrative to a new file (e.g., `docs/project_evolution.md`) or a dedicated "Status" section at the very bottom of the new README.

The goal is to move from **"Here is how this project was built"** to **"Here is what this project can do for you."**
