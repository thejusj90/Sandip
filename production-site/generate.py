"""Build a local review copy, or build for your real HTTPS domain."""
import argparse, html, json, os, re, shutil
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from xml.sax.saxutils import escape as xml
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--out',default='preview')
p.add_argument('--domain',help='Optional real HTTPS origin for production metadata')
p.add_argument('--form-action',help='Optional HTTPS form endpoint. Must validate submissions and handle success/failure.')
p.add_argument('--privacy-file',help='Approved plain text privacy notice; required for a live form.')
a=p.parse_args()
if a.form_action and not a.privacy_file:p.error('Supply the approved privacy notice for the live form.')
def https(v,origin=False):
 u=urlsplit(v)
 return u.scheme=='https' and bool(u.hostname) and (not origin or (u.path in ('','/') and not u.query and not u.fragment))
if a.domain and not https(a.domain,True):p.error('Use a real HTTPS site origin.')
if a.form_action and (not a.domain or not https(a.form_action)):p.error('A form endpoint requires a domain and HTTPS.')
site=(a.domain or '').rstrip('/')
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
content=ROOT/'content'
rows=json.loads((content/'seo-meta.json').read_text())
routes={r['URL path']:r for r in rows}
sectors=[r for r in rows if r['URL path'].startswith('/solutions/') and r['URL path']!='/solutions/']
impact='/impact-advisory/'
article=[r for r in rows if r['Page'].startswith('Article')]
assets=dict(zip([r['URL path'] for r in sectors],['corp-hd.webp','education-hd.webp','ngo-hd.webp','hospitality-hd.webp','facilities-hd.webp','executives-hd.webp']))
photo_alt={'nature-hd.webp':'Illustrative image of balanced river stones in a calm natural setting','corp-hd.webp':'Illustrative image of colleagues in a workplace discussion','education-hd.webp':'Illustrative image of educators in a group discussion','ngo-hd.webp':'Illustrative image of a community meeting','hospitality-hd.webp':'Illustrative image of a tropical hospitality setting','facilities-hd.webp':'Illustrative image of a wellness facility interior','executives-hd.webp':'Illustrative portrait of a professional in a work setting','home-hd.webp':'Illustrative image of a facilitated group discussion','nature.jpg':'Illustrative image of a green retreat setting','brand-logo-light.webp':'Dīpātma Holistic Wellness logo'}
sector_desc=['Workforce well-being, manager training and healthier work routines.','Educator capability, student well-being and campus planning.','Accessible programmes, caregiver support and local facilitator development.','Guest experience design, signature programmes and retreat operations.','Service design, facility readiness and client journeys.','Private coaching, recovery and sustainable leadership routines.']
article_desc=['What makes a workshop useful after the event ends.','How to turn a property’s assets into a distinct guest experience.','Design programmes for accessibility, local ownership and handover.','Agree a shared outcome, test a route to change and decide what comes next.']
interests={'consulting':'Consulting or assessment','training':'Training or workshop','design':'Programme design','partnership':'Strategic partnership','impact-strategy':'Community Impact Strategy','decision-impact-review':'Decision Impact Review','impact-readiness':'Impact Readiness Scan','impact-pilot':'Pilot design or evaluation','unsure':'Other or unsure'}
e=html.escape
def dest(route):return out/route.strip('/')/'index.html'
def link(h):
 u=urlsplit(h)
 if not u.path.startswith('/') or u.netloc:return h
 if site:return h
 target=dest(u.path) if u.path.endswith('/') else out/u.path.lstrip('/')
 rel=os.path.relpath(target,dest(current).parent)
 return urlunsplit(('', '',rel,u.query,u.fragment))
