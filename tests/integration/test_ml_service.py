"""
Integration tests for ML/NLP Service
Tests all AI/ML endpoints and functionality
"""

import pytest
from app.services.nlp_service import nlp_service


class TestNLPServiceInitialization:
    """Test NLP service initialization"""

    @pytest.mark.asyncio
    async def test_nlp_service_initialization(self):
        """Test that NLP service can be initialized"""
        await nlp_service.initialize()

        # Check if service is ready
        # Note: This might fail if models are not installed
        # That's expected behavior - tests should guide users to install models
        is_ready = nlp_service.is_ready()

        if not is_ready:
            pytest.skip("NLP models not installed. Run: python scripts/setup_nlp_models.py")

        assert nlp_service.initialized
        assert nlp_service.nlp is not None
        assert nlp_service.embedder is not None

    @pytest.mark.asyncio
    async def test_nlp_service_shutdown(self):
        """Test NLP service shutdown"""
        await nlp_service.initialize()
        await nlp_service.shutdown()
        # Service should still be in initialized state
        # But resources should be cleaned up


class TestTextProcessing:
    """Test basic text processing functions"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service for each test"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_tokenize(self):
        """Test tokenization"""
        text = "Dies ist ein Test."
        tokens = nlp_service.tokenize(text)

        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "Test" in tokens or "test" in tokens

    def test_lemmatize(self):
        """Test lemmatization"""
        text = "Die Kinder spielen im Garten."
        lemmas = nlp_service.lemmatize(text)

        assert isinstance(lemmas, list)
        assert len(lemmas) > 0
        # "spielen" should be lemmatized to "spielen" (infinitive)
        # "Kinder" should be lemmatized to "Kind" (singular)

    def test_remove_stopwords(self):
        """Test stopword removal"""
        text = "Dies ist ein wichtiger Test für die Funktion."
        filtered = nlp_service.remove_stopwords(text)

        assert isinstance(filtered, list)
        # Stopwords like "ist", "ein", "für", "die" should be removed
        assert "wichtiger" in filtered or "wichtig" in filtered
        assert "Test" in filtered or "test" in filtered

    def test_get_pos_tags(self):
        """Test POS tagging"""
        text = "Der schnelle Fuchs springt über den faulen Hund."
        pos_tags = nlp_service.get_pos_tags(text)

        assert isinstance(pos_tags, list)
        assert len(pos_tags) > 0
        # Each tuple should have (token, pos)
        assert all(len(tag) == 2 for tag in pos_tags)


class TestNamedEntityRecognition:
    """Test NER functionality"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_extract_entities_basic(self):
        """Test basic entity extraction"""
        text = "Die Bundesrepublik Deutschland liegt in Europa."
        entities = nlp_service.extract_entities(text)

        assert isinstance(entities, list)
        # Should find "Deutschland" and "Europa" as locations
        locations = [e for e in entities if e['label'] == 'LOC']
        assert len(locations) > 0

    def test_extract_entities_legal_text(self):
        """Test entity extraction in legal text"""
        text = """
        Nach § 5 SGB IX haben Menschen mit Behinderung Anspruch auf Leistungen.
        Die Berliner Senatsverwaltung ist zuständig.
        """
        entities = nlp_service.extract_entities(text)

        assert isinstance(entities, list)
        # Should find Berlin as location
        # Note: "SGB IX" might be extracted as organization or other entity

    def test_extract_legal_references(self):
        """Test legal reference extraction"""
        text = """
        Gemäß § 5 Abs. 2 Satz 1 SGB IX in Verbindung mit Art. 3 GG
        haben Menschen mit Behinderung Anspruch auf Teilhabe.
        """
        refs = nlp_service.extract_legal_references(text)

        assert isinstance(refs, list)
        assert len(refs) > 0
        # Should find "§ 5", "Abs. 2", "Satz 1", "Art. 3"
        assert any("§" in ref or "Art" in ref for ref in refs)


