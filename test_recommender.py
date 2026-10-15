
from unittest.mock import patch

from recommender import recommend, parse_query_with_gemini


def test_normal_query():
    result = recommend(
        "Find a meeting room in Pune under 1500 "
        "for 8 people with a projector"
    )
    assert result["status"] == "success"
    assert len(result["results"]) > 0

    for listing in result["results"]:
        assert listing["city"] == "Pune"
        assert listing["category"] == "meeting room"
        assert listing["price_per_hour"] <= 1500
        assert listing["capacity"] >= 8
        assert "projector" in [
            feature.strip().lower()
            for feature in listing["features"].split("|")
        ]


def test_vague_query():
    result = recommend("I need something nice")
    assert result["status"] == "clarification"
    assert result["results"] == []


def test_no_match_query():
    result = recommend(
        "Find a podcast studio in Pune under 1 "
        "for 100 people"
    )
    assert result["status"] == "no_matches"
    assert result["results"] == []


def test_results_are_available():
    result = recommend("Find a coworking space in Mumbai")

    for listing in result["results"]:
        assert listing["id"] > 0


def test_results_have_explanations():
    result = recommend("Find a photo studio in Delhi")

    if result["status"] == "success":
        for listing in result["results"]:
            assert len(listing["reasons"]) > 0
            assert listing["name"]
            assert listing["score"] > 0


def test_gemini_parser_returns_valid_requirements():
    # Avoid making a real API call during this unit test.
    fake_requirements = {
        "city": "Pune",
        "category": "meeting room",
        "max_price": 1500,
        "min_capacity": 8,
        "required_features": ["projector"],
        "preferred_features": [],
        "clarification_needed": False,
        "clarification_question": None,
    }

    with patch("recommender.parse_query_with_gemini",
               return_value=fake_requirements):
        from recommender import get_requirements

        result = get_requirements(
            "Find a meeting room in Pune under 1500 "
            "for 8 people with a projector"
        )

    assert result["city"] == "Pune"
    assert result["category"] == "meeting room"
    assert result["max_price"] == 1500
    assert result["min_capacity"] == 8
    assert "projector" in result["required_features"]


def test_rule_based_fallback_when_gemini_fails():
    with patch("recommender.parse_query_with_gemini",
               return_value=None):
        result = recommend(
            "Find a meeting room in Pune under 1500 "
            "for 8 people with a projector"
        )

    assert result["status"] == "success"
    assert len(result["results"]) > 0
