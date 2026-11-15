# DQR-Happy

Personal research and engineering website: **[dengqirui.me](https://dengqirui.me/)**.

A bilingual, accessible, dependency-free static site published with GitHub Pages.

English is served by default at `/`; Chinese is available at `/zh/`. The language switch preserves the page. Previously published `/en/` URLs redirect to their English root equivalents.

## Develop

Python 3.9+; no installation step. Serve this repository, not its parent folder.

```bash
python3 scripts/build.py
python3 scripts/check_site.py
python3 -m http.server 18765 --bind 127.0.0.1
```

Open `http://127.0.0.1:18765/`.

## Update content

| File | Purpose |
| --- | --- |
| `content/profile.json` | Public contact, publication, curated projects |
| `content/notes.json` | Note metadata and short bilingual notes |
| `content/articles/*.en.md` | Long-form English notes; Chinese pages link to the full English article |
| `scripts/build.py` | Shared templates, research table, education and biography |
| `assets/site.css` | Responsive layout, theme tokens, print styles |
| `assets/site.js` | Theme, menu, filtering and print actions |
| `docs/CONTENT_SOURCES.md` | Content provenance and claim boundaries |
| `docs/DESIGN.md` | Design and behavior contract |

Long-form Markdown supports level-two headings, paragraphs, inline code, HTTPS links, and fenced code blocks. Rebuild after editing and commit sources together with generated pages. Reported results must retain their conditions and source links.

## Publish

GitHub Pages serves `main:/`. Preserve `CNAME` (`dengqirui.me`) and `.nojekyll`. Verify the Pages build and HTTPS after pushing. ERETrace remains a separate project site at `/ERETrace/`.

No visitor analytics or external fonts. Public identity/contact were approved by the owner. Personal content remains with its author; linked projects retain their own licenses. No third-party code or visual assets are bundled.
