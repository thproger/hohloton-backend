from __future__ import annotations

BUSINESS_CATEGORIES: list[str] = [
    "Cafe",
    "Restaurant",
    "Bakery",
    "Bar",
    "Fast food",
    "Beauty",
    "Barbershop",
    "Health",
    "Pharmacy",
    "Fitness",
    "Services",
    "Auto",
    "Delivery",
    "Education",
    "Entertainment",
    "Other",
]


def normalize_category(value: str) -> str:
    return value.strip()


def is_valid_category(value: str) -> bool:
    normalized = normalize_category(value)
    return any(normalized.lower() == c.lower() for c in BUSINESS_CATEGORIES)


def canonical_category(value: str) -> str:
    normalized = normalize_category(value)
    for c in BUSINESS_CATEGORIES:
        if normalized.lower() == c.lower():
            return c
    return normalized
