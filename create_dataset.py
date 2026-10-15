
import csv
import random
from pathlib import Path

random.seed(42)

CITIES = [
    "Pune", "Mumbai", "Bengaluru",
    "Delhi", "Hyderabad", "Chennai"
]

LISTINGS = [
    {
        "category": "coworking",
        "names": ["WorkHub", "FocusSpace"],
        "price_range": (300, 1200),
        "capacity_range": (1, 20),
        "features": [
            "wifi", "power backup", "parking",
            "air conditioning", "coffee"
        ],
    },
    {
        "category": "podcast studio",
        "names": ["SoundBox", "Creator Studio"],
        "price_range": (800, 3000),
        "capacity_range": (2, 8),
        "features": [
            "soundproofing", "microphones", "lighting",
            "video recording", "wifi"
        ],
    },
    {
        "category": "meeting room",
        "names": ["MeetPoint", "Collab Room"],
        "price_range": (500, 2500),
        "capacity_range": (4, 20),
        "features": [
            "projector", "whiteboard", "wifi",
            "video conferencing", "air conditioning"
        ],
    },
    {
        "category": "event venue",
        "names": ["Celebration Hall", "GatherSpace"],
        "price_range": (3000, 15000),
        "capacity_range": (30, 200),
        "features": [
            "parking", "catering", "sound system",
            "air conditioning", "stage"
        ],
    },
    {
        "category": "training room",
        "names": ["LearnLab", "SkillSpace"],
        "price_range": (1000, 5000),
        "capacity_range": (10, 50),
        "features": [
            "projector", "whiteboard", "wifi",
            "computers", "air conditioning"
        ],
    },
    {
        "category": "photo studio",
        "names": ["FrameStudio", "LightBox Studio"],
        "price_range": (1000, 4000),
        "capacity_range": (2, 12),
        "features": [
            "lighting", "backdrops", "camera equipment",
            "changing room", "air conditioning"
        ],
    },
]


def create_dataset():
    output_path = Path("data") / "listings.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Allocate 35 listings across all six cities and categories.
    # Repeated city/category combinations provide more options
    # for common searches.
    plan = [
        ("Pune", 2), ("Mumbai", 2),
        ("Bengaluru", 2), ("Delhi", 2),
        ("Hyderabad", 2), ("Chennai", 2),
        ("Pune", 1), ("Mumbai", 1),
        ("Bengaluru", 1), ("Delhi", 1),
        ("Hyderabad", 1), ("Chennai", 1),
        ("Pune", 3), ("Mumbai", 3),
        ("Bengaluru", 3), ("Delhi", 3),
        ("Hyderabad", 3), ("Chennai", 3),
        ("Pune", 4), ("Mumbai", 4),
        ("Bengaluru", 4), ("Delhi", 4),
        ("Hyderabad", 4), ("Chennai", 4),
        ("Pune", 5), ("Mumbai", 5),
        ("Bengaluru", 5), ("Delhi", 5),
        ("Hyderabad", 5), ("Chennai", 5),
        ("Pune", 0), ("Mumbai", 0),
        ("Bengaluru", 0), ("Pune", 2),
        ("Mumbai", 2),
    ]

    rows = []

    for listing_id, (city, category_index) in enumerate(plan, start=1):
        item = LISTINGS[category_index]
        low_price, high_price = item["price_range"]
        low_capacity, high_capacity = item["capacity_range"]

        # Ensure each listing has a varied, valid feature combination.
        selected_features = random.sample(
            item["features"],
            k=random.randint(3, len(item["features"]))
        )

        price_steps = (high_price - low_price) // 100
        price = low_price + 100 * random.randint(0, price_steps)

        capacity = random.randint(low_capacity, high_capacity)

        rows.append({
            "id": listing_id,
            "name": f"{random.choice(item['names'])} {city} {listing_id}",
            "city": city,
            "category": item["category"],
            "price_per_hour": price,
            "capacity": capacity,
            "features": "|".join(selected_features),
            "rating": round(random.uniform(3.8, 5.0), 1),
            "available": True,
        })

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Dataset created: {output_path.resolve()}")
    print(f"Total listings: {len(rows)}")
    print(f"Cities: {len(set(row['city'] for row in rows))}")
    print(f"Categories: {len(set(row['category'] for row in rows))}")


if __name__ == "__main__":
    create_dataset()
