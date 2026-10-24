# MoveWise: code explanation (for judges and for me)

## 1. The big picture
MoveWise is one Streamlit app (`app.py`) plus one small calculation file (`eco.py`).
Streamlit re-runs `app.py` from top to bottom every time someone taps something. The page to show is stored in `st.session_state["page"]`.

```
app.py   screens, data loading, accounts, storage        eco.py   all environmental maths + EcoGuide tips (no Streamlit)
tests/   test_eco.py (maths) + test_app_pages.py (every page)
```
I kept the maths in `eco.py` on purpose: it can be tested without a browser, and it is the part judges will question.

## 2. How the app is organised (top to bottom in app.py)
1. Arabic/English dictionary and `tr()`: every text passes through it.
2. Demo data (26 places, only used offline) and calculation functions (distance, availability estimate, score, cost).
3. Storage and accounts: `load_json` / `save_json`, `mob_get` / `mob_add` (the Green Dashboard records).
4. OpenStreetMap loaders for parking (`osm_parkings`) and EV chargers (`osm_chargers`), refreshed every 30 minutes.
5. Look: one palette (`BRAND`), light and dark themes, CSS.
6. Callbacks (`cb_...`): what happens when a button is pressed.
7. Pages (`page_...`) and the router at the bottom, with the bottom bar (5 sections) and tabs (`subnav`).

## 3. The features and the functions behind them
| Feature | Main functions | How it works |
|---|---|---|
| Smart picks (Home) | `smart_picks`, `score_parts`, `reason`, `pick_card` | Skip full places and anything outside the budget, type or distance chosen. Rank the rest by a visible score: availability + data reliability + distance + price. Each card shows the points and a sentence explaining the pick. Not AI. |
| Destination search | `cb_destination`, `cb_set_area` | Sets the point distances are measured from (our own area list, else Nominatim/OpenStreetMap). |
| EcoImpact | `eco.eco_impact`, `ei_compute`, `page_ecoimpact` | extra km × journeys × weeks → km; km × L/100 ÷ 100 → litres; litres × kg CO₂ per litre → CO₂. "Avoided" = total × the % the user chooses (a what-if). |
| EcoTwin | `eco.twin_scenario`, `eco.twin_curve`, `page_ecotwin` | drivers × extra km × days = before; before × (1 − %) = after; the difference is avoided. Plotly bar charts compare before and after; a line chart shows CO₂ avoided at every % |
| Green Dashboard | `mob_add`, `mob_get`, `page_mobility` | Shows only records the user saved (EcoImpact, EcoTwin, timed sessions, cost estimates, car spots). Empty until then. |
| EcoGuide | `eco.TIPS`, `eco.search_tips`, `eco.personal_tip`, `page_ecoguide` | A fixed list of reviewed tips; keyword search; one "tip for you" chosen by simple rules from what the user has done. |
| Where did I park? | `car_resolve`, `cb_car_save`, `geocode_uae`, `mini_map`, `page_car` | Location from GPS, a parking place, an area name, or coordinates (checked to be inside the UAE). Saves floor/zone, note and the time automatically. Shows a map and a Google Maps walking-directions link. |
| EV charging | `osm_to_charger`, `ev_quality`, `ev_speed_class`, `page_ev` | Reads plug types, per-plug kW, price text from OpenStreetMap tags. Every detail is labelled "listed" or "not available"; speed class is labelled "estimated". |
| Timer | `cb_timer_start/stop`, `timer_clock` | Uses real timestamps. The reminder is checked every second while the page is open. Stopped sessions are saved. |
| Cost calculator | `estimate_cost`, `page_calc` | rate × (time − free minutes) ÷ 60, limited by an optional daily cap, plus an optional one-off fee. |

## 4. The environmental assumptions (be ready to say these)
* CO₂ per litre: petrol 2.35 kg and diesel 2.69 kg (US EPA and Natural Resources Canada).
* Electricity: 0.401 kg CO₂ per kWh, read from a third-party table citing DEWA 2020. **Not independently verified.** Editable.
* Litres per 100 km presets (6.5 / 8.5 / 12 / 7 / 4.5 and 18 kWh) are typical round numbers I chose. Editable.
* The % reduction is the user's own hypothetical. I do not know the real figure for the UAE.
* Not modelled: real traffic, how many parking spaces exist, how drivers behave, different cars for different drivers.

## 5. Libraries and data sources
Streamlit (screens), Plotly (interactive charts), pydeck (maps, comes with Streamlit), OpenStreetMap Overpass API (parking and charger locations), Nominatim (typed place → coordinates), streamlit-geolocation (the GPS button), Authlib/httpx (optional Google sign-in, switched off). No paid API and no API keys.

## 6. Suggested demo order (about 5 minutes)
1. Home: type a destination → smart picks → open "Why this pick" and read the points.
2. EcoTwin: load the 100 drivers / 2 km / 50% example → 200 km → 100 km. Change the numbers, show the charts update. Say clearly: hypothetical.
3. EcoImpact: show the step-by-step calculation and the editable assumptions.
4. Park a car: Timer with a reminder, then Where did I park? (floor + note + map + directions).
5. EV page: point out "listed" vs "not available" labels.
6. Green Dashboard: show that it only contains what was saved. Mention guest vs account.

## 7. Likely judge questions
* **Is availability live?** No. It is a typical-busyness estimate or a driver report, always labelled.
* **Is the CO₂ saving real?** No, it is an estimate/what-if. The formula, factors and sources are on screen. The reduction % is chosen by the user.
* **Where do the numbers come from?** EPA and Natural Resources Canada for fuel; a DEWA-based listing for electricity (unverified); typical consumption values I chose.
* **Is it AI?** No. The score, Parky and EcoGuide are rule-based. I built it with help from AI tools and can explain every part.
* **What data do you store?** Email, a salted hash of the password, saved places, car spot and records you save. Guests store nothing on the server.
* **What would you do next?** Measure real behaviour with a pilot (e.g. a survey of how long people search for parking), verify the electricity factor with DEWA, add live availability only if a real data source exists.

## 8. Testing checklist
`python -m unittest discover -s tests -v` (76 tests), then open the real app and check: phone layout, dark mode, Arabic, GPS permission, a signed-in account saving across visits.
