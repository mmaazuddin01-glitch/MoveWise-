"""MoveWise environmental maths and EcoGuide tips.   (plain Python, no Streamlit, so it can be tested on its own)

HONEST NOTES (tell the judges):
 - Everything here is an ESTIMATE from a simple formula. Nothing is measured from real cars or real UAE traffic.
 - Formula for a petrol/diesel car:   litres = km x (litres per 100 km) / 100        CO2 (kg) = litres x (kg CO2 per litre)
 - Formula for an electric car:       kWh    = km x (kWh per 100 km) / 100          CO2 (kg) = kWh x (kg CO2 per kWh of grid electricity)
 - The "avoided" numbers are WHAT-IF scenarios: avoided = total x (reduction % chosen by the user). They are not proof of savings.
 - Fuel consumption presets are typical round numbers chosen for this project. The user can overwrite every number.
"""

# ------------------------------------------------------------------ documented, editable factors ----
# kg of CO2 released by burning one litre of fuel.
#   Petrol : 0.002347 t CO2e per litre  - Natural Resources Canada (NRCan) greenhouse-gas calculator references.
#            8,887 g CO2 per US gallon  - US EPA "Greenhouse Gases Equivalencies Calculator" (= 2.348 kg per litre). The two agree.
#   Diesel : 10,180 g CO2 per US gallon - US EPA, same page (= 2.689 kg per litre).
FUEL_FACTORS = {"petrol": 2.35, "diesel": 2.69}

# kg of CO2 per kWh of grid electricity (only used for electric cars).
# 0.401 is the "generation factor" listed for the UAE (year 2020, source quoted as the DEWA sustainability report 2021) on the
# third-party table oer.enviraj.com. We could not check it against DEWA's own report, so it is an editable starting point.
GRID_FACTOR_DEFAULT = 0.401

# Typical consumption numbers (ASSUMPTIONS, editable): litres per 100 km, or kWh per 100 km for electric.
VEHICLES = {
    "Small petrol car": {"fuel": "petrol", "per100": 6.5},
    "Petrol sedan": {"fuel": "petrol", "per100": 8.5},
    "Petrol SUV": {"fuel": "petrol", "per100": 12.0},
    "Diesel car": {"fuel": "diesel", "per100": 7.0},
    "Hybrid car": {"fuel": "petrol", "per100": 4.5},
    "Electric car": {"fuel": "electric", "per100": 18.0},
}
DEFAULT_VEHICLE = "Petrol sedan"

PERIODS = {"One day": 1, "One week": 7, "One month (30 days)": 30, "One year (365 days)": 365}


