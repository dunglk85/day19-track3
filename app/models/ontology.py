from typing import List, Set

class Ontology:
    # Node Labels (PascalCase)
    LABELS: Set[str] = {
        "Company",
        "Person",
        "Technology",
        "Location",
        "Product"
    }

    # Relationship Types (SCREAMING_SNAKE_CASE)
    RELATIONSHIPS: Set[str] = {
        "FOUNDED_BY",
        "WORKS_AT",
        "CEO_OF",
        "DEVELOPED",
        "PARTNER_OF",
        "INVESTED_IN",
        "COMPETES_WITH",
        "HEADQUARTERED_IN",
        "ACQUIRED"
    }

    @classmethod
    def is_valid_label(cls, label: str) -> bool:
        return label in cls.LABELS

    @classmethod
    def is_valid_relationship(cls, rel_type: str) -> bool:
        return rel_type in cls.RELATIONSHIPS
