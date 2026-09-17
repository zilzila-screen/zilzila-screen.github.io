#!/usr/bin/env python3
"""Build the standalone static site from the Artifact source.

The Artifact version relies on the claude.ai platform for two things: a shared
database, and the HTML skeleton it gets wrapped in. This produces a
self-contained page that depends on neither, saving survey records in the
viewer's browser instead.

    python3 build_site.py            # -> site/index.html
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "zilzila.html"
SEED = ROOT / "src" / "seed.json"
OUT = ROOT / "index.html"

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'"
    "%3E%3Crect width='32' height='32' fill='%2312304a'/%3E%3Cpath d='M3 18h4l2-5 3 12"
    " 3-18 3 20 3-13 2 6 2-2h4' fill='none' stroke='%23e8a33d' stroke-width='2'"
    " stroke-linejoin='round' stroke-linecap='round'/%3E%3C/svg%3E"
)


def main():
    s = SRC.read_text()
    seed = json.loads(SEED.read_text())
    for i, r in enumerate(seed, 1):
        r["id"] = "demo-%03d" % i
        r.pop("idx", None)          # the model computes these; never store them
        r.pop("grade", None)

    cut = s.index("</style>") + len("</style>")
    head, body = s[:cut], s[cut:]
    head = head.replace(re.search(r"<title>.*?</title>", head).group(0), "", 1)

    # --- platform database -> browser storage -----------------------------
    start = body.index('(function(){\n  var s=el("r-stat");')
    end = body.index("})();\n})();", start)
    assert end > start, "could not locate the storage initialiser"
    body = body[:start] + '''(function(){
  var s=el("r-stat");
  rows=lsLoad();
  s.textContent=lsOK()?"Saved in this browser":"Storage unavailable";
  renderFolio();
''' + body[end:]

    storage = '''
/* ---------- browser storage ---------- */
var LS_KEY="zilzila.screenings.v1";
var SEED=''' + json.dumps(seed, separators=(",", ":")) + ''';
function lsOK(){
  try{localStorage.setItem("__z","1");localStorage.removeItem("__z");return true;}
  catch(e){return false;}
}
function lsLoad(){
  if(!lsOK())return SEED.slice();
  try{
    var a=JSON.parse(localStorage.getItem(LS_KEY));
    if(a&&a.length)return a;
  }catch(e){}
  lsSave(SEED);
  return SEED.slice();
}
function lsSave(a){
  try{localStorage.setItem(LS_KEY,JSON.stringify(a));}catch(e){}
}

'''
    marker = "/* ================= PORTFOLIO ================= */"
    body = body.replace(marker, storage + marker, 1)

    def swap(old, new):
        nonlocal body
        assert old in body, "build: could not find\n" + old[:90]
        body = body.replace(old, new, 1)

    swap('''  if(!db){local.unshift(rec);renderFolio();toast("Added — this session only");return;}
  db.collection("screenings").add(rec).then(function(){toast("Added to schedule");})
    .catch(function(e){
      local.unshift(rec);renderFolio();
      toast(e&&e.code==="quota_exceeded"?"Schedule full — remove records"
                                        :"Could not reach the shared schedule");});''',
         '''  rec.id="r"+Date.now().toString(36);
  rows.unshift(rec);lsSave(rows);renderFolio();
  toast(lsOK()?"Added to schedule":"Added — not saved, storage unavailable");''')

    swap('''  var id=b.getAttribute("data-id");
  if(db&&id)db.collection("screenings").doc(id).delete()
    .catch(function(){toast("Could not remove that record");});
  else{local.splice(parseInt(b.getAttribute("data-n"),10),1);renderFolio();}''',
         '''  var id=b.getAttribute("data-id");
  for(var n=0;n<rows.length;n++){
    if(rows[n].id===id){rows.splice(n,1);lsSave(rows);renderFolio();return;}
  }
  rows.splice(parseInt(b.getAttribute("data-n"),10),1);lsSave(rows);renderFolio();''')

    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Rapid seismic vulnerability triage for the Tashkent
 building stock. EMS-98 screening with a retrofit priority portfolio.">
<meta name="author" content="Ravshanbek Karomatov">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{FAVICON}">
<title>Zilzila Screen</title>
<style>
:root{{color-scheme:light dark;
  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
body{{margin:0}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
{head.strip()}
</head>
<body>
{body.strip()}
</body>
</html>
'''
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(doc)
    assert "claude" not in doc, "platform reference survived the build"
    print(f"built {OUT} — {len(doc):,} bytes, {len(seed)} seed records")


if __name__ == "__main__":
    main()
