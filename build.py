"""Build static reading pages.  py -3.12 build.py
Each article = src/<name>.py with ARTICLE + DICT. Output: articles/<slug>/index.html and index.html (library)."""
import glob, importlib.util, os, re, json, html as H
ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = re.compile(r"[A-Za-z]+(?:[-'’/][A-Za-z]+)*|\d[\d,.]*|[^A-Za-z\d]+")

def load(p):
    s = importlib.util.spec_from_file_location("a_" + os.path.basename(p)[:-3], p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def wrap(text, D, missing):
    out = []
    for t in TOKEN.findall(text):
        k = t.lower().replace("’", "'")
        if re.match(r"[A-Za-z]", t):
            if k in D: out.append(f'<span class="w" data-t="{H.escape(D[k], True)}">{H.escape(t)}</span>')
            else: missing.add(k); out.append(H.escape(t))
        else: out.append(H.escape(t))
    return "".join(out)

CSS = open(os.path.join(ROOT, "src", "isaac.css"), encoding="utf-8").read()
PAGE = open(os.path.join(ROOT, "src", "page.html"), encoding="utf-8").read()
LIB = open(os.path.join(ROOT, "src", "library.html"), encoding="utf-8").read()

cards = []
for p in sorted(glob.glob(os.path.join(ROOT, "src", "*.py"))):
    m = load(p); A, D = m.ARTICLE, m.DICT; missing = set()
    paras = "".join(f"<p>{wrap(t, D, missing)}</p>" for t in A["paras"])
    sp = "".join(f'<li>{wrap(q, D, missing)}</li>' for q in A["speaking"]) or '<li class="soon">The questions are coming soon…</li>'
    src = " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in A["sources"])
    html = (PAGE.replace("__CSS__", CSS).replace("__TITLE__", H.escape(A["title"])).replace("__TAG__", A["tag"]).replace("__DATE__", A["date"])
            .replace("__LEVEL__", A["level"]).replace("__PARAS__", paras).replace("__SPEAK__", sp).replace("__SOURCES__", src).replace("__WORDS__", str(len(" ".join(A["paras"]).split()))))
    d = os.path.join(ROOT, "articles", A["slug"]); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    cards.append(f'<a class="card" href="articles/{A["slug"]}/index.html"><span class="lv">{A["level"]}</span><h2>{H.escape(A["title"])}</h2><p>{H.escape(A["intro"])}</p><small>{A["tag"]} · {A["date"]}</small></a>')
    print(A["slug"], "missing:", sorted(missing))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(LIB.replace("__CSS__", CSS).replace("__CARDS__", "\n".join(reversed(cards))))