def href(s):return e(link(s),quote=True)
def ac(name,h,kind='dark'):return f'<a class="btn btn-{kind}" href="{href(h)}">{e(name)}</a>'
def inline(s):
 q=e(s)
 q=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<a href="{href(html.unescape(m[2]))}">{m[1]}</a>',q)
 q=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',q)
 q=re.sub(r'(?<!\*)\*([^*]+)\*',r'<em>\1</em>',q)
 if '→' in s:
  first,url=s.rsplit('→',1);url=url.strip()
  if url.startswith(('/','#')) and not re.search(r'\s',url):
   caption=first.strip()
   caption=re.sub(r'^\*\*[^*]+:\*\*\s*','',caption)
   if not caption:caption='Read the article'
   if len(caption)>90:return q.split('→',1)[0]+' <a class="textlink" href="'+href(url)+'">Explore this sector</a>'
   return f'<a class="textlink" href="{href(url)}">{e(caption.replace("**",""))}</a>'
 return q
def img(asset,loading='lazy',decorative=False):
 return f'<img src="{href("/assets/"+asset+"?v=20261121-hd")}" alt="{e("" if decorative else photo_alt.get(asset,""))}" loading="{loading}" decoding="async">'
def impact_url(i='impact-strategy'):
 return '/contact/?sector=impact-advisory&interest='+i+'#enquiry'
def section(h,b,cl='',id=''):
 return f'<section class="sec {cl}"'+(f' id="{e(id)}"' if id else '')+f'><div class="container">{f"<h2>{e(h)}</h2>" if h else ""}{b}</div></section>'
def markdown_lines(lines):
 res=[];mode=None
 def end():
  nonlocal mode
  if mode:res.append('</'+mode+'>');mode=None
 for s in lines:
  s=s.strip()
  if not s or s.startswith('>') or s.startswith('**Editorial'):continue
  if s.startswith('### '):end();res.append('<h3>'+inline(s[4:])+'</h3>')
  elif s.startswith('## '):end();res.append('<h2>'+inline(s[3:])+'</h2>')
  elif re.match(r'^(?:- |\d+\. )',s):
   pfx=re.match(r'^(?:- |\d+\. )',s);new='ul' if s.startswith('-') else 'ol'
   if new!=mode:end();mode=new;res.append('<'+mode+'>')
   res.append('<li>'+inline(s[pfx.end():])+'</li>')
  else:
   end()
   if s.startswith('**Reference:**') and 'https://' in s:
    caption,u=s.rsplit('https://',1);res.append('<p>'+inline(caption)+'<a href="'+e('https://'+u,quote=True)+'">WHO guidelines on mental health at work</a></p>')
   else:res.append('<p>'+inline(s)+'</p>')
 end()
 return ''.join(res)
def parts(lines):
 groups=[];lead=[]
 for s in lines:
  if s.startswith('### '):groups.append((s[4:],[]))
  elif groups:groups[-1][1].append(s)
  else:lead.append(s)
 return lead,groups
def faqs(lines):
 _,groups=parts(lines)
 return '<div class="prose faqs">'+''.join(f'<details><summary>{e(h)}</summary>{markdown_lines(b)}</details>' for h,b in groups)+'</div>'
def impact_preview():
 b='<div><span class="eyebrow">CROSS-SECTOR ADVISORY</span><h2>What will your decision change?</h2></div><div><p>Review who may benefit or bear the costs before you commit. Or start with a community priority and design a pilot to test what could improve it.</p><div class="btnrow">'+ac('Explore Impact Advisory',impact)+ac('Discuss an impact brief',impact_url(),'outline')+'</div></div>'
 return section('',b,'highlight')
def sector_cards():
 return '<div class="cards">' + ''.join(f'<a class="card linked-card" href="{href(r["URL path"])}">{img(assets[r["URL path"]],decorative=True)}<div class="card-copy"><span class="eyebrow">SECTOR SOLUTIONS</span><h3>{e(r["Page"])}</h3><p>{e(d)}</p><span class="arrow">Explore sector</span></div></a>' for r,d in zip(sectors,sector_desc)) + '</div>'
def article_cards():
 return '<div class="grid-four">'+''.join(f'<a class="card linked-card" href="{href(r["URL path"])}">{img(asset,decorative=True)}<div class="card-copy"><span class="eyebrow">{e(r["Page"].split(": ")[-1])}</span><h3>{e(r["Proposed H1"])}</h3><p>{e(d)}</p><span class="arrow">Read insight</span></div></a>' for r,asset,d in zip(article,['corp-hd.webp','hospitality-hd.webp','ngo-hd.webp','nature.jpg'],article_desc))+'</div>'
