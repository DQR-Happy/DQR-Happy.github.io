# Design and maintenance contract

Purpose: let collaborators and engineering teams understand DQR-Happy's background, inspect a research contribution, and reach public implementations or contact information.

Routes: Chinese root and English `/en/`; both have home, research, projects, notes, about, and three technical articles. Language switching preserves the current page. A 404 page provides recovery.

Visual language: pearl white / graphite with muted slate-blue, lilac-gray, and dusty-rose accents, editorial serif Latin display type, and system Chinese/body fonts. Hierarchy comes from borders, alignment, spacing, and relevant diagrams. The encoding figure is explicitly schematic. Performance values have context and source links.

Interactions: native navigation, mobile menu with Escape, system-aware persisted theme, project categories/search with URL state and an empty-result reset, a printable profile. Content remains available without JavaScript.

Implementation: Python standard-library generator, CSS, and vanilla JavaScript. No npm dependencies, external font services, analytics, or backend. GitHub Pages serves committed HTML from `main:/`. Edit content/templates/assets and rebuild rather than editing generated HTML.

Review: desktop 1440×900, mobile 390×844, light/dark, navigation, language symmetry, project filters and reset, profile print, link integrity, overflow, deterministic build, CNAME preservation, and ERETrace URL regression. Record observed verification separately from source review.

## Palette revision — 2026-11-15

The owner rejected the original green palette. This revision draws from these ColorKit palettes:

- [Muted blue / lilac](https://colorkit.co/palette/69779b-9692af-acdbdf-d7eaea/): use the blue/lilac relationship, excluding the cyan colors.
- [Muted rose / cool gray](https://colorkit.co/palette/e4babe-fcf1ef-e8d8c9-ced3d7-5e606c/): dusty rose and gray as supporting tones.

Role mapping: pearl background `#F6F5F8`, graphite body `#30313D`, slate controls `#5C6888` (darkened for contrast), lilac surface `#ECE8F0`, deep plum-gray feature panel `#3D394B`, blue/rose highlights `#BFC7DF` / `#E4BABE`. Dark mode uses graphite `#1D1E27` with pale slate/lilac accents. Color roles live in CSS variables, including feature-panel borders and SVG fills; no green accent remains. The light-mode primary button uses white text on slate (5.54:1); secondary body text on pearl is 5.46:1. Decorative colors are not used as low-contrast body text.
