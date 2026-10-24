# MoveWise
**Move Smarter. Live Greener.**

A smart-mobility and sustainability app for Dubai, Sharjah and Ajman, built with Python and Streamlit.
Built with help from AI tools. The author can explain how it works (see `CODE_EXPLANATION.md`).

## What it does
| Section | Features |
|---|---|
| **Home** | Destination search, smart picks with reasons, feature tiles, a clearly-labelled hypothetical eco example, your own saved numbers, quick tools |
| **Parking** | Search, map, nearby, saved places, community reports, family-friendly vote, availability estimate |
| **EV** | Charging stations with plug types, per-plug power, price when listed, filters, and a "listed / not available" label on every detail |
| **Eco** | **EcoImpact** calculator, **EcoTwin** simulator (before/after charts), **EcoGuide** tips |
| **Mobility** | **Green Dashboard** (your saved estimates, car spot, timed sessions), **Where did I park?** (GPS, parking place, area or coordinates; floor, note, date/time, map, directions), Parking timer with reminder, Cost calculator with additional fee, Profile |

Arabic / English and email login (or guest mode) are kept from ParkFinder UAE.

## Run it
```
py -m pip install -r requirements.txt
py -m streamlit run app.py
```
Deploy on Streamlit Community Cloud: put **all** of these in the GitHub repo: `app.py`, `eco.py`, `requirements.txt`, `hero.jpg`, `.streamlit/config.toml`.

## Test it
```
python -m unittest discover -s tests -v
```
* `tests/test_eco.py`: the CO₂ maths (for example 100 drivers × 2 km × 50% = 100 km avoided).
* `tests/test_app_pages.py`: runs every page of the app in English and Arabic, light and dark, and checks the features (saving a car spot, timer reminder, cost, EV filters, dashboard, navigation...). It uses a small stand-in for Streamlit (`tests/fake_streamlit.py`), so it checks behaviour, **not appearance**. Always also open the real app and click through it.

## What is real, estimated or demo (please read)
* **Parking locations** are real places mapped in OpenStreetMap. **Availability is not live**: it is a typical-busyness estimate for the day and time, or a driver report, and is always labelled. There are no live sensors.
* If OpenStreetMap cannot be reached, 26 **demo** places are shown and labelled as demo data.
* **EV chargers** come from OpenStreetMap volunteers. Plug types, power and price are shown only when a mapper listed them. **Live free/busy status is never shown** (no free public source exists). "Speed class" is our own plain-words label worked out from the listed kW and is marked *estimated*.
* **EcoImpact and EcoTwin are estimates and what-ifs, never measurements.** The formulas and every factor are shown on screen and can be changed (see `eco.py`):
  * fuel = distance × litres per 100 km ÷ 100; CO₂ = fuel × kg CO₂ per litre
  * petrol 2.35 kg/L (Natural Resources Canada and US EPA agree), diesel 2.69 kg/L (US EPA)
  * electricity 0.401 kg/kWh: the UAE figure was read from a third-party table that cites DEWA (2020) and **we could not check it against DEWA's own report**, so it is clearly marked and editable
  * consumption presets (litres per 100 km) are typical round numbers chosen for this project, not measurements
* The "reduction %" in EcoTwin is chosen by the user. MoveWise does not know the real figure.
* The Green Dashboard only shows what the user saved. Nothing is pre-filled or invented.

## Privacy and storage
Accounts keep a salted, hashed password. Saved places, car spot and dashboard records are stored per email in small JSON files under `user_data/`. Guests keep everything in the current visit only. Location is requested only when a location button is tapped. No API keys are needed. On free Streamlit hosting these files can be lost when the app restarts.

## Known limits
* Parking availability is an estimate; distances are straight-line.
* The timer reminder only works while the page is open in the browser (a web page cannot ring a closed phone).
* EcoGuide and Parky are rule-based, not AI.
* New Eco / Dashboard / EV text is in English first; the main labels and navigation are translated to Arabic, but longer new sentences are not yet.