def visual():
 return '<aside class="decision-visual" aria-label="Community impact strategy at a glance"><span>THE ADVISORY BRIEF</span><h2>One community.<br>One outcome to test.</h2>'+''.join(f'<div class="visual-row"><span>0{i}</span><div>{t}</div></div>' for i,t in enumerate(['Listen to the people affected','Compare practical options','Design a costed pilot','Review what changed'],1))+'<small>A framework for making decisions, not a report of client results.</small></aside>'
def hero(h,eyebrow,intro,buttons=(),asset=None):
 cl=(' impact-hero' if current==impact else ' home' if current=='/' else '')+(' lean' if not asset and current!=impact else '')
 visual_html=visual() if current==impact else f'<div class="hero-photo{" logo-image" if asset=="brand-logo-light.webp" else " approach-image" if asset=="nature-hd.webp" else " home-image" if asset=="home-hd.webp" else ""}">{img(asset,"eager")}</div>' if asset else ''
 bc=''
 if current in assets:bc=f'<div class="hero-crumb"><a href="{href("/solutions/")}">Solutions</a> / {e(routes[current]["Page"])}</div>'
 elif any(r['URL path']==current for r in article):bc=f'<div class="hero-crumb"><a href="{href("/insights/")}">Insights</a> / Article</div>'
 acts='<div class="actions">'+''.join(ac(n,h,'outline' if i else 'dark') for i,(n,h) in enumerate(buttons))+'</div>' if buttons else ''
 return f'<section class="hero{cl}"><div class="container hero-flex"><div>{bc}<span class="eyebrow">{e(eyebrow)}</span><h1>{e(h)}</h1>{f"<p>{e(intro)}</p>" if intro else ""}{acts}</div>{visual_html}</div></section>'
def form():
 options=[(r['URL path'].strip('/').split('/')[-1],r['Page']) for r in sectors]+[('impact-advisory','Impact Advisory / Cross-sector'),('other','Other')]
 def select(name,label,x):
  return f'<label>{label}<select name="{name}"><option value="">Not sure yet</option>'+''.join(f'<option value="{e(i)}">{e(t)}</option>' for i,t in x)+'</select></label>'
 def fd(t,n,attr='',req=False):
  return f'<label>{t}{" *" if req else ""}<input name="{n}" {attr} {"required" if req else ""}></label>'
 action=f' action="{e(a.form_action,quote=True)}" method="post" data-live="true"' if a.form_action else ' data-live="false"'
 hidden=f'<input type="hidden" name="_subject" value="New Dīpātma project enquiry"><input type="hidden" name="_template" value="table"><input type="hidden" name="_next" value="{e(site)}/thank-you/"><input type="text" name="_honey" class="form-trap" tabindex="-1" autocomplete="off" aria-hidden="true">' if a.form_action else ''
 return f'''<section class="sec" id="enquiry"><div class="container contact-layout"><div><span class="eyebrow">START WITH CONTEXT</span><h2>Project enquiry</h2><p>Tell us enough to understand the opportunity. Please do not submit personal medical information or confidential participant data.</p><p>Based in Goa, India. On-site and online delivery is scoped to the assignment.</p><p>Prefer email? <a class="textlink" href="mailto:wellnesswithsandip@gmail.com">wellnesswithsandip@gmail.com</a></p></div><div class="form-card"><form id="project-enquiry"{action}>{hidden}<p>{'Fields marked * are required.' if a.form_action else 'Preview only. Fields marked * are required. Nothing is sent.'}</p><div class="form-row">{fd('Full name','name','autocomplete="name" maxlength="120"',True)}{fd('Email','email','type="email" autocomplete="email" maxlength="180"',True)}</div><label>What would you like help with? *<span id="brief-hint"></span><textarea name="message" aria-describedby="brief-hint" required minlength="15" maxlength="2400"></textarea></label><details class="project-details" id="project-details"><summary>Add project details (optional)</summary><div class="project-details-fields">{fd('Organisation','organisation','autocomplete="organization" maxlength="150"')}<div class="form-row">{select('sector','Client category',options)}{select('interest','Type of support',list(interests.items()))}</div><div class="form-row">{fd('Project location','location','maxlength="120"')}{fd('Decision or launch deadline','timeline','maxlength="100"')}</div>{fd('Budget range (optional)','budget','maxlength="100"')}</div></details><label class="privacycheck"><input type="checkbox" name="consent" value="yes" required><span>I understand how my information is handled, as described in the <a href="{href('/privacy/')}">privacy notice</a>.</span></label><button class="btn btn-dark" type="submit">{'Send project enquiry' if a.form_action else 'Test enquiry in preview'}</button><p class="form-status" id="form-status" role="status" aria-live="polite"></p></form></div></div></section>'''
