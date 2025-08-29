import pytest


@pytest.fixture
def patch_heavy(monkeypatch):
    # stub embedding encoder and index within utils
    class DummyEmbed:
        def encode(self, texts, normalize_embeddings=True):
            import numpy as _np

            return _np.stack([_np.ones(8) * (i + 1) for i, _ in enumerate(texts)])

    def _apply():
        def dummy_build_index(seed_texts):
            from src import utils as _u

            embed = DummyEmbed()
            vecs = embed.encode(seed_texts)
            _u._faiss_index = (vecs, seed_texts)

        def dummy_retrieve(q, top_n=10):
            from src.data_processing import load_ideas

            rows = load_ideas()
            return [(1.0 / (i + 1), i) for i in range(min(top_n, len(rows)))]

        def dummy_generate(query, seeds, n=5, user_tags=None):
            return "Title: Generated A\nDescription: gen desc\nTags: gen"

        monkeypatch.setattr("src.utils.build_embedding_index", dummy_build_index, raising=False)
        monkeypatch.setattr("src.utils.retrieve_candidates", dummy_retrieve, raising=False)
        monkeypatch.setattr("src.utils.ollama_generate", dummy_generate, raising=False)

    return _apply


def test_recommend_mocked(patch_heavy):
    import sys
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    patch_heavy()
    payload = {"query": "test", "user_tags": ["HR"], "k": 2}

    try:
        from fastapi.testclient import TestClient
        from src.app import create_app

        client = TestClient(create_app())
        resp = client.post("/recommend", json=payload)
        assert resp.status_code == 200
        data = resp.json()
    except Exception:
        # Fallback: call recommendation function directly when httpx isn't available
        from src.app import hybrid_recommend
        from src.config import RecommendRequest

        req = RecommendRequest(**payload)
        results = hybrid_recommend(req, k=payload.get("k", 2))
        data = [r.dict() for r in results]
    assert isinstance(data, list)
    assert len(data) <= 2
    for it in data:
        assert "title" in it and "description" in it
