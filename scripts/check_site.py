#!/usr/bin/env python3
"""Validate generated routes, fragments, document structure and deployment contract."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.headings, self.errors = set(), [], [], []
        self.description = False
        self.canonical = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('duplicate ID: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.headings.append(tag)
        if tag == 'meta' and attrs.get('name') == 'description':
            self.description = bool(attrs.get('content'))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = True
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'a' and attrs.get('href') in ('', '#'):
            self.errors.append('empty link')


def main():
    errors = []
    pages = {path: Page(path.read_text()) for path in ROOT.rglob('*.html')}
    external = set()
    for path, page in pages.items():
        if len(page.headings) != 1 or not page.description or not page.canonical:
            errors.append(f'{path.relative_to(ROOT)}: missing h1/description/canonical')
        errors.extend(f'{path.relative_to(ROOT)}: {error}' for error in page.errors)
        for href in page.links:
            parsed = urlsplit(href)
            if parsed.scheme in ('mailto', 'tel'):
                continue
            if parsed.netloc and parsed.netloc != 'dengqirui.me':
                external.add(href)
                continue
            if parsed.path.startswith('/ERETrace/'):
                external.add(href)
                continue
            base = ROOT if parsed.path.startswith('/') else path.parent
            target = base / unquote(parsed.path).lstrip('/') if parsed.path else path
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{path.relative_to(ROOT)}: missing target {href}')
            elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{path.relative_to(ROOT)}: missing fragment {href}')
    if (ROOT / 'CNAME').read_text() != 'dengqirui.me\n':
        errors.append('CNAME changed')
    if not (ROOT / '.nojekyll').is_file():
        errors.append('.nojekyll missing')
    if len(pages) != 17:
        errors.append(f'Expected 16 content pages + 404, got {len(pages)}')
    for path in pages:
        if path.name != '404.html' and 'en' not in path.relative_to(ROOT).parts:
            if ROOT / 'en' / path.relative_to(ROOT) not in pages:
                errors.append(f'English counterpart missing for {path}')
    for filename in ('profile.json', 'notes.json'):
        json.loads((ROOT / 'content' / filename).read_text())
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(pages)} HTML pages, internal links/fragments, language counterparts, metadata, CNAME and Pages configuration.')
    print(f'{len(external)} distinct external links for deployment review.')


if __name__ == '__main__':
    main()