def foot():
 def col(h,l):return '<div><b>'+h+'</b>'+''.join(f'<a href="{href(u)}">{e(n)}</a>' for n,u in l)+'</div>'
 cta_name='Discuss an impact brief' if current==impact else 'Discuss a project'
 cta_url=impact_url() if current==impact else '/contact/'
 cta='' if current in ['/contact/','/thank-you/','/privacy/'] else '<section class="cta-footer"><div class="container footercta-grid"><div><span class="eyebrow">BEGIN A CONVERSATION</span><h2>What are you working on?</h2></div><p>Tell us who the work is for and what you need to decide or deliver.</p>'+ac(cta_name,cta_url,'gold')+'</div></section>'
 return cta+'<footer class="footer"><div class="container footergrid"><div class="footbrand"><span class="footbrand-name">Dīpātma</span><span>HOLISTIC WELLNESS</span><p>Strategic wellness consulting, training, partnerships and impact advisory.</p></div>'+col('Explore',[('All solutions','/solutions/'),('Impact Advisory',impact),('Our approach','/approach/'),('About Dīpātma','/about/'),('Insights','/insights/')])+col('Sectors',[(r['Page'],r['URL path']) for r in sectors])+col('Connect',[('Project enquiries','/contact/'),('Email Dīpātma','mailto:wellnesswithsandip@gmail.com'),('Privacy notice','/privacy/')])+'</div><div class="container footline"><span>© Dīpātma Holistic Wellness</span><span>Goa, India'+(' · Website preview' if not site else '')+'</span></div></footer>'
def shell(r,b,utility=False):
 nav=[('Solutions','/solutions/'),('Impact Advisory',impact),('Our approach','/approach/'),('About','/about/'),('Insights','/insights/'),('Contact','/contact/')]
 def navlink(n,u):
  active=current==u or (u in ['/solutions/','/insights/'] and current.startswith(u))
  return f'<a class="navlink{" impact-nav" if u==impact else ""}" href="{href(u)}"'+(' aria-current="page"' if current==u else ' aria-current="location"' if active else '')+f'>{e(n)}</a>'
 noindex=not site or utility
 title,desc=r['SEO title'],r['Meta description']
 tag=lambda name,val:f'<meta name="{name}" content="{e(val,quote=True)}">'
 head=tag('theme-color','#173c36')+tag('description',desc)+tag('robots','noindex,follow' if noindex else 'index,follow')+''.join(f'<meta property="{k}" content="{e(v,quote=True)}">' for k,v in {'og:title':title,'og:description':desc,'og:type':'article' if r in article else 'website'}.items())
 if site:
  head+=f'<meta property="og:image" content="{e(site)}/assets/home-hd.webp">'+tag('twitter:card','summary_large_image')
 if site and not utility:
  url=site+current;head+=f'<link rel="canonical" href="{e(url)}"><meta property="og:url" content="{e(url)}">'
  org={'@type':'Organization','@id':site+'/#organization','name':'Dīpātma Holistic Wellness','url':site+'/','logo':site+'/assets/brand-logo-light.webp'}
  graph=[org,{'@type':'WebPage','@id':url+'#webpage','url':url,'name':title,'description':desc,'inLanguage':'en-IN'}]
  if current in assets or current==impact:graph.append({'@type':'Service','name':r['Page'],'description':desc,'url':url,'provider':{'@id':org['@id']}})
  if current!='/':
   prev='/solutions/' if current in assets else '/insights/' if r in article else ''
   entries=[('Home','/')]+([(routes[prev]['Page'],prev)] if prev else [])+[(r['Proposed H1'] if r in article else r['Page'],current)]
   graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','name':n,'item':site+u,'position':i} for i,(n,u) in enumerate(entries,1)]})
  head+='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')+'</script>'
 header=f'''<a class="skip" href="#main">Skip to content</a><div class="topline"><div class="container topinner"><span>STRATEGIC WELLNESS · TRAINING · IMPACT ADVISORY</span><span>GOA · INDIA · ONLINE</span></div></div><header class="site-header"><div class="container navrow"><a class="brand" href="{href('/')}" aria-label="Dīpātma Holistic Wellness home"><span class="brand-mark">{img('logo-emblem-light.webp','eager',True)}</span><span class="brandtype"><b>Dīpātma</b><em>HOLISTIC WELLNESS</em></span></a><nav id="navigation" aria-label="Main navigation">{''.join(navlink(n,u) for n,u in nav)}</nav>{ac('Discuss a project','/contact/').replace('btn-dark','btn-dark btn-nav')}<button class="mobile-menu" type="button" aria-controls="navigation" aria-expanded="false">Menu</button></div></header>'''
 return f'<!doctype html><html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>{head}<link rel="icon" type="image/png" sizes="32x32" href="{href('/assets/favicon-light.png')}"><link rel="apple-touch-icon" sizes="180x180" href="{href('/assets/apple-touch-icon-light.png')}"><link rel="stylesheet" href="{href("/assets/base.css")}"><link rel="stylesheet" href="{href("/assets/site.css?v=complete-logo-20261121")}"><link rel="stylesheet" href="{href("/assets/mobile.css?v=20261121-mobile-1")}"><script defer src="{href("/assets/site.js?v=20261121-priorities")}"></script></head><body>{header}<main id="main">{b}</main>{foot()}</body></html>'
