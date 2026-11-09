# Tools

**The link contract.** The live tour's links and QR codes are in circulation, so changes must only add. These must keep working:
the site address and `/campaign/`; the `utm_*`, `view=tour`, `time` and `season` settings; home links `#16a`–`#16f`, with a floor
(`#16c-l1`) and a room (`#16c-l1-living`); plain and tagged links show Start the tour, home and time links skip it, `view=tour` hides the features and spec.

- `linkcheck.py`: opens every campaign link and QR address plus a set of home, floor, room and time links, and fails if any lands differently. Run before every push.
- `make_beta.py`: copies the live page to `/beta/` (not indexed, no analytics, Preview badge) to try bigger changes before they go live.

## Floor areas — one system of record

The schedule **"16 Sunnyvale Road - Floor and Room Area Breakdown"** (Google Doc,
https://docs.google.com/document/d/1-RRCxcrhvH-cFtqFmYIh6POzNFPEMS9Bomum3EvdRw0/edit) is the source of record.
The page copies it into one table, `const AREAS` in `index.html` (A = 16A, M = 16B–E, F = 16F).
The home cards, the headline "141–148 m²" and every room label read from that table; room labels
use keys like `'Garage · {garage}'`. To change a figure: update the doc, then the table, nothing else.
`linkcheck.py` fails if a hard-coded `… m²` figure appears anywhere outside the table.
