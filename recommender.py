
import json
import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai

# -------------------- Configuration --------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash-lite"

DATA_PATH = Path(__file__).parent / "data" / "listings.csv"

CITY_NAMES = [
    "Pune", "Mumbai", "Bengaluru",
    "Delhi", "Hyderabad", "Chennai",
]

CATEGORIES = [
    "coworking",
    "podcast studio",
    "meeting room",
    "event venue",
    "training room",
    "photo studio",
]

CATEGORY_ALIASES = {
    "coworking": ["coworking", "co-working", "workspace", "desk"],
    "podcast studio": ["podcast studio", "recording studio", "podcast"],
    "meeting room": ["meeting room", "conference room", "meeting space"],
    "event venue": ["event venue", "event hall", "party hall", "venue"],
    "training room": ["training room", "classroom", "workshop room"],
    "photo studio": ["photo studio", "photography studio", "photoshoot studio"],
}

FEATURE_ALIASES = {
    "wifi": ["wifi", "wi-fi", "internet"],
    "power backup": ["power backup", "backup power"],
    "parking": ["parking", "car parking"],
    "air conditioning": ["air conditioning", "ac", "air conditioned"],
    "coffee": ["coffee", "coffee machine"],
    "soundproofing": ["soundproofing", "soundproof"],
    "microphones": ["microphones", "microphone", "mic"],
    "lighting": ["lighting", "lights"],
    "video recording": ["video recording", "video recording equipment"],
    "projector": ["projector", "projection"],
    "whiteboard": ["whiteboard", "white board"],
    "video conferencing": ["video conferencing", "video conference"],
    "catering": ["catering", "food service"],
    "sound system": ["sound system", "speakers"],
    "stage": ["stage", "platform"],
    "computers": ["computers", "computer systems", "pcs"],
    "backdrops": ["backdrops", "backdrop"],
    "camera equipment": ["camera equipment", "camera gear"],
    "changing room": ["changing room", "changing area"],
    "natural light": ["natural light", "daylight"],
    "recording equipment": ["recording equipment", "recording gear"],
}

# Features accepted from Gemini and matched to the listing dataset.
GEMINI_FEATURES = [
    "wifi",
    "projector",
    "whiteboard",
    "parking",
    "air conditioning",
    "soundproofing",
    "natural light",
    "recording equipment",
    "microphones",
    "lighting",
    "video recording",
    "power backup",
    "coffee",
    "video conferencing",
    "catering",
    "sound system",
    "stage",
    "computers",
    "backdrops",
    "camera equipment",
    "changing room",
]


# -------------------- Rule-Based Query Parser --------------------

def parse_query(query):
    """Extract listing requirements using simple text rules."""
    text = (query or "").lower().strip()

    result = {
        "city": None,
        "category": None,
        "max_price": None,
        "min_capacity": None,
        "required_features": [],
        "preferred_features": [],
        "available_only": True,
        "vague": False,
        "clarification": None,
    }

    if not text:
        result["vague"] = True
        result["clarification"] = (
            "Please describe what type of space you need."
        )
        return result

    for city in CITY_NAMES:
        if re.search(rf"\b{re.escape(city.lower())}\b", text):
            result["city"] = city
            break

    for category, aliases in CATEGORY_ALIASES.items():
        if any(alias in text for alias in aliases):
            result["category"] = category
            break

    budget_match = re.search(
        r"(?:under|below|less than|maximum|max|budget(?: of)?|within)"
        r"\s*₹?\s*([\d,]+)",
        text,
    )
    if budget_match:
        result["max_price"] = int(
            budget_match.group(1).replace(",", "")
        )

    capacity_match = re.search(
        r"(?:for|capacity(?: of)?|accommodate(?:s)?|seating for)"
        r"\s*(\d+)\s*(?:people|persons|guests|attendees|seats|members)?"
        r"|\b(\d+)\s*(?:people|persons|guests|attendees|seats)\b",
        text,
    )
    if capacity_match:
        number = capacity_match.group(1) or capacity_match.group(2)
        result["min_capacity"] = int(number)

    required_words = [
        "must have", "must include", "need", "needs",
        "require", "requires", "required", "mandatory",
        "essential", "only if", "with",
    ]

    for feature, aliases in FEATURE_ALIASES.items():
        positions = [
            text.find(word)
            for word in required_words
            if text.find(word) >= 0
        ]
        feature_positions = [
            text.find(alias)
            for alias in aliases
            if text.find(alias) >= 0
        ]

        if feature_positions:
            if positions and any(
                position <= min(feature_positions)
                for position in positions
            ):
                result["required_features"].append(feature)
            else:
                result["preferred_features"].append(feature)

    if not any([
        result["city"],
        result["category"],
        result["max_price"] is not None,
        result["min_capacity"] is not None,
        result["required_features"],
        result["preferred_features"],
    ]):
        result["vague"] = True
        result["clarification"] = (
            "Could you specify the type of space, city, budget, "
            "capacity, or features you prefer?"
        )

    return result