def render_row(r):
 is_article=r in article
 lines=(content/('articles' if is_article else 'pages')/r['Markdown filename']).read_text().splitlines()
 heading=r['Proposed H1']
 if is_article:
  category=next((s.split('**Article category:**',1)[1].strip() for s in lines if s.startswith('**Article category:**')),'Insights')
  lines=[s for s in lines[1:] if not s.startswith(('**Article category:**','**Suggested author:**','**Publication date:**','**Suggested reading time:**','>'))]
  return hero(heading,category,r['Meta description'])+'<article class="article-main"><div class="container prose">'+markdown_lines(lines)+'</div></article>'
 groups=[]
 for s in lines[1:]:
  if s.startswith('## '):groups.append((s[3:],[]))
  elif groups:groups[-1][1].append(s)
 eyebrow=next((s.split(':**',1)[1].strip() for s in lines if s.startswith('**Eyebrow:**')),'Dīpātma Holistic Wellness')
 lead=next((s.split(':**',1)[1].strip() for s in lines if s.startswith('**Hero introduction:**')),'')
 buttons=[]
 for s in lines:
  if s.startswith(('**Primary CTA:**','**Secondary CTA:**')) and '→' in s:
   n,u=s.split(':**',1)[1].split('→',1);buttons.append((n.strip(),u.strip()))
 if current=='/':buttons=[('Explore our solutions','/solutions/'),('Explore Impact Advisory',impact)]
 hero_pic=assets.get(current) or {'/':'home-hd.webp','/about/':'brand-logo-light.webp','/contact/':'hospitality-hd.webp','/approach/':'nature-hd.webp'}.get(current)
 body=hero(heading,eyebrow,lead,buttons,hero_pic)
 if current=='/':body+=impact_preview()
 for title,lines in groups:
  match=re.search(r' \{#([^}]+)\}$',title);sid=match[1] if match else '';h=title[:match.start()] if match else title
  if h.startswith('Impact Advisory') and current=='/':continue
  if h.startswith('Impact Advisory') and current=='/solutions/':body+=impact_preview();continue
  if (current=='/' and h.startswith('Wellness solutions designed')) or (current=='/solutions/' and sid=='sectors'):
   body+=section(h,sector_cards(),id=sid);continue
  if current=='/insights/' and h.startswith('Explore our latest'):
   body+=section(h,article_cards());continue
  if current=='/contact/' and sid=='enquiry':
   body+=form();continue
  if current=='/' and h.startswith('The Dīpātma Method'):
   desc=['Understand the needs, people and setting.','Design a programme, service or pilot.','Test the design in its real setting.','Transfer tools and agree who owns the work.','Review what changed and decide what comes next.']
   body+=section(h,'<div class="steps">'+''.join(f'<div class="step"><div class="step-num">0{i}</div><b>{n}</b><span>{d}</span></div>' for i,(n,d) in enumerate(zip(['Insight','Architecture','Activation','Continuity','Evidence'],desc),1))+'</div><div class="btnrow">'+ac('See how we work','/approach/','outline')+'</div>')
   continue
  if h.startswith('Frequently asked'):
   body+=section(h,faqs(lines));continue
  if current==impact and sid=='services':
   _,cards=parts(lines)
   body+=section(h,'<div class="pair">'+''.join(f'<article class="card impact-card"><span class="eyebrow">{e(label)}</span><h3>{e(head)}</h3>{markdown_lines(b)}{ac(cta,impact_url(key),"dark" if i==0 else "outline")}</article>' for i,((head,b),label,cta,key) in enumerate(zip(cards,['FLAGSHIP ENGAGEMENT','PRE-DECISION ADVISORY'],['Discuss a strategy brief','Request a decision review'],['impact-strategy','decision-impact-review'])))+'</div>',id=sid)
   continue
  leadlines,groups3=parts(lines)
  if groups3 and (current==impact or any(w in h.lower() for w in ['services','solutions','three ways','principles']) or sid=='method'):
   grid='pair' if len(groups3)==4 else 'cards'
   body+=section(h,'<div class="prose">'+markdown_lines(leadlines)+'</div>'+f'<div class="{grid}">'+''.join(f'<article class="card"><h3>{e(name)}</h3>{markdown_lines(b)}</article>' for i,(name,b) in enumerate(groups3,1))+'</div>',id=sid)
   continue
  filtered=[s for s in lines if not s.startswith(('**Contact details:**','**Author line format:**'))]
  body+=section(h,'<div class="prose">'+markdown_lines(filtered)+'</div>',id=sid)
 if current=='/':
  body+=section('Insights for your next decision',article_cards())
 return body

