ITEMS = {
    # per_kg=True → compare on $/kg (both APIs provide a unit price).
    # The pack size doesn't matter for these; we normalise to per-kg before comparing.
    "Proteins": [
        {"name": "Chicken Breast",    "search": "chicken breast",         "per_kg": True},
        {"name": "Beef Mince",        "search": "beef mince",             "per_kg": True},
        {"name": "Salmon Fillet",     "search": "atlantic salmon fillet", "per_kg": True},
        {"name": "Eggs 12 Pack",      "search": "free range eggs 12 pack"},
    ],
    "Dairy": [
        {"name": "Full Cream Milk 2L",   "search": "full cream milk 2L"},
        {"name": "Butter 500g",          "search": "butter 500g"},
        {"name": "Cheddar Cheese 500g",  "search": "cheddar cheese 500g"},
        {"name": "Greek Yoghurt 500g",   "search": "greek style yoghurt 500g"},
    ],
    "Bread": [
        {"name": "White Sandwich Bread", "search": "white sandwich bread loaf"},
        {"name": "Wholegrain Bread",     "search": "wholegrain bread loaf"},
    ],
    "Pantry": [
        {"name": "Pasta 500g",               "search": "spaghetti pasta 500g"},
        {"name": "White Rice 1kg",           "search": "white rice 1kg"},
        {"name": "Olive Oil 500ml",          "search": "olive oil 500ml"},
        {"name": "Diced Tomatoes 400g",      "search": "diced tomatoes 400g can"},
        {"name": "Tuna in Springwater 95g",  "search": "tuna in springwater 95g"},
        {"name": "Plain Flour 1kg",          "search": "plain flour 1kg"},
        {"name": "White Sugar 1kg",          "search": "white sugar 1kg"},
        {"name": "Rolled Oats 1kg",          "search": "rolled oats 1kg"},
    ],
    "Produce": [
        {"name": "Washed Potatoes",   "search": "washed potatoes",   "per_kg": True},
        {"name": "Brown Onions",      "search": "brown onions",       "per_kg": True},
        {"name": "Carrots",           "search": "carrots",            "per_kg": True},
        {"name": "Broccoli (each)",   "search": "broccoli head"},
        {"name": "Baby Spinach 120g", "search": "baby spinach 120g"},
        {"name": "Bananas",           "search": "cavendish bananas",  "per_kg": True},
        {"name": "Pink Lady Apples",  "search": "pink lady apples",   "per_kg": True},
    ],
    "Frozen": [
        {"name": "Frozen Peas 1kg", "search": "frozen peas 1kg"},
    ],
    "Drinks": [
        {"name": "Orange Juice 2L",     "search": "orange juice 2L"},
        {"name": "Instant Coffee 200g", "search": "instant coffee 200g"},
    ],
    "Household": [
        {"name": "Toilet Paper 12pk",     "search": "toilet paper 12 pack"},
        {"name": "Dishwashing Liquid 1L", "search": "dishwashing liquid 1 litre"},
    ],
}

ALL_ITEM_NAMES = [item["name"] for items in ITEMS.values() for item in items]

def _lookup(item_name: str) -> dict:
    for items in ITEMS.values():
        for item in items:
            if item["name"] == item_name:
                return item
    return {}

def get_search_term(item_name: str) -> str:
    return _lookup(item_name).get("search", item_name)

def is_per_kg(item_name: str) -> bool:
    return bool(_lookup(item_name).get("per_kg", False))
