"""Sample venue catalog for DEMO MODE (no Google Places key configured).

Every entry is a real, well-known place (so nothing is fabricated), but in
demo mode its rating, hours, and price are SAMPLE values — the API labels the
whole catalog as demo data and the UI shows a demo badge. Never misrepresent
these as live, verified results.
"""
from __future__ import annotations

from app.schemas import Venue

# tag vocabulary used by the category matcher:
# dinner, brunch, casual, upscale, vegetarian, vegan, gluten-free, dairy-free,
# cocktail, casual drinks, beer, live music, concerts, comedy, dancing,
# games, bowling, escape rooms, outdoor, dessert, coffee, hotel, latin, italian


def _v(id, name, address, lat, lng, tags, price_level, rating=4.5, hours=None, cost=None) -> dict:
    return {
        "id": id, "name": name, "address": address, "lat": lat, "lng": lng,
        "tags": tags, "price_level": price_level, "rating": rating,
        "hours": hours, "cost": cost,
    }


_CATALOG: dict[str, list[dict]] = {
    "denver": [
        # --- dinner ---
        _v("den-01", "Denver Biscuit Company", "3237 E Colfax Ave, Denver, CO", 39.7403, -104.9489,
           ["dinner", "brunch", "casual"], 2, 4.6, cost=18),
        _v("den-02", "Watercourse Foods", "837 E 17th Ave, Denver, CO", 39.7433, -104.9766,
           ["dinner", "casual", "vegetarian", "vegan", "gluten-free"], 2, 4.5, cost=20),
        _v("den-03", "City, O' City", "206 E 13th Ave, Denver, CO", 39.7371, -104.9846,
           ["dinner", "casual", "vegetarian", "vegan"], 2, 4.4, cost=20),
        _v("den-04", "Linger", "2030 W 30th Ave, Denver, CO", 39.7622, -105.0079,
           ["dinner", "upscale", "vegetarian", "gluten-free", "eclectic"], 3, 4.5, cost=42),
        _v("den-05", "Root Down", "1600 W 33rd Ave, Denver, CO", 39.7629, -105.0083,
           ["dinner", "upscale", "vegetarian", "gluten-free", "casual"], 3, 4.6, cost=38),
        _v("den-06", "Work & Class", "2500 Larimer St, Denver, CO", 39.7585, -104.9867,
           ["dinner", "casual", "latin"], 2, 4.4, cost=28),
        _v("den-07", "Tavernetta", "1948 Market St, Denver, CO", 39.7544, -104.9932,
           ["dinner", "upscale", "italian", "romantic"], 3, 4.6, cost=55),
        _v("den-08", "Snooze, an A.M. Eatery", "2262 Larimer St, Denver, CO", 39.7534, -104.9922,
           ["dinner", "brunch", "casual", "gluten-free", "vegetarian"], 2, 4.4, cost=20),
        # --- cocktail bars ---
        _v("den-09", "Williams & Graham", "3160 Tejon St, Denver, CO", 39.7648, -105.0106,
           ["cocktail", "upscale"], 3, 4.7, cost=24),
        _v("den-10", "Death & Co Denver", "1280 25th St, Denver, CO", 39.7597, -105.0054,
           ["cocktail", "upscale", "trendy"], 3, 4.6, cost=26),
        _v("den-11", "The Green Russell", "1422 Larimer St, Denver, CO", 39.7489, -105.0002,
           ["cocktail", "casual drinks"], 3, 4.5, cost=22),
        # --- casual drinks ---
        _v("den-12", "Falling Rock Tap House", "1919 Blake St, Denver, CO", 39.7535, -104.9970,
           ["casual drinks", "beer"], 2, 4.5, cost=12),
        _v("den-13", "Great Divide Brewing Co", "2201 Arapahoe St, Denver, CO", 39.7540, -104.9893,
           ["casual drinks", "beer"], 2, 4.4, cost=12),
        _v("den-14", "Denver Beer Co", "1695 Platte St, Denver, CO", 39.7597, -105.0062,
           ["casual drinks", "beer", "outdoor"], 2, 4.4, cost=11),
        # --- games / arcade / bowling ---
        _v("den-15", "The 1UP Arcade Bar", "1925 Blake St, Denver, CO", 39.7534, -104.9968,
           ["games", "casual drinks"], 2, 4.6, cost=14),
        _v("den-16", "Punch Bowl Social", "650 15th St, Denver, CO", 39.7455, -104.9937,
           ["games", "bowling", "dinner", "casual drinks", "dancing"], 2, 4.4, cost=25),
        _v("den-17", "Bowlero Denver", "6800 Leetsdale Dr, Denver, CO", 39.7308, -104.9066,
           ["bowling", "casual drinks"], 2, 4.2, cost=18),
        # --- live music / concerts / comedy ---
        _v("den-18", "The Ogden Theatre", "935 E Colfax Ave, Denver, CO", 39.7395, -104.9765,
           ["live music", "concerts"], 2, 4.6, cost=35),
        _v("den-19", "Mission Ballroom", "4242 Wynkoop St, Denver, CO", 39.7743, -105.0028,
           ["concerts", "live music"], 3, 4.7, cost=55),
        _v("den-20", "Ophelia's Electric Soapbox", "1215 20th St, Denver, CO", 39.7560, -104.9949,
           ["dinner", "live music", "casual"], 3, 4.5, cost=30),
        _v("den-21", "Comedy Works Downtown", "1226 15th St, Denver, CO", 39.7477, -104.9995,
           ["comedy"], 2, 4.7, cost=28),
        # --- dancing ---
        _v("den-22", "Bar Standard", "1037 Broadway, Denver, CO", 39.7328, -104.9873,
           ["dancing", "energetic"], 2, 4.3, cost=15),
        _v("den-23", "Club Vinyl", "1082 Broadway, Denver, CO", 39.7334, -104.9876,
           ["dancing", "energetic"], 2, 4.2, cost=15),
        # --- escape rooms / outdoor / dessert / coffee ---
        _v("den-24", "EscapeWorks Denver", "2161 Lawrence St, Denver, CO", 39.7546, -105.0009,
           ["escape rooms"], 3, 4.6, cost=35),
        _v("den-25", "City Park", "2001 Colorado Blvd, Denver, CO", 39.7477, -104.9510,
           ["outdoor", "free"], 0, 4.7, cost=0),
        _v("den-26", "Little Man Ice Cream", "2620 16th St, Denver, CO", 39.7617, -105.0089,
           ["dessert", "outdoor"], 1, 4.6, cost=6),
        _v("den-27", "Voodoo Doughnut Denver", "1520 E Colfax Ave, Denver, CO", 39.7398, -104.9692,
           ["dessert"], 1, 4.4, cost=5),
        _v("den-28", "Huckleberry Roasters", "4301 Pecos St, Denver, CO", 39.7765, -105.0061,
           ["coffee"], 2, 4.8, cost=5),
    ],
    "boulder": [
        _v("bou-01", "The Sink", "1165 13th St, Boulder, CO", 40.0083, -105.2773,
           ["dinner", "casual", "burger", "gluten-free"], 2, 4.4, cost=18),
        _v("bou-02", "Foolish Craig's Cafe", "1611 Pearl St, Boulder, CO", 40.0193, -105.2758,
           ["dinner", "brunch", "casual", "vegetarian", "vegan"], 2, 4.5, cost=20),
        _v("bou-03", "Mountain Sun Pub & Brewery", "1535 Pearl St, Boulder, CO", 40.0190, -105.2746,
           ["casual drinks", "beer", "casual"], 2, 4.5, cost=12),
        _v("bou-04", "The Boulder Theatre", "2032 14th St, Boulder, CO", 40.0182, -105.2787,
           ["concerts", "live music", "comedy"], 2, 4.6, cost=35),
        _v("bou-05", "Escape Room Boulder", "1925 Central Ave, Boulder, CO", 40.0198, -105.2521,
           ["escape rooms"], 3, 4.6, cost=34),
        _v("bou-06", "Pearl Street Mall", "Pearl St, Boulder, CO", 40.0185, -105.2777,
           ["outdoor", "casual drinks", "dessert", "free"], 0, 4.7, cost=0),
    ],
    "austin": [
        _v("aus-01", "Franklin Barbecue", "900 E 11th St, Austin, TX", 30.2714, -97.7284,
           ["dinner", "casual", "bbq"], 2, 4.7, cost=25),
        _v("aus-02", "Home Slice Pizza", "1415 S Congress Ave, Austin, TX", 30.2454, -97.7496,
           ["dinner", "casual", "vegetarian"], 2, 4.6, cost=16),
        _v("aus-03", "Peche", "208 W 4th St, Austin, TX", 30.2666, -97.7474,
           ["cocktail", "romantic"], 3, 4.5, cost=22),
        _v("aus-04", "The Continental Club", "1315 S Congress Ave, Austin, TX", 30.2474, -97.7492,
           ["live music", "casual drinks"], 2, 4.7, cost=20),
        _v("aus-05", "Pinballz Arcade", "8940 Research Blvd, Austin, TX", 30.4177, -97.7124,
           ["games", "bowling"], 2, 4.5, cost=15),
        _v("aus-06", "Zilker Metropolitan Park", "2100 Barton Springs Rd, Austin, TX", 30.2669, -97.7731,
           ["outdoor", "free"], 0, 4.8, cost=0),
    ],
}

