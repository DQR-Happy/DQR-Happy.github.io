# Design and maintenance contract

Purpose: let collaborators and engineering teams understand Qirui Deng's background, inspect a research contribution, and reach public implementations or contact information.

Routes: Chinese root and English `/en/`; both have home, research, projects, notes, about, and three technical articles. Language switching preserves the current page. A 404 page provides recovery.

Visual language: paper white / graphite with forest-green accents, editorial serif Latin display type, and system Chinese/body fonts. Hierarchy comes from borders, alignment, spacing, and relevant diagrams. The encoding figure is explicitly schematic. Performance values have context and source links.

Interactions: native navigation, mobile menu with Escape, system-aware persisted theme, project categories/search with URL state and an empty-result reset, citation copy with failure guidance, and a printable profile. Content remains available without JavaScript.

Implementation: Python standard-library generator, CSS, and vanilla JavaScript. No npm dependencies, external font services, analytics, or backend. GitHub Pages serves committed HTML from `main:/`. Edit content/templates/assets and rebuild rather than editing generated HTML.

Review: desktop 1440×900, mobile 390×844, light/dark, navigation, language symmetry, project filters and reset, citation copy, profile print, link integrity, overflow, deterministic build, CNAME preservation, and ERETrace URL regression. Record observed verification separately from source review.
