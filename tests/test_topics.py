import runpy

import github


def test_topics_rank_by_repository_count_with_alphabetical_ties(monkeypatch):
    # Import the application without network access or a real metadata lookup.
    monkeypatch.setattr(github, "enrich_manifest", lambda manifest: [])
    topic_counts = runpy.run_path("app.py")["topic_counts"]
    repos = [
        {"topics": ["python", "python", "valkey", "aiven-runtime"]},
        {"topics": ["python", "valkey", "aiven-labs"]},
        {"topics": ["python", "clickhouse", "airflow"]},
        {},
    ]
    assert topic_counts(repos) == [
        {"name": "python", "count": 3},
        {"name": "valkey", "count": 2},
        {"name": "airflow", "count": 1},
        {"name": "clickhouse", "count": 1},
    ]
    assert topic_counts([]) == []