def _check(name, value, minimum=0.0, maximum=None):
    """Reject text, negative or absurd numbers so a typo can never produce a nonsense result."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError("%s must be a number." % name)
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError("%s must be a real number." % name)
    if value < minimum:
        raise ValueError("%s cannot be less than %s." % (name, minimum))
    if maximum is not None and value > maximum:
        raise ValueError("%s cannot be more than %s." % (name, maximum))
    return value


def factor_for(fuel, grid_factor=GRID_FACTOR_DEFAULT):
    """kg CO2 per litre (petrol/diesel) or per kWh (electric)."""
    return grid_factor if fuel == "electric" else FUEL_FACTORS[fuel]


def unit_for(fuel):
    return "kWh" if fuel == "electric" else "litres"


def trip_emissions(km, fuel, per100, factor):
    """One calculation used everywhere: distance -> energy used -> CO2.  Returns (energy, co2_kg)."""
    km = _check("Distance", km)
    per100 = _check("Consumption", per100, 0.0, 100.0)
    factor = _check("Emission factor", factor, 0.0, 10.0)
    energy = km * per100 / 100.0
    return energy, energy * factor


# ------------------------------------------------------------------------------- EcoImpact ----
def eco_impact(extra_km_per_journey, journeys_per_week, weeks, fuel, per100, factor, reduction_pct):
    """EcoImpact calculator. 'extra km' = the extra distance driven on one journey, e.g. circling for a parking space.

    Returns a dict with the total extra distance, the energy used, the CO2, and the what-if saving for the chosen
    reduction percentage."""
    extra = _check("Extra distance per journey", extra_km_per_journey, 0.0, 1000.0)
    journeys = _check("Journeys per week", journeys_per_week, 0.0, 1000.0)
    weeks = _check("Number of weeks", weeks, 0.0, 520.0)
    pct = _check("Reduction", reduction_pct, 0.0, 100.0)
    total_km = extra * journeys * weeks
    energy, co2 = trip_emissions(total_km, fuel, per100, factor)
    share = pct / 100.0
    return {"total_km": total_km, "energy": energy, "unit": unit_for(fuel), "co2_kg": co2, "reduction_pct": pct,
            "avoided_km": total_km * share, "avoided_energy": energy * share, "avoided_co2_kg": co2 * share,
            "remaining_km": total_km * (1 - share), "remaining_co2_kg": co2 * (1 - share), "journeys_total": journeys * weeks}


# --------------------------------------------------------------------------------- EcoTwin ----
def twin_scenario(drivers, extra_km_per_driver_per_day, reduction_pct, days, fuel, per100, factor):
    """EcoTwin: the 'digital twin' of a group of drivers searching for parking, before and after a hypothetical improvement.

    The example from the brief: 100 drivers x 2 km = 200 km. A 50% what-if reduction avoids 100 km."""
    drivers = _check("Number of drivers", drivers, 0.0, 10_000_000.0)
    extra = _check("Extra kilometres per driver per day", extra_km_per_driver_per_day, 0.0, 1000.0)
    pct = _check("Reduction", reduction_pct, 0.0, 100.0)
    days = _check("Number of days", days, 1.0, 3650.0)
    before_km = drivers * extra * days
    after_km = before_km * (1 - pct / 100.0)
    e_before, co2_before = trip_emissions(before_km, fuel, per100, factor)
    e_after, co2_after = trip_emissions(after_km, fuel, per100, factor)
    return {"drivers": drivers, "days": days, "reduction_pct": pct, "unit": unit_for(fuel),
            "before_km": before_km, "after_km": after_km, "avoided_km": before_km - after_km,
            "before_energy": e_before, "after_energy": e_after, "avoided_energy": e_before - e_after,
            "before_co2_kg": co2_before, "after_co2_kg": co2_after, "avoided_co2_kg": co2_before - co2_after}


def twin_curve(drivers, extra_km, days, fuel, per100, factor, steps=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)):
    """What-if table: how much CO2 would be avoided at each reduction percentage (used for the line chart)."""
    return [(p, twin_scenario(drivers, extra_km, p, days, fuel, per100, factor)["avoided_co2_kg"]) for p in steps]


# ---------------------------------------------------------------------------- formatting ----
def fmt_amount(x, digits=1):
    """1234.5 -> '1,234.5'   (whole numbers lose the .0)"""
    text = ("{:,.%df}" % digits).format(x)
    return text[:-2] if digits and text.endswith(".0") else text


def fmt_co2(kg):
    """Show tonnes for big numbers, kilograms otherwise."""
    return ("%s t CO₂" % fmt_amount(kg / 1000.0, 2)) if kg >= 1000 else ("%s kg CO₂" % fmt_amount(kg, 1))


# ------------------------------------------------------------------------------- EcoGuide ----
# A fixed, reviewed list of practical tips. Rule-based, NOT AI. No numbers are claimed here: use the calculators for numbers.
TIPS = [
    {"topic": "Less driving", "icon": "🧭", "title": "Choose the parking before you leave",
     "text": "Pick a car park first, then drive straight to it. Searching street by street is where most unnecessary kilometres come from.",
     "why": "Circling adds distance, fuel and emissions without taking you any closer to your destination.", "keys": "circling search before plan drive"},
    {"topic": "Less driving", "icon": "🔁", "title": "Combine errands into one trip",
     "text": "Group nearby stops into one journey instead of several short ones, and park once if the stops are within walking distance.",
     "why": "Short cold-start trips and repeated parking searches are inefficient. One trip means one search.", "keys": "combine trips errands short walk"},
    {"topic": "Less driving", "icon": "🚶", "title": "Park a little further and walk",
     "text": "A free or cheaper car park 5 to 10 minutes' walk away is often easier to find than one right at the door.",
     "why": "Less competition for the closest spots means less circling. MoveWise shows walking time on every card.", "keys": "walk further distance cheaper free"},
    {"topic": "Parking smarter", "icon": "⏰", "title": "Check the typical busyness for your time",
     "text": "Open a parking place's Details page to see its weekly busyness pattern and the quietest hour today. Remember it is an estimate, not a live count.",
     "why": "Arriving at a quieter time makes finding a space faster.", "keys": "busy time quiet pattern hour peak"},
    {"topic": "Parking smarter", "icon": "📣", "title": "Share a quick parking report",
     "text": "If a place is almost full or full when you arrive, report it. Reports expire after two hours, so they stay fresh.",
     "why": "Driver reports are the only 'now' information MoveWise has, so each one helps the next driver.", "keys": "report community full available"},
    {"topic": "Parking smarter", "icon": "💾", "title": "Save the places you use often",
     "text": "Save your regular car parks, then compare them quickly next time. Use 'Where did I park?' so you never wander looking for your car.",
     "why": "Knowing where you are going and where you left the car removes needless driving and walking around.", "keys": "save favourite car find where"},
    {"topic": "EV charging", "icon": "🔌", "title": "Charge where you already park",
     "text": "If you drive an electric car, choose a car park that has a charger and charge while you shop or work, instead of making a special trip.",
     "why": "Charging while parked uses time you would spend anyway, so no extra kilometres are needed.", "keys": "ev charging electric charger plug"},
    {"topic": "EV charging", "icon": "📋", "title": "Check plug type and power before you go",
     "text": "Look at the plug type and kW on the EV page, and confirm with the operator's app. Volunteers add this data, so it can be missing.",
     "why": "A station with the wrong plug means a wasted trip.", "keys": "plug type kw speed fast connector"},
    {"topic": "EV charging", "icon": "⚡", "title": "Match charging speed to how long you will stay",
     "text": "Staying for hours? A slower charger is enough. Only passing through? Look for a faster one.",
     "why": "It avoids queueing at fast chargers when you do not need them.", "keys": "fast slow speed time stay queue"},
    {"topic": "Planning journeys", "icon": "🕒", "title": "Travel outside the busiest hours when you can",
     "text": "Moving a trip by even 30 minutes can mean less traffic and an easier parking search.",
     "why": "Less congestion means shorter, smoother journeys.", "keys": "time traffic rush peak hour"},
    {"topic": "Planning journeys", "icon": "🚇", "title": "Consider public transport for the busiest destinations",
     "text": "For places where parking is hard to find, check whether the Metro, a bus or a ride share is simpler for that trip.",
     "why": "Not driving at all avoids the parking search entirely.", "keys": "metro bus public transport train ride share"},
    {"topic": "Planning journeys", "icon": "⚙️", "title": "Keep your car in good shape",
     "text": "Correct tyre pressure and regular servicing help a car use fuel as efficiently as it can.",
     "why": "A well-maintained car uses less fuel for the same distance.", "keys": "tyre tire pressure service fuel efficient"},
]
TOPICS = ["All"] + sorted({t["topic"] for t in TIPS}, key=lambda t: [x["topic"] for x in TIPS].index(t))


def tips_for(topic):
    return [t for t in TIPS if topic == "All" or t["topic"] == topic]


STOP_WORDS = {"the", "and", "for", "you", "your", "can", "how", "what", "which", "should", "use", "with", "that", "this", "are", "from",
              "when", "where", "does", "have", "get", "any", "not", "but", "into", "than", "then", "will", "would", "could", "about"}


def search_tips(question):
    """Very simple keyword match for the EcoGuide question box. Whole words only; keywords and titles count more than body text."""
    words = {w for w in "".join(c.lower() if c.isalnum() else " " for c in str(question)).split() if len(w) > 2 and w not in STOP_WORDS}
    scored = []
    for t in TIPS:
        key_words = set(t["keys"].split()) | set(t["title"].lower().replace(",", " ").split()) | {t["topic"].lower()}
        body_words = set("".join(c.lower() if c.isalnum() else " " for c in t["text"] + " " + t["why"]).split())
        points = sum(3 for w in words if w in key_words) + sum(1 for w in words if w in body_words)
        if points:
            scored.append((points, t))
    scored.sort(key=lambda s: -s[0])
    return [t for _, t in scored[:3]]


def personal_tip(has_eco_result, has_saved_parking, has_car_spot):
    """One tip chosen by simple rules from what the person has actually done in the app (never invented statistics)."""
    if not has_eco_result:
        return TIPS[0], "Run the EcoImpact calculator first, then the tips can match your own numbers."
    if not has_saved_parking:
        return TIPS[5], "You have not saved any parking places yet."
    if not has_car_spot:
        return TIPS[5], "You can also save where you parked, so you never search for your car."
    return TIPS[3], "You already use the saved places, so the next gain is choosing the quietest time."
