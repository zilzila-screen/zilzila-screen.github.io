# Zilzila Screen

Rapid seismic vulnerability triage for the Tashkent building stock.

**[Open the tool →](https://raasulbkh.github.io/zilzila-screen/)**

Created by **Ravshanbek Karomatov**.

---

## What it does

Tashkent has roughly 209,000 dwellings. Nobody can commission an engineering
assessment for all of them, and a 2026 study found that about 4% of the housing
stock would suffer severe damage in a repeat of the 1966 earthquake — mostly
brick and adobe buildings predating it. The problem is not *can we assess a
building*, it is *which buildings do we assess first*.

Zilzila Screen answers that. A surveyor screens a building in about a minute
from what is visible at street level, and the tool ranks the resulting survey
list by retrofit priority.

It has two views:

- **Survey** — screen one building. Structural type sets a base EMS-98
  vulnerability class, then period of construction, height, ground type and
  observed defects shift it. The expected damage state is drawn, not just
  described.
- **Portfolio** — the programme view. Risk distribution, exposure by district,
  a structural type by period matrix and a ranked retrofit queue.

## Method

Screening follows the European Macroseismic Scale (EMS-98). Structural type
gives a base vulnerability class on the A–F scale; modifiers shift it; the
shifted class is read against the EMS-98 damage distributions at MSK-64
intensity VIII, which corresponds to a repeat of the 1966 Tashkent earthquake.

The tool reports the **worst credible damage grade, not the expected one**.
EMS-98 gives a distribution of outcomes per vulnerability class rather than a
single result, and the conservative tail is the right posture for triage: a
Priority 1 result means commission an engineering assessment, and the
assessment refines it.

The hazard context in the title block comes from a Gutenberg–Richter recurrence
analysis of the 1970–2026 USGS instrumental catalogue for a 300 km zone around
Tashkent: b = 1.29, an M ≥ 6.0 earthquake roughly every 13 years and a
475-year magnitude of 7.09.

## Limits

This is a screening heuristic on visible attributes. It cannot see
reinforcement, foundations or material strength, and it is not a structural
assessment or a site-specific hazard study. The weights are a defensible
calibration of the EMS-98 class structure, not a published lookup table;
validating them against observed damage — the 1966 isoseismal data would be the
obvious test set — is the clear next step.

## Running it

A single static HTML page with no build step, no dependencies and no backend.
Survey records are saved in the viewer's browser.

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

To rebuild `index.html` after editing the source in `src/`:

```sh
cd src && python3 build_site.py
```

## Data

The portfolio opens with 40 seeded survey records across 11 Tashkent districts,
generated to demonstrate the view and labelled as such in the page. Buildings
added from the Survey view are counted alongside them.