for row in rows:
 current=row['URL path'];target=dest(current);target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(shell(row,render_row(row)),encoding='utf-8')
extras=[('/privacy/','Privacy notice','How this website handles information.'),('/thank-you/','Enquiry confirmation','Confirmation of a submitted enquiry.')]
for current,title,desc in extras:
 if current=='/privacy/':
  notice=Path(a.privacy_file).read_text() if a.privacy_file else 'This review version does not send or store enquiry form details. No analytics are included in this build. A live notice should explain how enquiries are handled and provide a verified point of contact.'
  body=hero(title,'WEBSITE INFORMATION','')+section('Enquiry information','<div class="prose policy">'+markdown_lines(notice.splitlines())+'</div>')
 else:
  intro='An enquiry was not submitted through this preview.' if not a.form_action else 'If you have just submitted the project enquiry form, you can return to the site below.'
  body=hero('Enquiry confirmation','PROJECT ENQUIRIES',intro,[('Return home','/')])
 target=dest(current);target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(shell({'SEO title':title+' | Dīpātma','Meta description':desc},body,True),encoding='utf-8')
current='/'
(out/'404.html').write_text(shell({'SEO title':'Page not found | Dīpātma','Meta description':'Return to the Dīpātma website.'},hero('Page not found','WEBSITE NAVIGATION','The address you entered may have changed.',[('Return home','/')]),True),encoding='utf-8')
shutil.copytree(ROOT/'assets',out/'assets',dirs_exist_ok=True)
if site:
 (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+site+'/sitemap.xml\n')
 (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+xml(site+r['URL path'])+'</loc></url>\n' for r in rows)+'</urlset>\n')
else:(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print(f'{len(rows)} content pages, {len(extras)} utility pages and fallback built to {out}')
