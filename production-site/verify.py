"""Verify the generated multi-page website before a release (standard library only)."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent / 'dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
pages = {}
for file in ROOT.rglob('*.html'):
    page = Page(); page.feed(file.read_text()); pages[file.resolve()] = page
    assert sum(tag == 'h1' for tag, _ in page.tags) == 1, file
assert len(pages) == 20, 'Expected 17 content pages, 2 utility pages and a 404 page'
for file, page in pages.items():
    for tag, attrs in page.tags:
        key = 'href' if tag in ('a', 'link') else 'src' if tag in ('img', 'script') else None
        if not key: continue
        url = urlsplit(attrs.get(key, ''))
        if url.scheme or url.netloc: continue
        target = ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else file.parent / unquote(url.path) if url.path else file
        if url.path.endswith('/'): target = target / 'index.html'
        target = target.resolve()
        assert target.exists(), (file, attrs)
        if url.fragment and target in pages:
            assert any(a.get('id') == url.fragment for _, a in pages[target].tags), (file, attrs)
contact = pages[(ROOT / 'contact/index.html').resolve()]
required = {a.get('name') for t, a in contact.tags if t in ('input', 'textarea', 'select') and 'required' in a}
assert required == {'name', 'email', 'message', 'consent'}, required
assert any(t == 'details' and a.get('id') == 'project-details' for t, a in contact.tags)
assert any(t == 'form' and a.get('data-live') == 'true' and a.get('action') == 'https://formsubmit.co/wellnesswithsandip@gmail.com' for t, a in contact.tags)
urls = [e.text for e in ET.parse(ROOT / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls) == 17 and len(set(urls)) == 17
for url in urls:
    assert url.startswith('https://www.dipatmawellness.com/')
    assert urlsplit(url).path not in ('/privacy/', '/thank-you/')
    page = pages[(ROOT / urlsplit(url).path.lstrip('/') / 'index.html').resolve()]
    assert any(t == 'link' and a.get('rel') == 'canonical' and a.get('href') == url for t, a in page.tags), url
    assert any(t == 'meta' and a.get('name') == 'robots' and a.get('content') == 'index,follow' for t, a in page.tags), url
print('PASS: 20 pages; internal links, fragments and assets; 17 canonical sitemap entries; simplified live enquiry form')
