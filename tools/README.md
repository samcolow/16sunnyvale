# Tools

**The link contract.** The live tour's links and QR codes are in circulation, so changes must only add. These must keep working:
the site address and `/campaign/`; the `utm_*`, `view=tour`, `time` and `season` settings; home links `#16a`–`#16f`, with a floor
(`#16c-l1`) and a room (`#16c-l1-living`); plain and tagged links show Start the tour, home and time links skip it, `view=tour` hides the features and spec.

- `linkcheck.py`: opens every campaign link and QR address plus a set of home, floor, room and time links, and fails if any lands differently. Run before every push.
- `make_beta.py`: copies the live page to `/beta/` (not indexed, no analytics, Preview badge) to try bigger changes before they go live.