# -------------------- Gemini Query Parser --------------------

def parse_query_with_gemini(query):
    """Use Gemini to extract structured requirements, or return None."""
    if not API_KEY or not query or not query.strip():
        return None

    prompt = f"""
You extract search requirements for a workspace and venue listing app.

Return ONLY a JSON object with:
- city: one of {CITY_NAMES}, or null
- category: one of {CATEGORIES}, or null
- max_price: a positive number, or null
- min_capacity: a positive integer, or null
- required_features: a list chosen only from {GEMINI_FEATURES}
- preferred_features: a list chosen only from {GEMINI_FEATURES}
- clarification_needed: true or false
- clarification_question: a short question or null

Do not invent requirements. Treat explicit budget limits as max_price,
people counts as min_capacity, necessary features as required_features,
and optional features as preferred_features.
If the query is too vague, request clarification.
Return JSON only.

User query: {json.dumps(query)}
"""

    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0,
            },
        )

        data = json.loads(response.text)
        if not isinstance(data, dict):
            return None

        city = data.get("city")
        category = data.get("category")
        max_price = data.get("max_price")
        min_capacity = data.get("min_capacity")
        required = data.get("required_features", [])
        preferred = data.get("preferred_features", [])
        vague = data.get("clarification_needed", False)
        clarification = data.get("clarification_question")

        if city not in CITY_NAMES:
            city = None

        if category not in CATEGORIES:
            category = None

        if (
            isinstance(max_price, bool)
            or not isinstance(max_price, (int, float))
            or max_price <= 0
        ):
            max_price = None

        if (
            isinstance(min_capacity, bool)
            or not isinstance(min_capacity, int)
            or min_capacity <= 0
        ):
            min_capacity = None

        if not isinstance(required, list):
            required = []
        if not isinstance(preferred, list):
            preferred = []

        required = [
            feature for feature in required
            if feature in GEMINI_FEATURES
        ]
        preferred = [
            feature for feature in preferred
            if feature in GEMINI_FEATURES
        ]

        if not isinstance(vague, bool):
            vague = False
        if not isinstance(clarification, str):
            clarification = None

        return {
            "city": city,
            "category": category,
            "max_price": max_price,
            "min_capacity": min_capacity,
            "required_features": required,
            "preferred_features": preferred,
            "clarification_needed": vague,
            "clarification_question": clarification,
        }

    except Exception as error:
        print(f"Gemini query parsing failed: {error}")
        return None


# -------------------- Unified Requirements --------------------

def get_requirements(query):
    """Try Gemini first and use rule-based parsing as a fallback."""
    gemini = parse_query_with_gemini(query)

    if gemini is not None:
        return {
            "city": gemini["city"],
            "category": gemini["category"],
            "max_price": gemini["max_price"],
            "min_capacity": gemini["min_capacity"],
            "required_features": [
                feature.lower()
                for feature in gemini["required_features"]
            ],
            "preferred_features": [
                feature.lower()
                for feature in gemini["preferred_features"]
            ],
            "available_only": True,
            "vague": gemini["clarification_needed"],
            "clarification": (
                gemini["clarification_question"]
                or "Could you share your preferred city, listing type, or budget?"
            ),
        }

    print("Using rule-based query parser as fallback.")
    return parse_query(query)


# -------------------- Listing Data --------------------