# Which venue tags satisfy which activity/category selections.
_CATEGORY_TAGS: dict[str, set[str]] = {
    "dinner": {"dinner", "brunch", "bbq", "burger", "latin", "italian", "eclectic"},
    "cocktail bars": {"cocktail"},
    "casual drinks": {"casual drinks", "beer"},
    "live music": {"live music"},
    "dancing": {"dancing"},
    "comedy shows": {"comedy"},
    "concerts": {"concerts"},
    "games & arcade bars": {"games"},
    "bowling": {"bowling"},
    "escape rooms": {"escape rooms"},
    "outdoor activities": {"outdoor"},
    "dessert or coffee": {"dessert", "coffee"},
    "something unexpected": {"eclectic", "surprise", "live music", "games"},
}

# Rough per-person cost guides used ONLY as estimates (never presented as fact).
_PRICE_PER_LEVEL = {0: 0, 1: 12, 2: 25, 3: 45, 4: 90}


def demo_cities() -> list[str]:
    return sorted(_CATALOG.keys())


def build_venue(raw: dict) -> Venue:
    maps_url = (
        "https://www.google.com/maps/search/?api=1&query="
        + raw["name"].replace(" ", "+")
        + "+"
        + raw["address"].replace(" ", "+")
    )
    return Venue(
        id=raw["id"],
        name=raw["name"],
        address=raw["address"],
        lat=raw["lat"],
        lng=raw["lng"],
        rating=raw.get("rating"),
        rating_verified=False,
        price_level=raw.get("price_level", 0),
        price_verified=False,
        cost_estimate_per_person=raw.get("cost", _PRICE_PER_LEVEL.get(raw.get("price_level", 0), 0)),
        hours=raw.get("hours"),
        hours_verified=False,
        tags=raw.get("tags", []),
        google_maps_url=maps_url,
        source="demo",
        source_label="Demo sample place — not a live result",
    )


def search_demo(city_key: str, categories: list[str], budget: int | None, limit: int = 10) -> list[Venue]:
    """Demo-mode venue search: match tags to categories, apply budget, keep order."""
    city_key = (city_key or "").strip().lower()
    raw_list = _CATALOG.get(city_key) or _CATALOG.get("denver", [])
    matched: list[Venue] = []
    for raw in raw_list:
        tags = set(raw.get("tags", []))
        if categories:
            wanted = set()
            for c in categories:
                wanted |= _CATEGORY_TAGS.get(c.lower(), set())
            if not (tags & wanted):
                continue
        venue = build_venue(raw)
        if budget is not None and venue.cost_estimate_per_person is not None and venue.cost_estimate_per_person > budget:
            continue
        matched.append(venue)
    return matched[:limit]