class TestSemanticEmbeddings:
    """Test semantic embedding generation"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_generate_embedding_single(self):
        """Test single text embedding"""
        text = "Menschen mit Behinderung haben Anspruch auf Teilhabe."
        embedding = nlp_service.generate_embedding(text)

        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # paraphrase-multilingual-MiniLM-L12-v2 dimension

    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        texts = [
            "Leistungen zur Teilhabe am Arbeitsleben",
            "Persönliches Budget für Menschen mit Behinderung",
            "Medizinische Rehabilitation und Therapie"
        ]
        embeddings = nlp_service.generate_embeddings_batch(texts)

        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(len(emb) == 384 for emb in embeddings)

    def test_embedding_consistency(self):
        """Test that same text produces consistent embeddings"""
        text = "Test der Konsistenz"
        emb1 = nlp_service.generate_embedding(text)
        emb2 = nlp_service.generate_embedding(text)

        assert emb1 == emb2  # Should be exactly the same


class TestSimilarityScoring:
    """Test similarity calculations"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_calculate_similarity_identical(self):
        """Test similarity of identical texts"""
        text1 = "Leistungen zur Teilhabe"
        text2 = "Leistungen zur Teilhabe"

        similarity = nlp_service.calculate_similarity(text1, text2)

        assert isinstance(similarity, float)
        assert 0.99 <= similarity <= 1.01  # Should be ~1.0 for identical texts

    def test_calculate_similarity_similar(self):
        """Test similarity of similar texts"""
        text1 = "Persönliches Budget für Menschen mit Behinderung"
        text2 = "Individuelles Budget zur Teilhabe"

        similarity = nlp_service.calculate_similarity(text1, text2)

        assert isinstance(similarity, float)
        assert 0.5 <= similarity <= 1.0  # Should be moderately high

    def test_calculate_similarity_different(self):
        """Test similarity of different texts"""
        text1 = "Leistungen zur Teilhabe am Arbeitsleben"
        text2 = "Die Katze sitzt auf der Matte"

        similarity = nlp_service.calculate_similarity(text1, text2)

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 0.5  # Should be low

    def test_find_most_similar(self):
        """Test finding most similar texts"""
        query = "Unterstützung für Menschen mit Behinderung"
        candidates = [
            "Leistungen zur Teilhabe",
            "Die Katze sitzt auf der Matte",
            "Hilfe für behinderte Menschen",
            "Persönliches Budget"
        ]

        results = nlp_service.find_most_similar(query, candidates, top_k=2)

        assert isinstance(results, list)
        assert len(results) <= 2
        # Results should be tuples of (index, similarity)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
        # Should find "Hilfe für behinderte Menschen" as most similar


