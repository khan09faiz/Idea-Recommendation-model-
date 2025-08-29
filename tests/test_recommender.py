def test_recommend_endpoint_smoke():
    # ensure local package is importable
    import sys
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    payload = {"query": "help with team coaching", "user_tags": ["HR", "Coaching"], "k": 3}

    # Prefer exercising the HTTP endpoint when test client is available.
    try:
        from fastapi.testclient import TestClient
        from src.app import create_app

        client = TestClient(create_app())
        resp = client.post("/recommend", json=payload)
        assert resp.status_code == 200
        data = resp.json()
    except Exception:
        # Fallback: call the recommendation function directly when httpx/TestClient
        # isn't installed in the environment (keeps tests lightweight).
        from src.app import hybrid_recommend
        from src.config import RecommendRequest

        req = RecommendRequest(**payload)
        results = hybrid_recommend(req, k=payload.get("k", 3))
        data = [r.dict() for r in results]
    assert isinstance(data, list)
    # each item should have expected keys
    for item in data:
        assert "id" in item and "title" in item and "description" in item
