import base64, gzip, pathlib
root=pathlib.Path(__file__).parent
out=root/'dist'
out.mkdir(exist_ok=True)
html=gzip.decompress(base64.b64decode((root/'index.html.gz.b64').read_text())).decode('utf-8')
# Replace emoji-rendered external-link arrows with a crisp, accessible inline icon.
icon='<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block;vertical-align:-0.16em;margin-left:0.2em"><path d="M7 17 17 7M8 7h9v9"/></svg>'
html=html.replace('↗',icon)
(out/'index.html').write_text(html,encoding='utf-8')
(out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.fullchoicebreath.com/sitemap.xml\n')
paths=['/','/about/','/approach/','/solutions/','/impact-advisory/','/insights/','/contact/','/privacy/']
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>https://www.fullchoicebreath.com{p}</loc></url>\n' for p in paths)+'</urlset>\n'
(out/'sitemap.xml').write_text(xml)
