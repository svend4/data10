"""
ML/NLP API endpoints
Машинное обучение и обработка естественного языка
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import nlp_service, block_service


router = APIRouter()


class TextAnalysisRequest(BaseModel):
    """Запрос на анализ текста"""
    text: str = Field(..., description="Текст для анализа")


class TextAnalysisResponse(BaseModel):
    """Результат анализа текста"""
    text: str
    stats: dict
    keywords: List[str]
    entities: List[dict]
    legal_references: List[str]
    embedding: Optional[List[float]] = None


class EmbeddingRequest(BaseModel):
    """Запрос на генерацию embedding"""
    text: str = Field(..., description="Текст для векторизации")


class EmbeddingResponse(BaseModel):
    """Ответ с embedding"""
    text: str
    embedding: List[float]
    dimension: int


class SimilarityRequest(BaseModel):
    """Запрос на вычисление сходства"""
    text1: str = Field(..., description="Первый текст")
    text2: str = Field(..., description="Второй текст")


class SimilarityResponse(BaseModel):
    """Ответ с мерой сходства"""
    text1: str
    text2: str
    similarity: float


class SemanticSearchRequest(BaseModel):
    """Запрос семантического поиска"""
    query: str = Field(..., description="Поисковый запрос")
    limit: int = Field(5, ge=1, le=50, description="Количество результатов")
    source: Optional[str] = Field(None, description="Фильтр по источнику")


class SemanticSearchResponse(BaseModel):
    """Результат семантического поиска"""
    query: str
    results: List[dict]
    total: int


class NERRequest(BaseModel):
    """Запрос на извлечение сущностей"""
    text: str = Field(..., description="Текст для анализа")


class NERResponse(BaseModel):
    """Ответ с извлечёнными сущностями"""
    text: str
    entities: List[dict]
    legal_references: List[str]


class ClassificationRequest(BaseModel):
    """Запрос на классификацию блока"""
    text: str = Field(..., description="Текст блока")
    title: str = Field("", description="Заголовок блока (опционально)")


class ClassificationResponse(BaseModel):
    """Результат классификации"""
    text: str
    type: str
    category: Optional[str]
    entities: List[dict]
    confidence: float


class SummarizationRequest(BaseModel):
    """Запрос на резюмирование текста"""
    text: str = Field(..., description="Текст для резюмирования")
    max_sentences: int = Field(3, ge=1, le=10, description="Максимум предложений")
    method: str = Field("frequency", description="Метод: 'frequency' или 'position'")


class SummarizationResponse(BaseModel):
    """Результат резюмирования"""
    original_text: str
    summary: str
    compression_ratio: float
    summary_points: List[str]


@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Полный анализ текста

    Выполняет комплексный NLP анализ текста:
    - Статистика (слова, предложения, уникальные слова)
    - Ключевые слова (top-10)
    - Named Entity Recognition (сущности)
    - Извлечение юридических ссылок (§, Art., etc.)
    - Генерация semantic embedding

    Example:
    ```json
    POST /api/ml/analyze
    {
      "text": "Nach § 5 SGB IX haben Menschen mit Behinderung Anspruch..."
    }
    ```

    Returns:
    ```json
    {
      "text": "...",
      "stats": {
        "word_count": 45,
        "sentence_count": 3,
        "unique_words": 32
      },
      "keywords": ["Anspruch", "Behinderung", "Teilhabe"],
      "entities": [{"text": "SGB IX", "label": "LAW"}],
      "legal_references": ["§ 5", "SGB IX"],
      "embedding": [0.123, -0.456, ...]
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready. Models may still be loading."
        )

    try:
        stats = nlp_service.get_text_stats(request.text)
        keywords = nlp_service.extract_keywords(request.text, top_n=10)
        entities = nlp_service.extract_entities(request.text)
        legal_refs = nlp_service.extract_legal_references(request.text)
        embedding = nlp_service.generate_embedding(request.text)

        return TextAnalysisResponse(
            text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            stats=stats,
            keywords=keywords,
            entities=entities,
            legal_references=legal_refs,
            embedding=embedding
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embedding", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """
    Генерация semantic embedding для текста

    Создаёт векторное представление текста для семантического поиска.

    Example:
    ```json
    POST /api/ml/embedding
    {
      "text": "Persönliches Budget für Menschen mit Behinderung"
    }
    ```

    Returns:
    ```json
    {
      "text": "Persönliches Budget...",
      "embedding": [0.123, -0.456, 0.789, ...],
      "dimension": 384
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready"
        )

    try:
        embedding = nlp_service.generate_embedding(request.text)
        if embedding is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate embedding"
            )

        return EmbeddingResponse(
            text=request.text[:100] + "..." if len(request.text) > 100 else request.text,
            embedding=embedding,
            dimension=len(embedding)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """
    Вычислить семантическое сходство между текстами

    Использует косинусное сходство embedding векторов.
    Результат: 0.0 (полностью разные) - 1.0 (идентичные).

    Example:
    ```json
    POST /api/ml/similarity
    {
      "text1": "Persönliches Budget",
      "text2": "Individuelles Budget für Teilhabe"
    }
    ```

    Returns:
    ```json
    {
      "text1": "Persönliches Budget",
      "text2": "Individuelles Budget für Teilhabe",
      "similarity": 0.87
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready"
        )

    try:
        similarity = nlp_service.calculate_similarity(
            request.text1,
            request.text2
        )

        return SimilarityResponse(
            text1=request.text1[:100],
            text2=request.text2[:100],
            similarity=round(similarity, 4)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Семантический поиск блоков

    Ищет блоки по смыслу, а не по ключевым словам.
    Использует embedding vectors для нахождения семантически похожих блоков.

    Example:
    ```json
    POST /api/ml/semantic-search
    {
      "query": "Wie bekomme ich finanzielle Unterstützung?",
      "limit": 5,
      "source": "SGB IX"
    }
    ```

    Returns:
    ```json
    {
      "query": "Wie bekomme ich finanzielle Unterstützung?",
      "results": [
        {
          "block_id": "sgb9_para29",
          "title": "§ 29 Persönliches Budget",
          "similarity": 0.82,
          "content": "..."
        }
      ],
      "total": 5
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready"
        )

    try:
        # Получить все блоки (с опциональным фильтром по source)
        blocks = await block_service.list_blocks(
            source=request.source,
            limit=1000  # Достаточно для семантического поиска
        )

        if not blocks:
            return SemanticSearchResponse(
                query=request.query,
                results=[],
                total=0
            )

        # Подготовить тексты для сравнения
        candidates = [f"{block.title} {block.content}" for block in blocks]

        # Найти наиболее похожие
        similar_indices = nlp_service.find_most_similar(
            request.query,
            candidates,
            top_k=request.limit
        )

        # Сформировать результаты
        results = []
        for idx, similarity in similar_indices:
            block = blocks[idx]
            results.append({
                "block_id": block.id,
                "title": block.title,
                "content": block.content[:200] + "..." if len(block.content) > 200 else block.content,
                "source": block.source,
                "type": block.type,
                "similarity": round(similarity, 4)
            })

        return SemanticSearchResponse(
            query=request.query,
            results=results,
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ner", response_model=NERResponse)
async def extract_entities_api(request: NERRequest):
    """
    Named Entity Recognition (NER)

    Извлекает именованные сущности из текста:
    - Персоны (PER)
    - Организации (ORG)
    - Локации (LOC)
    - Законы и юридические ссылки

    Example:
    ```json
    POST /api/ml/ner
    {
      "text": "Nach § 5 SGB IX haben Menschen mit Behinderung in Berlin..."
    }
    ```

    Returns:
    ```json
    {
      "text": "...",
      "entities": [
        {"text": "Berlin", "label": "LOC", "start": 50, "end": 56}
      ],
      "legal_references": ["§ 5", "SGB IX"]
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready"
        )

    try:
        entities = nlp_service.extract_entities(request.text)
        legal_refs = nlp_service.extract_legal_references(request.text)

        return NERResponse(
            text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            entities=entities,
            legal_references=legal_refs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify", response_model=ClassificationResponse)
async def classify_block(request: ClassificationRequest):
    """
    Автоматическая классификация блока

    Определяет тип и категорию блока на основе содержимого.
    Использует rule-based классификацию с ключевыми словами и NER.

    Типы блоков:
    - paragraph: Параграф закона
    - definition: Определение
    - procedure: Процедура/процесс
    - requirement: Требование/условие
    - right: Право/притязание
    - obligation: Обязанность
    - sanction: Санкция

    Категории:
    - employment: Трудоустройство
    - health: Здоровье
    - education: Образование
    - social_security: Социальное обеспечение
    - participation: Участие/интеграция
    - administration: Администрация

    Example:
    ```json
    POST /api/ml/classify
    {
      "text": "Menschen mit Behinderung haben Anspruch auf Leistungen...",
      "title": "§ 5 Leistungen zur Teilhabe"
    }
    ```

    Returns:
    ```json
    {
      "text": "Menschen mit Behinderung...",
      "type": "right",
      "category": "participation",
      "entities": [...],
      "confidence": 0.7
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready"
        )

    try:
        classification = nlp_service.classify_block(
            request.text,
            request.title
        )

        return ClassificationResponse(
            text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            type=classification["type"],
            category=classification["category"],
            entities=classification["entities"],
            confidence=classification["confidence"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    """
    Extractive summarization (резюмирование)

    Создаёт краткое резюме текста, выбирая наиболее важные предложения.

    Методы:
    - frequency: Выбирает предложения с наиболее частыми ключевыми словами
    - position: Выбирает первые N предложений

    Example:
    ```json
    POST /api/ml/summarize
    {
      "text": "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe. Diese umfassen Leistungen zur medizinischen Rehabilitation, zur Teilhabe am Arbeitsleben...",
      "max_sentences": 2,
      "method": "frequency"
    }
    ```

    Returns:
    ```json
    {
      "original_text": "Menschen mit Behinderung...",
      "summary": "Menschen mit Behinderung haben Anspruch auf Leistungen.",
      "compression_ratio": 0.25,
      "summary_points": [
        "Menschen mit Behinderung haben Anspruch auf Leistungen",
        "Leistungen umfassen medizinische Rehabilitation"
      ]
    }
    ```
    """
    if not nlp_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="NLP service not ready"
        )

    try:
        summary = nlp_service.summarize_text(
            request.text,
            max_sentences=request.max_sentences,
            method=request.method
        )

        summary_points = nlp_service.generate_summary_points(
            request.text,
            max_points=request.max_sentences + 2
        )

        compression_ratio = len(summary) / len(request.text) if request.text else 0

        return SummarizationResponse(
            original_text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            summary=summary,
            compression_ratio=round(compression_ratio, 2),
            summary_points=summary_points
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_nlp_status():
    """
    Статус NLP сервиса

    Проверяет готовность моделей NLP.

    Example:
    ```
    GET /api/ml/status
    ```

    Returns:
    ```json
    {
      "status": "ready",
      "spacy_model": "de_core_news_lg",
      "transformer_model": "paraphrase-multilingual-MiniLM-L12-v2",
      "initialized": true
    }
    ```
    """
    return {
        "status": "ready" if nlp_service.is_ready() else "not_ready",
        "spacy_model": nlp_service.spacy_model_name,
        "transformer_model": nlp_service.transformer_model_name,
        "initialized": nlp_service.initialized
    }
