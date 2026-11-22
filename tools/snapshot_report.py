"""Freezes the current defects report at /defects/report/<YYYY-MM-DD>/ (Pacific/Auckland date unless given).
Copies defects/data.enc.json (same key, same passcode) and the report page into that folder, and lists the date in
defects/report/snapshots.json. Run after build_defects.py, then commit and push. Re-running on the same day replaces that day's snapshot.
Usage: python3 tools/snapshot_report.py [YYYY-MM-DD]"""
import datetime, json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rep = os.path.join(ROOT, 'defects', 'report')
day = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=13))).strftime('%Y-%m-%d')
out = os.path.join(rep, day); os.makedirs(out, exist_ok=True)
shutil.copy(os.path.join(ROOT, 'defects', 'data.enc.json'), os.path.join(out, 'data.enc.json'))
shutil.copy(os.path.join(rep, 'index.html'), os.path.join(out, 'index.html'))
sp = os.path.join(rep, 'snapshots.json')
l = json.load(open(sp)) if os.path.exists(sp) else []
if day not in l: l = sorted(l + [day])
json.dump(l, open(sp, 'w'))
print('snapshot', day, '| all:', l)
