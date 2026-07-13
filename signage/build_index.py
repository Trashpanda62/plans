#!/usr/bin/env python3
"""build_index.py — regenerate the signage dashboard index.html from the asset pairs.

Every card renders: a PNG preview (click to open full) + a PDF download button + a PNG
download button. Sections are curated below; any pair not listed falls into "More".
Polish target: the storybook look (parchment/wood, serif display, soft cards) — no video.
"""
from __future__ import annotations
from pathlib import Path
import html

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

# curated sections: (Section title, note, [ (slug, Title, tag) ... ])
SECTIONS = [
    ("Farm Day", "The Farm Day Saturdays campaign — print flyers + social graphics.", [
        ("tapestry-farm-day-letter", "Farm Day — Letter Flyer", "Flyer"),
        ("tapestry-farm-day-quarter", "Farm Day — Quarter Flyer", "Flyer"),
        ("tapestry-farm-day-quarter-4up", "Farm Day — Quarter (4-up print)", "Print"),
        ("tapestry-farm-day-social-1080x1080", "Farm Day — Social (Square)", "Social"),
        ("tapestry-farm-day-social-1080x1350", "Farm Day — Social (Portrait)", "Social"),
    ]),
    ("Animal & Pasture Signs", "Signs posted around the farm by each animal and pasture.", [
        ("tapestry-acres-alpaca-sign", "Alpacas", "Sign"),
        ("tapestry-acres-alpaca-fiber-sign", "Alpaca Fiber", "Sign"),
        ("tapestry-acres-alpaca-uses-sign", "Alpaca Uses", "Sign"),
        ("tapestry-acres-highland-sign", "Highland Cattle", "Sign"),
        ("tapestry-acres-goats-sign", "Goats", "Sign"),
        ("tapestry-acres-nigerian-dwarves-sign", "Nigerian Dwarf Goats", "Sign"),
        ("tapestry-acres-kunekune-sign", "KuneKune Pigs", "Sign"),
        ("tapestry-acres-mules-sign", "Mules", "Sign"),
        ("tapestry-acres-murphy-sign", "Murphy", "Sign"),
        ("tapestry-acres-penelope-sign", "Penelope", "Sign"),
        ("tapestry-acres-drylot-sign", "The Drylot", "Sign"),
        ("tapestry-acres-poison-ivy-sign", "Poison Ivy Warning", "Warning"),
        ("alpaca-walks-sign", "Alpaca Walks", "Sign"),
        ("alpaca-parking-sign", "Alpaca Parking", "Sign"),
    ]),
    ("Trail Sign Packages", "Full interpretive trail-sign packages — one sign per page, print-ready.", [
        ("dale-hollow-trail-signs", "The Drowned Valley — Dale Hollow (24 signs)", "Trail set"),
        ("tapestry-and-dale-hollow-trail-signs", "Dale Hollow + Tapestry Acres (36 signs)", "Trail set"),
    ]),
    ("Ads & Flyers", "Food-truck menu ads, promo flyers, and printable handouts.", [
        ("tapestry-acres-smashburger-ad", "Smashburger", "Ad"),
        ("tapestry-acres-brats-ad-v2", "Bratwurst", "Ad"),
        ("tapestry-acres-queso-ad", "Queso", "Ad"),
        ("tapestry-acres-drinks-ad", "Drinks", "Ad"),
        ("smashburger-flyer", "Smashburger Flyer", "Flyer"),
        ("tapestry-acres-food-truck-saturdays", "Food Truck Saturdays", "Flyer"),
        ("tapestry-acres-flyer-letter", "Farm Flyer (Letter)", "Flyer"),
        ("tapestry-acres-flyer-parchment", "Farm Flyer (Parchment)", "Flyer"),
        ("tapestry-acres-rack-card", "Rack Card", "Handout"),
        ("tapestry-acres-rack-card-1", "Rack Card (Alt)", "Handout"),
        ("tapestry-acres-may-rv-promo", "RV Sites Promo", "Promo"),
        ("tapestry-farm-card", "Farm Card", "Handout"),
    ]),
    ("Logos & Brand", "Tapestry Acres logo marks and brand assets.", [
        ("final-logo-blue", "Primary Logo (Blue)", "Logo"),
        ("original", "Original Logo", "Logo"),
        ("black-and-grey-animal-farm-retro-logo", "Retro Farm Logo", "Logo"),
        ("black-and-white-vintage-chicken-farm-logo", "Vintage Chicken Logo", "Logo"),
        ("black-and-white-vintage-circle-farm-logo", "Vintage Circle Logo", "Logo"),
    ]),
]

