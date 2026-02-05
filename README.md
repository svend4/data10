# Dynamic Content Blocks System

**Система динамических информационных блоков для законодательных текстов и структурированного контента**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Описание

Модульная система для работы со структурированным контентом, основанная на концепции переиспользуемых информационных блоков с автоматической сборкой документов по правилам и условиям.

**Ключевые возможности:**
- 🧩 Модульные блоки контента с метаданными
- 🔗 Граф зависимостей и семантических связей (Neo4j)
- 🤖 Автоматическая сборка документов по правилам
- 🔍 Полнотекстовый поиск с Elasticsearch (fuzzy, highlights, suggestions)
- 🧠 **AI/ML интеграция**: Semantic search, NER, auto-classification, summarization
- 🎯 **Semantic embeddings** (384-dim) для концептуального поиска
- 📊 Условная логика (rule engine) с операторами и группами
- 🌳 Динамическая иерархия и вложенность
- 🔄 Версионирование с полной историей изменений
- ⚡ Redis кэширование для производительности
- 📦 Bulk operations для массовых операций
- 📄 Экспорт в DOCX, Markdown, Text

## Целевые применения

- **Юридические фирмы**: автоматизация составления Widerspruch, Antrag и других документов
- **Государственные органы**: управление законодательной базой
- **Образование**: интерактивные учебные материалы по праву
- **Корпорации**: управление политиками и процедурами
- **Новостные агентства**: кластеризация и автоматическая генерация summary

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│             FastAPI REST API (OpenAPI/Swagger)                  │
│   /blocks  /documents  /search  /versions  /bulk  /ml          │
├─────────────────────────────────────────────────────────────────┤
│  BlockService │ AssemblyService │ SearchService │ CacheService │
│  RuleEngine   │ VersionService  │ ExportService │ NLPService   │
├─────────────────────────────────────────────────────────────────┤
│  Neo4j Graph │ MongoDB Docs │ Elasticsearch + Embeddings       │
│  (Relations) │ (Blocks/Docs)│  (Search + kNN) │ Redis Cache   │
└─────────────────────────────────────────────────────────────────┘
```

**Технологический стек:**
- **Backend**: Python 3.10+, FastAPI, Pydantic, async/await
- **Databases**:
  - Neo4j 5.x (графы связей, DAG, relationships)
  - MongoDB 6.x (блоки, документы, шаблоны)
  - Elasticsearch 8.x (полнотекстовый поиск, немецкий анализатор)
  - Redis 7.x (кэширование, TTL, counters)
- **Document Processing**: python-docx, PyPDF2, BeautifulSoup
- **NLP/ML**: spaCy (de_core_news_lg), Transformers, sentence-transformers
- **Infrastructure**: Docker Compose, GitHub Actions CI/CD

## Быстрый старт

### Требования
- Python 3.10+
- Docker & Docker Compose
- 8GB RAM минимум (16GB рекомендуется для Elasticsearch)

### Автоматическая установка (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourusername/data10.git
cd data10

# 2. Копировать конфигурацию
cp .env.example .env

# 3. Запустить инфраструктуру
docker-compose up -d

# 4. Подождать пока службы запустятся (~30 секунд)
sleep 30

# 5. Установить зависимости
pip install -r requirements.txt

# 6. Запустить quickstart (всё в одной команде!)
python scripts/quickstart.py
```

Quickstart автоматически:
- ✅ Проверит все службы (MongoDB, Neo4j, Elasticsearch, Redis)
- ✅ Импортирует SGB IX образцы
- ✅ Создаст Widerspruch template
- ✅ Соберёт пример документа
- ✅ Экспортирует в TXT, MD, DOCX

### Ручная установка

```bash
# После шагов 1-5 выше:

# Импортировать SGB IX данные
python scripts/import_sgb9.py --file data/samples/sgb9_sample.txt

# Импортировать Widerspruch template
python scripts/import_widerspruch_template.py

# Запустить API сервер
uvicorn app.main:app --reload
```

### Доступ

