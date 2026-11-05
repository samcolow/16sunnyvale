"""Builds the preview at /beta/ from index.html: same page, not indexed, no analytics, a small Preview badge.
Work on beta/index.html for bigger changes, try it at 16sunnyvale.sasu.co.nz/beta/, then copy the change into index.html.
Usage: python3 tools/make_beta.py   (copies index.html to beta/index.html; run it when starting a new preview)"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'index.html')).read()
s = re.sub(r'<script defer id="umami-tracker"[^>]*></script>\n?', '', s)            # previews don't count in analytics
s = s.replace('<meta name=viewport', '<meta name="robots" content="noindex,nofollow"><meta name=viewport', 1)
s = s.replace('./audio/', '../audio/')                                              # shared audio files
s = s.replace('</body>', '<div style="position:fixed;left:12px;bottom:12px;z-index:9999;background:#e0a020;color:#1b2438;font:600 12px/1 sans-serif;padding:6px 10px;border-radius:999px;pointer-events:none">Preview · not the live tour</div>\n</body>', 1)
os.makedirs(os.path.join(ROOT, 'beta'), exist_ok=True)
open(os.path.join(ROOT, 'beta', 'index.html'), 'w').write(s)
print('beta/index.html written')