# Info / text signs whose master is a graphic-only docx (no readable text layer) or is
# best shown as clean web text — kept as styled text cards, unchanged in spirit from v1.
TEXT_CARDS = [
    ("Animal Feed", "$1 each — Alpaca &amp; Goat Feed, Animal Crackers for cows &amp; goats, Chicken Feed. Please feed gently: hands flat. Thank you!", "Info"),
    ("Guest Wi-Fi", "Network: <strong>Tapestry Acres</strong> · Password: <strong>maxfield</strong>. Scan to connect, or enter manually. tapestryacres.com", "Info"),
    ("Alpaca Rental", "$25 for 30 minutes · $40 for 1 hour. Need one longer? Ask our staff about bringing alpacas to your next event.", "Info"),
    ("Walking Your Alpaca — Safe Handling Rules", "Approach from the side, keep the lead loose (never around your hand), no pulling, hands off the head/face, no treats from your pocket, stay calm and quiet. If something feels off, stop and bring the alpaca back to staff.", "Rules"),
    ("Sorghum — The Roller Mill", "Juice-extraction press: the first stop in making sorghum syrup. Heavy iron rollers, traditionally mule-powered, crush the cane and squeeze out the raw green juice. Spent cane (bagasse) is piled aside.", "Interpretive"),
    ("Sorghum — The Cooker", "The evaporating pan: a long shallow pan over open fire where raw juice becomes golden syrup. The cook skims green foam and reads doneness by how the syrup sheets off a wooden paddle.", "Interpretive"),
    ("Loved Your Visit? Leave a Review", "Scan with your phone's camera to leave a Google review. Thank you from the herd — Monroe, Tennessee · woaksyarns.com", "Review"),
]


def card(slug: str, title: str, tag: str) -> str:
    png = f"assets/{slug}.png"
    pdf = f"assets/{slug}.pdf"
    t = html.escape(title)
    if not (ASSETS / f"{slug}.png").exists():
        return ""  # skip missing silently; report is separate
    return f'''      <li class="card">
        <a class="thumb" href="{png}" target="_blank" rel="noopener" aria-label="Open {t} preview">
          <img src="{png}" alt="{t}" loading="lazy">
        </a>
        <div class="meta">
          <p class="cap">{t}</p>
          <span class="tag">{html.escape(tag)}</span>
        </div>
        <div class="dl">
          <a class="btn" href="{pdf}" download>PDF ↓</a>
          <a class="btn ghost" href="{png}" download>PNG ↓</a>
        </div>
      </li>'''


def text_card(title: str, body: str, tag: str) -> str:
    return f'''      <li class="card text">
        <p class="cap">{title}</p>
        <p class="body">{body}</p>
        <span class="tag">{tag}</span>
      </li>'''


def section(title: str, note: str, items) -> str:
    cards = "\n".join(c for c in (card(*it) for it in items) if c)
    return f'''  <section>
    <h2>{html.escape(title)}</h2>
    <p class="sec-note">{html.escape(note)}</p>
    <ul class="grid">
{cards}
    </ul>
  </section>'''