class TestTextClassification:
    """Test block classification"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_classify_block_type_right(self):
        """Test classification of 'right' type"""
        text = "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe."
        title = "§ 5 Anspruch auf Leistungen"

        block_type = nlp_service.classify_block_type(text, title)

        assert isinstance(block_type, str)
        assert block_type == "right"  # Contains "Anspruch", "haben", "berechtigt"

    def test_classify_block_type_definition(self):
        """Test classification of 'definition' type"""
        text = "Menschen mit Behinderung sind Personen, die körperliche, seelische oder geistige Beeinträchtigungen haben."
        title = "Definition von Behinderung"

        block_type = nlp_service.classify_block_type(text, title)

        assert isinstance(block_type, str)
        assert block_type == "definition"  # Contains "sind", "Definition"

    def test_classify_category_health(self):
        """Test classification of health category"""
        text = "Leistungen zur medizinischen Rehabilitation und Therapie"

        category = nlp_service.classify_category(text)

        assert isinstance(category, str) or category is None
        if category:
            assert category == "health"  # Contains "medizinischen", "Therapie"

    def test_classify_category_employment(self):
        """Test classification of employment category"""
        text = "Leistungen zur Teilhabe am Arbeitsleben und Beschäftigung"

        category = nlp_service.classify_category(text)

        assert isinstance(category, str) or category is None
        if category:
            assert category == "employment"  # Contains "Arbeitsleben", "Beschäftigung"

    def test_classify_block_full(self):
        """Test full block classification"""
        text = "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe am Arbeitsleben."
        title = "§ 5 Leistungen zur Teilhabe"

        result = nlp_service.classify_block(text, title)

        assert isinstance(result, dict)
        assert "type" in result
        assert "category" in result
        assert "entities" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0


class TestTextSummarization:
    """Test text summarization"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_summarize_text_frequency(self):
        """Test frequency-based summarization"""
        text = """
        Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe.
        Die Leistungen umfassen medizinische Rehabilitation.
        Die Leistungen umfassen auch berufliche Rehabilitation.
        Die Leistungen werden durch Rehabilitationsträger erbracht.
        Die Rehabilitationsträger sind gesetzlich verpflichtet.
        """

        summary = nlp_service.summarize_text(text, max_sentences=2, method="frequency")

        assert isinstance(summary, str)
        assert len(summary) < len(text)
        # Should contain key terms like "Leistungen", "Rehabilitation"

    def test_summarize_text_position(self):
        """Test position-based summarization"""
        text = """
        Dies ist der erste Satz.
        Dies ist der zweite Satz.
        Dies ist der dritte Satz.
        Dies ist der vierte Satz.
        """

        summary = nlp_service.summarize_text(text, max_sentences=2, method="position")

        assert isinstance(summary, str)
        # Should contain first 2 sentences
        assert "erste" in summary
        assert "zweite" in summary

    def test_generate_summary_points(self):
        """Test summary points generation"""
        text = """
        Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe.
        Die Leistungen umfassen medizinische Rehabilitation.
        Die Leistungen umfassen berufliche Rehabilitation.
        Die Leistungen umfassen soziale Teilhabe.
        Die Leistungen werden durch Rehabilitationsträger erbracht.
        """

        points = nlp_service.generate_summary_points(text, max_points=3)

        assert isinstance(points, list)
        assert len(points) <= 3
        assert all(isinstance(p, str) for p in points)


class TestTextStatistics:
    """Test text statistics"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_get_text_stats(self):
        """Test text statistics generation"""
        text = "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe."

        stats = nlp_service.get_text_stats(text)

        assert isinstance(stats, dict)
        assert "total_words" in stats
        assert "total_sentences" in stats
        assert "unique_words" in stats
        assert "avg_word_length" in stats
        assert "avg_sentence_length" in stats

        assert stats["total_words"] > 0
        assert stats["total_sentences"] > 0
        assert stats["unique_words"] > 0

    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = """
        Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe
        am Arbeitsleben. Die Leistungen umfassen medizinische Rehabilitation
        und berufliche Rehabilitation. Die Teilhabe ist ein wichtiges Recht.
        """

        keywords = nlp_service.extract_keywords(text, top_n=5)

        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        # Should extract key terms like "Leistungen", "Rehabilitation", "Teilhabe"
        keywords_lower = [k.lower() for k in keywords]
        assert any(term in ' '.join(keywords_lower) for term in ['leistung', 'rehabilitation', 'teilhabe'])


class TestErrorHandling:
    """Test error handling"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup NLP service"""
        await nlp_service.initialize()
        if not nlp_service.is_ready():
            pytest.skip("NLP models not installed")

    def test_empty_text_handling(self):
        """Test handling of empty text"""
        text = ""

        # These should not raise exceptions
        tokens = nlp_service.tokenize(text)
        assert isinstance(tokens, list)

        embedding = nlp_service.generate_embedding(text)
        # Empty text should still produce an embedding (zero vector or default)

    def test_very_long_text_handling(self):
        """Test handling of very long text"""
        text = "Test Satz. " * 1000  # Very long text

        # Should not raise exceptions
        embedding = nlp_service.generate_embedding(text)
        assert embedding is not None
        assert isinstance(embedding, list)

    def test_special_characters_handling(self):
        """Test handling of special characters"""
        text = "§ 5 Abs. 2 Satz 1 <>&%$#@!"

        # Should not raise exceptions
        tokens = nlp_service.tokenize(text)
        entities = nlp_service.extract_entities(text)
        refs = nlp_service.extract_legal_references(text)

        assert isinstance(tokens, list)
        assert isinstance(entities, list)
        assert isinstance(refs, list)
