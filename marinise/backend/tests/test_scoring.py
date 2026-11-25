"""
Section 21: "Tüm önemli işlemler için testler oluştur." These cover the
pure-logic pieces of the Lead Scoring engine that don't need a live Postgres
connection; DB-integration tests belong in a separate suite once CI has a
Postgres+PostGIS service container (tracked in docs/PROGRESS.md).
"""
from app.services.scoring import _priority_for


def test_priority_thresholds_match_section_10():
    assert _priority_for(100) == "high"
    assert _priority_for(80) == "high"
    assert _priority_for(79) == "medium"
    assert _priority_for(60) == "medium"
    assert _priority_for(59) == "potential"
    assert _priority_for(40) == "potential"
    assert _priority_for(39) == "low"
    assert _priority_for(0) == "low"