def build() -> str:
    secs = "\n".join(section(t, n, items) for (t, n, items) in SECTIONS)
    tcards = "\n".join(text_card(*t) for t in TEXT_CARDS)
    text_sec = f'''  <section>
    <h2>Info, Rules &amp; Interpretive Text</h2>
    <p class="sec-note">Text-only signs — printable straight from the page.</p>
    <ul class="grid">
{tcards}
    </ul>
  </section>'''
    trail_link = '''  <section>
    <h2>Heritage Trail (Live)</h2>
    <p class="sec-note">The interactive interpretive trail, posted along the forest paths.</p>
    <ul class="grid">
      <li class="card text">
        <p class="cap">Heritage Trail Signs</p>
        <p class="body">The full set of interpretive signs along the Tapestry Acres Heritage Trail — history, flora, and farm heritage stops.</p>
        <div class="dl"><a class="btn" href="https://trashpanda62.github.io/plans/trails/" target="_blank" rel="noopener">Open trail ↗</a></div>
        <span class="tag">Trail</span>
      </li>
    </ul>
  </section>'''
    return TEMPLATE.replace("{{SECTIONS}}", secs + "\n" + trail_link + "\n" + text_sec)


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tapestry Acres — Signage Dashboard</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🪧</text></svg>">
<style>
  :root{
    --ink:#2b2620; --soft:#6b6258; --line:#ded4c4; --line-soft:#ece3d5;
    --sage:#7a8b5a; --sage-deep:#566a3c; --clay:#b9824f; --clay-deep:#9c6a3c;
    --parchment:#f3efe7; --ground:#f7f2e8; --card:#fffdf8; --gold:#c69a4c;
    --serif:"Georgia","Palatino Linotype",Palatino,"Book Antiqua",serif;
    --sans:"Segoe UI",-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;
    --shadow:0 10px 30px -18px rgba(70,50,28,.5);
    --ease:cubic-bezier(.22,.61,.36,1);
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html,body{margin:0;}
  body{
    font-family:var(--sans); color:var(--ink); line-height:1.5;
    background:
      radial-gradient(1200px 500px at 15% -8%, rgba(122,139,90,.14), transparent 60%),
      radial-gradient(1000px 460px at 100% 0%, rgba(185,130,79,.12), transparent 55%),
      var(--ground);
    background-attachment:fixed;
  }
  .page{max-width:1120px; margin:0 auto; padding:26px 26px 80px;}

  .home{display:inline-flex; align-items:center; gap:7px; font-size:13px; font-weight:600;
    color:var(--soft); text-decoration:none; padding:7px 14px 7px 11px;
    border:1px solid var(--line); border-radius:999px; background:var(--card); margin-bottom:30px;
    transition:color .15s var(--ease), border-color .15s var(--ease), transform .15s var(--ease);}
  .home:hover{color:var(--sage-deep); border-color:var(--sage); transform:translateX(-2px);}

  header{position:relative; padding:6px 0 26px; margin-bottom:8px;
    border-bottom:2px solid transparent;
    border-image:linear-gradient(90deg,var(--sage),var(--clay) 70%,transparent) 1;}
  header img.logo{display:block; max-height:78px; width:auto; margin:0 0 18px;}
  .eyebrow{font-size:11px; letter-spacing:3px; text-transform:uppercase; color:var(--clay-deep);
    font-weight:800; margin:0 0 10px;}
  h1{font-family:var(--serif); font-weight:700; font-size:clamp(32px,6vw,50px);
    line-height:1.02; letter-spacing:-.6px;}
  .intro{font-size:14.5px; color:var(--soft); margin:16px 0 6px; max-width:62ch; line-height:1.65;}

  section{margin-top:14px;}
  h2{font-family:var(--serif); font-weight:700; font-size:clamp(21px,4vw,28px); color:var(--sage-deep);
    margin:46px 0 3px; letter-spacing:-.3px; display:flex; align-items:center; gap:12px;}
  h2::after{content:""; flex:1; height:1px; background:linear-gradient(90deg,var(--line),transparent);}
  .sec-note{font-size:12.5px; color:var(--soft); margin:0 0 20px;}

  .grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(232px,1fr)); gap:20px;
    list-style:none;}

  .card{background:var(--card); border:1px solid var(--line); border-radius:14px; padding:12px 12px 14px;
    display:flex; flex-direction:column; transition:border-color .16s var(--ease),
    box-shadow .2s var(--ease), transform .16s var(--ease);}
  .card:hover{border-color:#cdbf9f; box-shadow:var(--shadow); transform:translateY(-3px);}

  .thumb{display:block; border-radius:9px; overflow:hidden; background:var(--parchment);
    border:1px solid var(--line-soft); aspect-ratio:4/5; position:relative;}
  .thumb img{width:100%; height:100%; object-fit:contain; display:block; padding:6px;}
  .thumb::after{content:"⤢ open"; position:absolute; right:8px; bottom:8px; font-size:10px; font-weight:700;
    letter-spacing:.4px; color:#fff; background:rgba(40,32,22,.78); padding:3px 8px; border-radius:999px;
    opacity:0; transition:opacity .18s var(--ease);}
  .card:hover .thumb::after{opacity:1;}

  .meta{display:flex; align-items:flex-start; justify-content:space-between; gap:8px; margin:12px 2px 0;}
  .cap{font-family:var(--serif); font-weight:700; font-size:15px; color:var(--ink); line-height:1.25;}
  .tag{flex:none; font-size:9.5px; font-weight:800; letter-spacing:.6px; text-transform:uppercase;
    color:var(--clay-deep); background:var(--parchment); border:1px solid #e6dcc8;
    border-radius:999px; padding:3px 9px; margin-top:1px; white-space:nowrap;}

  .dl{display:flex; gap:8px; margin:12px 2px 0;}
  .btn{flex:1; text-align:center; font-size:12px; font-weight:700; letter-spacing:.3px;
    text-decoration:none; padding:8px 10px; border-radius:9px;
    background:var(--sage-deep); color:#fff; border:1px solid var(--sage-deep);
    transition:filter .15s var(--ease), transform .12s var(--ease);}
  .btn:hover{filter:brightness(1.08); transform:translateY(-1px);}
  .btn.ghost{background:transparent; color:var(--sage-deep); border-color:var(--line);}
  .btn.ghost:hover{border-color:var(--sage); background:var(--card);}

  .card.text{background:linear-gradient(180deg,var(--card),#fbf7ee); justify-content:flex-start;}
  .card.text .cap{margin-bottom:8px;}
  .card.text .body{font-size:12.5px; color:var(--soft); line-height:1.55;}
  .card.text .tag{align-self:flex-start; margin-top:12px;}
  .card.text .dl{margin-top:12px;}

  footer{margin-top:60px; padding-top:18px; border-top:1px solid var(--line);
    font-size:11.5px; color:var(--soft); display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;}
  footer .mark{font-family:var(--serif); font-style:italic; color:var(--sage-deep);}

  @media (max-width:560px){
    .grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:14px;}
    .page{padding:20px 16px 64px;}
  }
</style>
</head>
<body>
<div class="page">
  <a class="home" href="https://trashpanda62.github.io/plans/"><span aria-hidden="true">←</span> The Map</a>
  <header>
    <img class="logo" src="assets/logo.png" alt="Tapestry Acres logo">
    <p class="eyebrow">Tapestry Acres</p>
    <h1>Signage Dashboard</h1>
    <p class="intro">Every sign, ad, flyer, and brand asset for the farm — gathered in one place. Each item has a preview and downloads as both a print-ready <strong>PDF</strong> and a <strong>PNG</strong>.</p>
  </header>

{{SECTIONS}}

  <footer>
    <span class="mark">Signage Dashboard</span>
    <span>Tapestry Acres · Dale Hollow · Monroe, TN</span>
  </footer>
</div>
</body>
</html>
'''


if __name__ == "__main__":
    out = HERE / "index.html"
    out.write_text(build(), encoding="utf-8")
    print("wrote", out)