- **API**: http://localhost:8000
- **Документация (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Проверка установки

```bash
# Проверить health всех служб
curl http://localhost:8000/health

# Должен вернуть:
# {
#   "status": "healthy",
#   "services": {
#     "api": {"status": "up"},
#     "mongodb": {"status": "up", "latency_ms": 2.5},
#     "neo4j": {"status": "up", "latency_ms": 15.3},
#     "redis": {"status": "up", "latency_ms": 1.2},
#     "elasticsearch": {"status": "up", "latency_ms": 8.7}
#   }
# }
```

## Структура проекта

```
data10/
├── app/                          # Основное приложение
│   ├── models/                   # Модели данных
│   ├── services/                 # Бизнес-логика
│   ├── repositories/             # Работа с БД
│   ├── api/                      # API endpoints
│   └── utils/                    # Утилиты
├── tests/                        # Тесты
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                      # Скрипты
├── data/                         # Данные
│   ├── raw/                      # Исходные тексты
│   ├── processed/                # Обработанные блоки
│   └── samples/                  # Примеры
├── docker/                       # Docker конфигурация
├── docs/                         # Документация
└── dynamic_content_blocks_methodology.md  # Полная методология
```

## Документация

📚 **[Полная методология](./dynamic_content_blocks_methodology.md)** - comprehensive guide (193 KB, 5946 строк):
- Теоретические основы (теория графов, семантические сети)
- Классические алгоритмы и паттерны проектирования
- Технологический стек и архитектура
- Практическая реализация
- Deployment и масштабирование
- Roadmap на 12 месяцев

## Примеры использования

### 1. Quickstart - одна команда для старта
```bash
python scripts/quickstart.py
```
Автоматически:
- Проверит службы (MongoDB, Neo4j, Elasticsearch, Redis)
- Импортирует SGB IX образцы
- Создаст Widerspruch шаблон
- Соберёт пример документа
- Экспортирует в TXT, MD, DOCX

### 2. Полнотекстовый поиск
```bash
# Поиск блоков
curl "http://localhost:8000/api/search?q=Teilhabe&source=SGB+IX&limit=10"

# Автодополнение
curl "http://localhost:8000/api/search/suggest?prefix=Leist"

# Похожие блоки
curl "http://localhost:8000/api/search/similar/sgb9_para5"
```

### 3. Версионирование
```bash
# История изменений
curl "http://localhost:8000/api/versions/sgb9_para5/history"

# Сравнение версий
curl "http://localhost:8000/api/versions/sgb9_para5/compare?old_version=1&new_version=2"

# Откат к версии
curl -X POST "http://localhost:8000/api/versions/sgb9_para5/restore" \
  -H "Content-Type: application/json" \
  -d '{"version": 2}'
```

### 4. Bulk operations
```bash
# Массовый импорт
curl -X POST "http://localhost:8000/api/bulk/import" \
  -F "file=@blocks.json"

# Массовое обновление
curl -X POST "http://localhost:8000/api/bulk/update" \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {"block_id": "block1", "update_data": {"title": "New Title"}},
      {"block_id": "block2", "update_data": {"content": "New Content"}}
    ]
  }'

# Массовый экспорт
curl -X POST "http://localhost:8000/api/bulk/export" \
  -H "Content-Type: application/json" \
  -d '["block1", "block2"]' > export.json
```

### 5. Сборка документов из шаблонов
```bash
# Использовать готовый Widerspruch шаблон
curl -X POST "http://localhost:8000/api/documents/assemble" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "widerspruch_standard_v1",
    "title": "Widerspruch - Max Mustermann",
    "context": {
      "VORNAME": "Max",
      "NACHNAME": "Mustermann",
      "BESCHEID_DATUM": "15.01.2024",
      "grund_type": "rechtsverletzung"
    }
  }'

# Экспорт документа
curl "http://localhost:8000/api/documents/{document_id}/export/docx" \
  --output widerspruch.docx
```

### 6. AI/ML операции
```bash
# Semantic search (поиск по смыслу, а не ключевым словам)
curl -X POST "http://localhost:8000/api/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Welche Leistungen gibt es für Menschen mit Behinderung?",
    "source": "SGB IX",
    "limit": 5,
    "min_score": 0.6
  }'

# Auto-classification блока
curl -X POST "http://localhost:8000/api/ml/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Menschen mit Behinderung haben Anspruch auf Leistungen...",
    "title": "§ 5 Leistungen zur Teilhabe"
  }'

# Summarization (резюмирование)
curl -X POST "http://localhost:8000/api/ml/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long legal text...",
    "max_sentences": 3,
    "method": "frequency"
  }'

# Named Entity Recognition
curl -X POST "http://localhost:8000/api/ml/ner" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Nach § 5 SGB IX haben Menschen mit Behinderung in Berlin..."
  }'

# Text analysis (полный анализ)
curl -X POST "http://localhost:8000/api/ml/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your German legal text here..."}'

# Similarity между текстами
curl -X POST "http://localhost:8000/api/ml/similarity" \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "Persönliches Budget",
    "text2": "Individuelles Budget für Teilhabe"
  }'
```

### 7. Python примеры
```python
# См. полные примеры в examples/
python examples/01_create_blocks.py      # Создание блоков
python examples/02_assemble_document.py  # Сборка документа
python examples/03_export_document.py    # Экспорт в форматы
```

## Roadmap

### Phase 1: MVP ✅ Completed (Jan 2026)
- [x] Базовый парсинг SGB IX с regex patterns
- [x] Neo4j граф с основными связями (PARENT, CHILD, REFERENCES)
- [x] MongoDB хранилище блоков с индексами
- [x] Rule engine с условной логикой (==, >, in, contains, AND/OR)
- [x] Базовая сборка документов из templates
- [x] Экспорт в DOCX, Markdown, Text
- [x] REST API с FastAPI и OpenAPI документацией
- [x] Docker Compose инфраструктура
- [x] Готовый Widerspruch template с примерами
- [x] Quickstart script для быстрого старта
- [x] Integration tests для всех сервисов

**Commits**: eee2609 (setup), 2b09719 (MVP), 44a0ac0 (Phase 1), c4bd669 (Phase 1.5)

### Phase 2: Advanced Features ✅ Completed (Feb 2026)
- [x] **Elasticsearch** полнотекстовый поиск
  - Немецкий анализатор для юридических текстов
  - Fuzzy matching, highlighting, autocomplete
  - More Like This для похожих блоков
  - Bulk reindexing
- [x] **Redis** кэширование
  - TTL кэши для блоков (1h), документов (30m), поиска (10m)
  - Counters и статистика
  - Pattern-based invalidation
- [x] **Версионирование блоков**
  - Полная история изменений
  - Сравнение версий (diff)
  - Откат к предыдущим версиям
  - Audit trail с авторами
- [x] **Bulk operations**
  - Массовое создание, обновление, удаление
  - JSON импорт/экспорт
  - Batch reindexing
- [x] Расширенный health check (все сервисы)
- [x] API endpoints: /search, /versions, /bulk

**Commits**: e774bda (Search & Cache), f8437fa (Versioning), e498d8b (Bulk Ops)

**Statistics**:
- **38+ API endpoints** across 6 routers
- **7 services**: Block, Rule, Assembly, Search, Cache, Version, NLP
- **4 databases**: Neo4j, MongoDB, Elasticsearch (with embeddings), Redis
- **10+ scripts** для automation
- **60+ integration tests**

### Phase 3: AI/ML Integration ✅ Completed (Feb 2026)
- [x] **NLP Service** с spaCy (de_core_news_lg)
  - Немецкий языковой анализ для юридических текстов
  - Tokenization, lemmatization, POS tagging
  - Named Entity Recognition (NER)
  - Legal reference extraction (§, Art., Abs., Satz)
- [x] **Semantic embeddings** (sentence-transformers)
  - 384-dimensional vectors для текстов
  - Batch generation для производительности
  - Multilingual model (German + English)
- [x] **Semantic search** с Elasticsearch
  - kNN search на embedding векторах
  - Cosine similarity scoring (0-1)
  - Hybrid search (keyword + semantic)
- [x] **Auto-classification** (rule-based)
  - Block types: paragraph, definition, procedure, requirement, right, obligation, sanction
  - Categories: employment, health, education, social_security, participation, administration
- [x] **Extractive summarization**
  - Frequency-based: важнейшие предложения
  - Position-based: первые N предложений
  - Summary points generation
- [x] **Similarity scoring** с embeddings
  - Calculate text similarity (0-1)
  - Find most similar blocks
- [x] **ML API endpoints**: /analyze, /embedding, /similarity, /semantic-search, /ner, /classify, /summarize

**Commits**: 6c5c16a (NLP & Semantic Search)

### Phase 4: Production & Scale 📋 Planned (Q3 2026)
- [ ] Web UI (React/Vue)
- [ ] Authentication & Authorization (OAuth2, JWT)
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Metrics & monitoring (Prometheus, Grafana)
- [ ] Kubernetes deployment
- [ ] Performance optimization
- [ ] Multi-tenancy

[Полный roadmap в документации](./dynamic_content_blocks_methodology.md#12-roadmap-и-будущее-развитие)

## Тестирование

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Только unit-тесты
pytest tests/unit/

# Только интеграционные
pytest tests/integration/
```

## Разработка

```bash
# Установить dev-зависимости
pip install -r requirements-dev.txt

# Линтеры
black app/
flake8 app/
mypy app/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Лицензия

MIT License - см. [LICENSE](LICENSE)

## Контакты

- **Автор методологии**: Claude (Anthropic)
- **Версия**: 1.0
- **Дата**: 04.02.2026

## Благодарности

Проект основан на современных подходах к работе со структурированным контентом:
- Теория графов и семантические сети
- Design patterns (Composite, Strategy, Observer, Chain of Responsibility)
- Архитектурные паттерны (Microservices, Event-Driven, CQRS, DDD)
- NLP/ML методы для обработки естественного языка

---

**Статус проекта**: Active Development | Phase 3 Complete ✅
**Версия**: 3.0.0 (Phase 3: AI/ML Integration)
**Последнее обновление**: 05.02.2026

**Основные достижения Phase 3**:
- 🧠 NLP Service с spaCy для немецкого языка
- 🎯 Semantic search с embeddings (384-dim vectors)
- 🤖 Auto-classification блоков (types & categories)
- 📝 Extractive summarization для юридических текстов
- 🔍 Named Entity Recognition (NER)
- 📊 8 новых ML API endpoints
- 🚀 Production-ready with 38+ API endpoints

**Следующий этап**: Phase 4 - Production & Scale (Web UI, Auth, Monitoring)
