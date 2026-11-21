import base64, gzip, pathlib
root=pathlib.Path(__file__).parent
out=root/'dist'
out.mkdir(exist_ok=True)
(out/'index.html').write_bytes(gzip.decompress(base64.b64decode((root/'index.html.gz.b64').read_text())))
(out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.fullchoicebreath.com/sitemap.xml\n')
paths=['/','/about/','/approach/','/solutions/','/impact-advisory/','/insights/','/contact/','/privacy/']
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>https://www.fullchoicebreath.com{p}</loc></url>\n' for p in paths)+'</urlset>\n'
(out/'sitemap.xml').write_text(xml)
