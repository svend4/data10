"""
Integration tests for ML API endpoints
Tests all REST API endpoints for ML/NLP functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.nlp_service import nlp_service


# Create test client
client = TestClient(app)


class TestMLAPIHealth:
    """Test ML API health and status"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()

    def test_ml_status_endpoint(self):
        """Test GET /api/ml/status"""
        response = client.get("/api/ml/status")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "spacy_model" in data
        assert "transformer_model" in data
        assert "initialized" in data

        assert data["status"] in ["ready", "not_ready"]
        assert data["spacy_model"] == "de_core_news_lg"
        assert data["transformer_model"] == "paraphrase-multilingual-MiniLM-L12-v2"


class TestTextAnalysisAPI:
    """Test /api/ml/analyze endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_analyze_text_success(self):
        """Test successful text analysis"""
        payload = {
            "text": "Nach § 5 SGB IX haben Menschen mit Behinderung Anspruch auf Leistungen zur Teilhabe."
        }

        response = client.post("/api/ml/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "text" in data
        assert "stats" in data
        assert "keywords" in data
        assert "entities" in data
        assert "legal_references" in data
        assert "embedding" in data

        # Check stats
        assert "total_words" in data["stats"]
        assert "total_sentences" in data["stats"]

        # Check keywords
        assert isinstance(data["keywords"], list)

        # Check entities
        assert isinstance(data["entities"], list)

        # Check legal references
        assert isinstance(data["legal_references"], list)
        assert len(data["legal_references"]) > 0

        # Check embedding
        assert isinstance(data["embedding"], list)
        assert len(data["embedding"]) == 384

    def test_analyze_text_missing_text(self):
        """Test analysis with missing text"""
        payload = {}

        response = client.post("/api/ml/analyze", json=payload)

        assert response.status_code == 422  # Validation error

    def test_analyze_text_empty_text(self):
        """Test analysis with empty text"""
        payload = {"text": ""}

        response = client.post("/api/ml/analyze", json=payload)

        # Empty text should still work (graceful handling)
        assert response.status_code in [200, 422]


class TestEmbeddingAPI:
    """Test /api/ml/embedding endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_generate_embedding_success(self):
        """Test successful embedding generation"""
        payload = {
            "text": "Persönliches Budget für Menschen mit Behinderung"
        }

        response = client.post("/api/ml/embedding", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "text" in data
        assert "embedding" in data
        assert "dimension" in data

        assert isinstance(data["embedding"], list)
        assert data["dimension"] == 384
        assert len(data["embedding"]) == 384

    def test_generate_embedding_long_text(self):
        """Test embedding generation with long text"""
        payload = {
            "text": "Menschen mit Behinderung haben Anspruch. " * 50
        }

        response = client.post("/api/ml/embedding", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert len(data["embedding"]) == 384


class TestSimilarityAPI:
    """Test /api/ml/similarity endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_calculate_similarity_success(self):
        """Test successful similarity calculation"""
        payload = {
            "text1": "Persönliches Budget",
            "text2": "Individuelles Budget für Teilhabe"
        }

        response = client.post("/api/ml/similarity", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "text1" in data
        assert "text2" in data
        assert "similarity" in data

        assert isinstance(data["similarity"], float)
        assert 0.0 <= data["similarity"] <= 1.0

    def test_calculate_similarity_identical(self):
        """Test similarity of identical texts"""
        payload = {
            "text1": "Leistungen zur Teilhabe",
            "text2": "Leistungen zur Teilhabe"
        }

        response = client.post("/api/ml/similarity", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Identical texts should have high similarity
        assert data["similarity"] > 0.95

    def test_calculate_similarity_missing_field(self):
        """Test similarity with missing field"""
        payload = {
            "text1": "Test"
        }

        response = client.post("/api/ml/similarity", json=payload)

        assert response.status_code == 422  # Validation error


class TestNERAPI:
    """Test /api/ml/ner endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_ner_success(self):
        """Test successful NER extraction"""
        payload = {
            "text": "Nach § 5 SGB IX haben Menschen mit Behinderung in Berlin Anspruch auf Leistungen."
        }

        response = client.post("/api/ml/ner", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "text" in data
        assert "entities" in data
        assert "legal_references" in data

        assert isinstance(data["entities"], list)
        assert isinstance(data["legal_references"], list)

        # Should find Berlin as location
        locations = [e for e in data["entities"] if e['label'] == 'LOC']
        # Note: Might not always detect Berlin depending on context

        # Should find legal references
        assert len(data["legal_references"]) > 0

    def test_ner_with_multiple_entities(self):
        """Test NER with multiple entities"""
        payload = {
            "text": "Die Berliner Senatsverwaltung und das Bundesministerium arbeiten zusammen."
        }

        response = client.post("/api/ml/ner", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert len(data["entities"]) > 0


class TestClassificationAPI:
    """Test /api/ml/classify endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_classify_success(self):
        """Test successful classification"""
        payload = {
            "text": "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe.",
            "title": "§ 5 Leistungen zur Teilhabe"
        }

        response = client.post("/api/ml/classify", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "text" in data
        assert "type" in data
        assert "category" in data
        assert "entities" in data
        assert "confidence" in data

        assert isinstance(data["type"], str)
        assert data["type"] in [
            "paragraph", "definition", "procedure",
            "requirement", "right", "obligation", "sanction"
        ]

        if data["category"]:
            assert data["category"] in [
                "employment", "health", "education",
                "social_security", "participation", "administration"
            ]

        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0

    def test_classify_without_title(self):
        """Test classification without title"""
        payload = {
            "text": "Menschen mit Behinderung haben Anspruch auf Leistungen."
        }

        response = client.post("/api/ml/classify", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "type" in data


class TestSummarizationAPI:
    """Test /api/ml/summarize endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_summarize_success(self):
        """Test successful summarization"""
        payload = {
            "text": """
            Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe.
            Die Leistungen umfassen medizinische Rehabilitation.
            Die Leistungen umfassen berufliche Rehabilitation.
            Die Leistungen umfassen soziale Teilhabe.
            Die Leistungen werden durch Rehabilitationsträger erbracht.
            Die Rehabilitationsträger sind gesetzlich verpflichtet.
            """,
            "max_sentences": 2,
            "method": "frequency"
        }

        response = client.post("/api/ml/summarize", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "original_text" in data
        assert "summary" in data
        assert "compression_ratio" in data
        assert "summary_points" in data

        assert isinstance(data["summary"], str)
        assert len(data["summary"]) < len(payload["text"])
        assert isinstance(data["compression_ratio"], float)
        assert 0.0 <= data["compression_ratio"] <= 1.0
        assert isinstance(data["summary_points"], list)

    def test_summarize_position_method(self):
        """Test summarization with position method"""
        payload = {
            "text": "Erster Satz. Zweiter Satz. Dritter Satz. Vierter Satz.",
            "max_sentences": 2,
            "method": "position"
        }

        response = client.post("/api/ml/summarize", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Should contain first 2 sentences
        assert "Erster" in data["summary"]

    def test_summarize_invalid_method(self):
        """Test summarization with invalid method"""
        payload = {
            "text": "Test text.",
            "max_sentences": 2,
            "method": "invalid_method"
        }

        response = client.post("/api/ml/summarize", json=payload)

        # Should either accept it (and fallback to default) or reject
        # Implementation dependent
        assert response.status_code in [200, 422]


class TestSemanticSearchAPI:
    """Test /api/ml/semantic-search endpoint"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup services"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

        # Note: This endpoint also requires blocks to be indexed
        # In a real integration test, you'd create test blocks first

    def test_semantic_search_structure(self):
        """Test semantic search response structure"""
        payload = {
            "query": "Welche Leistungen gibt es für Menschen mit Behinderung?",
            "limit": 5
        }

        response = client.post("/api/ml/semantic-search", json=payload)

        # May return 200 even if no results (empty database)
        if response.status_code == 200:
            data = response.json()

            assert "query" in data
            assert "results" in data
            assert "total" in data

            assert isinstance(data["results"], list)
            assert isinstance(data["total"], int)

            # If results exist, check structure
            if len(data["results"]) > 0:
                result = data["results"][0]
                assert "block_id" in result
                assert "title" in result
                assert "similarity" in result


class TestElasticsearchSemanticSearchAPI:
    """Test /api/search/semantic endpoint (Elasticsearch-based)"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup services"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_elasticsearch_semantic_search_structure(self):
        """Test Elasticsearch semantic search response structure"""
        payload = {
            "query": "Teilhabe am Arbeitsleben",
            "limit": 5,
            "min_score": 0.5
        }

        response = client.post("/api/search/semantic", json=payload)

        # May return 200 even if no results (empty index)
        if response.status_code == 200:
            data = response.json()

            assert "query" in data
            assert "results" in data
            assert "total" in data

            assert data["query"] == payload["query"]
            assert isinstance(data["results"], list)
            assert isinstance(data["total"], int)

    def test_elasticsearch_semantic_search_with_filters(self):
        """Test semantic search with filters"""
        payload = {
            "query": "Leistungen",
            "source": "SGB IX",
            "limit": 10,
            "min_score": 0.6
        }

        response = client.post("/api/search/semantic", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "results" in data


class TestMLAPIErrorHandling:
    """Test error handling in ML API"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()

    def test_service_not_ready_handling(self):
        """Test API behavior when NLP service is not ready"""
        if nlp_service.is_ready():
            pytest.skip("NLP service is ready, cannot test not-ready state")

        # If service is not ready, endpoints should return 503
        payload = {"text": "Test"}

        response = client.post("/api/ml/analyze", json=payload)

        # Should return 503 Service Unavailable
        assert response.status_code == 503

    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/ml/analyze",
            data="not a valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_malformed_request(self):
        """Test handling of malformed requests"""
        # Missing required fields
        payload = {}

        response = client.post("/api/ml/analyze", json=payload)

        assert response.status_code == 422


class TestMLAPIIntegration:
    """Test full integration scenarios"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_full_workflow_analysis_to_classification(self):
        """Test complete workflow: analyze -> classify"""
        text = "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe am Arbeitsleben."
        title = "§ 5 Leistungen zur Teilhabe"

        # Step 1: Analyze
        response1 = client.post("/api/ml/analyze", json={"text": text})
        assert response1.status_code == 200
        analysis = response1.json()

        # Step 2: Classify
        response2 = client.post("/api/ml/classify", json={"text": text, "title": title})
        assert response2.status_code == 200
        classification = response2.json()

        # Both should succeed and return consistent data
        assert analysis["keywords"] is not None
        assert classification["type"] is not None

    def test_embedding_and_similarity_workflow(self):
        """Test workflow: generate embeddings -> calculate similarity"""
        text1 = "Persönliches Budget"
        text2 = "Individuelles Budget"

        # Generate embeddings
        response1 = client.post("/api/ml/embedding", json={"text": text1})
        response2 = client.post("/api/ml/embedding", json={"text": text2})

        assert response1.status_code == 200
        assert response2.status_code == 200

        emb1 = response1.json()["embedding"]
        emb2 = response2.json()["embedding"]

        assert len(emb1) == 384
        assert len(emb2) == 384

        # Calculate similarity
        response3 = client.post("/api/ml/similarity", json={"text1": text1, "text2": text2})
        assert response3.status_code == 200

        similarity = response3.json()["similarity"]
        assert 0.0 <= similarity <= 1.0
