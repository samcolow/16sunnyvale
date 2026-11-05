"""Link contract check for the 16 Sunnyvale 3D tour.

Opens every link and QR address on /campaign/, plus a set of home, floor, room and time links,
against a local copy of the site, and confirms each still lands the way it did when the tour went live.
Run before every push:   python3 tools/linkcheck.py [page]   (page defaults to index.html; use beta/index.html for the preview)
Needs Playwright with Chromium. Exits non-zero if any link breaks.
"""
import asyncio, http.server, os, re, sys, threading
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
PORT = 8799
THREE = os.environ.get('THREE_DIR')  # optional local three.js (build/three.min.js, examples/js/controls/OrbitControls.js) when the CDN is unreachable

# expected landing for each fixed link:  gate = Start the tour shown, tour = tour-only mode, home = selected home (None = whole site), floor = 0 outside .. 3 L2
FIXED = [
  ('',                                {'gate': True,  'tour': False, 'home': None, 'floor': 0}),
  ('?utm_source=qr',                  {'gate': True,  'tour': False, 'home': None, 'floor': 0}),
  ('?view=tour',                      {'gate': True,  'tour': True,  'home': None, 'floor': 0}),
  ('#16a',                            {'gate': False, 'tour': False, 'home': 'lot1', 'floor': 0}),
  ('#16c-l1',                         {'gate': False, 'tour': False, 'home': 'lot3', 'floor': 2}),
  ('#16f-l2',                         {'gate': False, 'tour': False, 'home': 'lot6', 'floor': 3}),
  ('#16c-l1-living',                  {'gate': False, 'tour': False, 'home': 'lot3', 'floor': 2, 'spot': 'living'}),
  ('?view=tour#16b',                  {'gate': False, 'tour': True,  'home': 'lot2', 'floor': 0}),
  ('?time=golden&season=winter',      {'gate': False, 'tour': False, 'home': None, 'floor': 0, 'sun': True}),
  ('?time=18:30',                     {'gate': False, 'tour': False, 'home': None, 'floor': 0, 'sun': True}),
]

class Quiet(http.server.SimpleHTTPRequestHandler):
  def log_message(self, *a): pass

def serve():
  os.chdir(ROOT)
  httpd = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Quiet)
  threading.Thread(target=httpd.serve_forever, daemon=True).start()
  return httpd

async def route(r):
  u = r.request.url
  if THREE and 'three.min.js' in u: return await r.fulfill(path=os.path.join(THREE, 'build/three.min.js'), content_type='text/javascript')
  if THREE and 'OrbitControls' in u: return await r.fulfill(path=os.path.join(THREE, 'examples/js/controls/OrbitControls.js'), content_type='text/javascript')
  if u.startswith(f'http://127.0.0.1:{PORT}') or 'cdnjs' in u or 'jsdelivr' in u or 'unpkg' in u: return await r.continue_()
  return await r.abort()   # analytics, fonts: not needed for the check

async def campaign_links(b):
  pg = await b.new_page(); await pg.route('**/*', route)
  await pg.goto(f'http://127.0.0.1:{PORT}/campaign/index.html'); await pg.wait_for_timeout(800)
  urls = await pg.evaluate("[...document.querySelectorAll('.url')].map(e=>e.textContent)")
  qrs = await pg.evaluate("typeof QR!=='undefined'?QR.map(q=>q[2]):[]")
  await pg.close()
  out = []
  for u in urls + qrs:
    s = urlsplit(u); q = '?' + s.query if s.query else ''; h = '#' + s.fragment if s.fragment else ''
    home = re.match(r'#16([a-f])', h); vt = 'view=tour' in q
    out.append((q + h, {'gate': not home and 'time=' not in q, 'tour': vt, 'home': ('lot' + str('abcdef'.index(home.group(1)) + 1)) if home else None, 'floor': 0}))
  return out, len(urls), len(qrs)

STATE = """()=>({gate: !document.getElementById('startGate').hidden,
  tour: document.documentElement.classList.contains('tour-only'),
  sel: (document.querySelector('#info h2')||{}).textContent||'',
  floor: [...document.querySelectorAll('#seg button')].findIndex(b=>b.getAttribute('aria-pressed')==='true'),
  sun: document.getElementById('bSun').getAttribute('aria-pressed')==='true',
  spot: !document.getElementById('spotBar').hidden ? document.getElementById('spotName').textContent : ''})"""

async def check(b, suffix, exp):
  pg = await b.new_page(viewport={'width': 1280, 'height': 800}); await pg.route('**/*', route)
  errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
  await pg.goto(f'http://127.0.0.1:{PORT}/{PAGE}{suffix}'); await pg.wait_for_timeout(3600)
  st = await pg.evaluate(STATE); await pg.close()
  bad = []
  if errs: bad.append('script error: ' + errs[0][:80])
  if st['gate'] != exp['gate']: bad.append(f"start button {'missing' if exp['gate'] else 'shown'}")
  if st['tour'] != exp['tour']: bad.append(f"tour-only {'off' if exp['tour'] else 'on'}")
  want = '16' + 'ABCDEF'[int(exp['home'][3]) - 1] if exp['home'] else None
  if want and want not in st['sel']: bad.append(f"opened {st['sel'] or 'nothing'}, expected {want}")
  if st['floor'] != exp['floor']: bad.append(f"floor {st['floor']}, expected {exp['floor']}")
  if exp.get('sun') and not st['sun']: bad.append('A day here not open')
  if exp.get('spot') and not st['spot']: bad.append('not standing in the room')
  return bad

async def main():
  httpd = serve()
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl'])
    camp, nu, nq = await campaign_links(b)
    cases = FIXED + camp; fails = 0
    for suffix, exp in cases:
      bad = await check(b, suffix, exp)
      if bad: fails += 1; print('FAIL', suffix or '(plain)', '-', '; '.join(bad))
    await b.close()
  httpd.shutdown()
  print(f"{len(cases) - fails}/{len(cases)} links OK ({len(FIXED)} fixed, {nu} campaign links, {nq} QR codes) on {PAGE}")
  sys.exit(1 if fails else 0)

asyncio.run(main())