def load_listings():
    """Load and prepare the CSV listing dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. "
            "Run: python create_dataset.py"
        )

    df = pd.read_csv(DATA_PATH)

    df["available"] = (
        df["available"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("true")
    )

    df["features_list"] = (
        df["features"]
        .fillna("")
        .apply(
            lambda value: [
                feature.strip().lower()
                for feature in str(value).split("|")
                if feature.strip()
            ]
        )
    )

    return df


# -------------------- Recommendation Engine --------------------

def recommend(query, top_n=5):
    """Filter, rank and explain suitable listings."""
    df = load_listings()
    requirements = get_requirements(query)

    if requirements["vague"]:
        return {
            "status": "clarification",
            "message": requirements["clarification"],
            "requirements": requirements,
            "results": [],
        }

    candidates = df[df["available"]].copy()

    if requirements["city"]:
        candidates = candidates[
            candidates["city"].str.lower()
            == requirements["city"].lower()
        ]

    if requirements["category"]:
        candidates = candidates[
            candidates["category"].str.lower()
            == requirements["category"].lower()
        ]

    if requirements["max_price"] is not None:
        candidates = candidates[
            candidates["price_per_hour"]
            <= requirements["max_price"]
        ]

    if requirements["min_capacity"] is not None:
        candidates = candidates[
            candidates["capacity"]
            >= requirements["min_capacity"]
        ]

    required_features = requirements["required_features"]

    if required_features:
        candidates = candidates[
            candidates["features_list"].apply(
                lambda features: all(
                    feature in features for feature in required_features
                )
            )
        ]

    if candidates.empty:
        return {
            "status": "no_matches",
            "message": (
                "No available listings match all your stated "
                "requirements. Try relaxing your budget, capacity, "
                "or required features."
            ),
            "requirements": requirements,
            "results": [],
        }

    def calculate_score(row):
        score = float(row["rating"]) * 10

        matched_preferences = sum(
            feature in row["features_list"]
            for feature in requirements["preferred_features"]
        )
        score += matched_preferences * 8

        budget = requirements["max_price"]
        if budget is not None and budget > 0:
            score += max(
                0,
                15 * (1 - row["price_per_hour"] / budget),
            )

        capacity = requirements["min_capacity"]
        if capacity is not None:
            extra_capacity = max(0, row["capacity"] - capacity)
            score += max(0, 5 - extra_capacity * 0.2)

        return round(score, 2)

    candidates["score"] = candidates.apply(calculate_score, axis=1)
    candidates = candidates.sort_values(
        by=["score", "rating", "price_per_hour"],
        ascending=[False, False, True],
    )

    results = []

    for _, row in candidates.head(top_n).iterrows():
        reasons = [
            f"Rated {row['rating']}/5",
            f"₹{row['price_per_hour']} per hour",
            f"Capacity for {row['capacity']} people",
        ]

        if requirements["city"]:
            reasons.append(f"Located in {row['city']}")

        if requirements["category"]:
            reasons.append(f"Category: {row['category']}")

        matched_features = [
            feature
            for feature in (
                required_features + requirements["preferred_features"]
            )
            if feature in row["features_list"]
        ]

        if matched_features:
            reasons.append("Features: " + ", ".join(matched_features))

        results.append({
            "id": int(row["id"]),
            "name": row["name"],
            "city": row["city"],
            "category": row["category"],
            "price_per_hour": int(row["price_per_hour"]),
            "capacity": int(row["capacity"]),
            "features": row["features"],
            "rating": float(row["rating"]),
            "score": float(row["score"]),
            "reasons": reasons,
        })

    return {
        "status": "success",
        "message": f"Found {len(candidates)} matching available listings.",
        "requirements": requirements,
        "results": results,
    }


if __name__ == "__main__":
    example = (
        "Find a meeting room in Pune under 1500 "
        "for 8 people with a projector"
    )
    response = recommend(example)

    print("\nQuery:", example)
    print("Status:", response["status"])
    print("Message:", response["message"])

    for index, listing in enumerate(response["results"], start=1):
        print(f"\n{index}. {listing['name']}")
        print(f"   Price: ₹{listing['price_per_hour']}/hour")
        print(f"   Rating: {listing['rating']}/5")
        print("   Why recommended:", "; ".join(listing["reasons"]))
