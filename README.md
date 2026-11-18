# Система динамических информационных блоков (`data10`)

## Назначение проекта

Репозиторий `data10` посвящён проектированию и реализации **Системы динамических информационных блоков (Dynamic Content Blocks System)** — модульной платформы для хранения, связывания и автоматической сборки структурированных и законодательных документов по правилам и условиям (на примере немецкого социального законодательства SGB IX и шаблонов заявлений `Widerspruch` / `Antrag`).

Основная концепция проекта — «Lego-конструктор» информации:
- **Атомарность и переиспользование**: контент разбивается на независимые смысловые блоки с метаданными.
- **Графовые зависимости и условная логика**: связи и правила активации блоков моделируются в виде ориентированного ациклического графа (DAG) и семантической сети.
- **Динамическое встраивание и эскалация детализации**: новые фрагменты автоматически встраиваются в нужный уровень иерархии.
- **Автоматическая сборка и экспорт**: генерация готовых документов из шаблонов с экспортом в DOCX, Markdown и TXT.

> **Важно о структуре репозитория:** ветка `main` содержит фундаментальное методологическое руководство [`dynamic_content_blocks_methodology.md`](dynamic_content_blocks_methodology.md) и файл лицензии, тогда как прикладная кодовая база (4-фазное приложение на Python/FastAPI) расположена в ветке `claude/review-repository-DMl4A`.

## Архитектура и основные компоненты

### 1. Методологическая база (ветка `main`)

Файл [`dynamic_content_blocks_methodology.md`](dynamic_content_blocks_methodology.md) (193 КБ, 5946 строк) описывает:
- **Теоретические основы**: теория графов (DAG, топологическая сортировка Кана, семантические сети `IS-A` / `PART-OF` / `RELATED-TO`, Property Graphs в Neo4j), формальная логика (логика высказываний и логика первого порядка).
- **Алгоритмы и паттерны**: паттерн `Composite` (`ContentComponent`, `TextBlock`, `Section`), подходы к автоматическому встраиванию контента и эскалации детализации, применение к законодательным текстам (SGB IX).
- **NLP и ML-модели**: тематическое моделирование (BERTopic / Gensim), извлечение именованных сущностей для немецких юридических текстов (spaCy `de_core_news_lg` + `entity_ruler` для `§`, `Az.`, сроков и ведомств), семантический поиск на векторных представлениях (`sentence-transformers`, `paraphrase-multilingual-MiniLM-L12-v2`).
- **Архитектура, развёртывание и дорожная карта**: от прототипа к распределённой производственной системе.

### 2. Четырёхфазная прикладная реализация (ветка `claude/review-repository-DMl4A`)

В ветке `claude/review-repository-DMl4A` реализован бэкенд-сервис **Dynamic Content Blocks API** (`version="4.0.0"` в `app/main.py`):

- **Точка входа (`app/main.py`)**: FastAPI-приложение с OpenAPI/Swagger (`/docs`), ReDoc (`/redoc`), расширенным `/health` (мониторинг латентности API, MongoDB, Neo4j, Redis, Elasticsearch) и `/metrics`.
- **Middleware (`app/middleware/`)**:
  - `MetricsMiddleware` — сбор метрик Prometheus.
  - `AuditMiddleware` — аудит-логирование операций.
  - `RateLimitMiddleware` (`RateLimiter`) — ограничение частоты запросов по алгоритму скользящего окна (по умолчанию `100` запросов за `60` с, с поддержкой Redis и fallback в память).
- **API-роутеры (`app/api/`, 9 модулей, 50+ эндпоинтов)**:
  - `blocks.py` (`/api/blocks`) — управление информационными блоками;
  - `documents.py` (`/api/documents`) — сборка документов из шаблонов и экспорт;
  - `search.py` (`/api/search`) — полнотекстовый (Elasticsearch) и семантический (kNN) поиск;
  - `versions.py` (`/api/versions`) — история изменений, сравнение (`diff`) и откат версий блоков;
  - `bulk.py` (`/api/bulk`) — массовые импорт/экспорт/обновление и переиндексация;
  - `ml.py` (`/api/ml`) — NLP-анализ, NER, эмбеддинги, классификация, суммаризация и расчёт сходства;
  - `auth.py` (`/api`) — аутентификация (JWT, API-ключи, RBAC);
  - `audit.py` (`/api`) — запросы к журналу аудита;
  - `metrics.py` (`/metrics`) — экспорт метрик для Prometheus.
- **Сервисный слой (`app/services/`)**:
  - `block_service.py`, `assembly_service.py`, `rule_engine.py`, `search_service.py`, `cache_service.py`, `version_service.py`, `nlp_service.py`, `auth_service.py`, `audit_service.py`, `metrics_service.py`.
- **Уровень данных и модели**: `app/models/`, `app/repositories/`, `app/core/`, `app/utils/`.

## Стек технологий и структура каталогов

### Технологический стек (по ветке `claude/review-repository-DMl4A`)

- **Веб-фреймворк и валидация:** Python 3.10+, `fastapi==0.108.0`, `uvicorn[standard]==0.25.0`, `pydantic==2.5.3`, `pydantic-settings==2.1.0`.
- **Базы данных и поиск (`docker-compose.yml` и `requirements.txt`):**
  - **Neo4j `5.15.0`** (с плагином APOC; драйверы `neo4j==5.15.0`, `py2neo==2021.2.3`) — граф связей и зависимостей блоков;
  - **MongoDB `7.0`** (`pymongo==4.6.1`, `motor==3.3.2`) — хранение блоков, документов и шаблонов;
  - **Elasticsearch `8.11.1`** (`elasticsearch==8.11.1`) — полнотекстовый и векторный (kNN) поиск;
  - **Redis `7.2-alpine`** (`redis==5.0.1`, `celery==5.3.4`) — кеширование, rate limiting и брокер фоновых задач.
- **NLP и ML:** `spacy==3.7.2` (`de_core_news_lg`), `sentence-transformers==2.2.2` (384-мерные эмбеддинги), `transformers==4.36.0`, `torch==2.1.2`, `bertopic==0.16.0`, `gensim==4.3.2`, `scikit-learn==1.3.2`, `numpy==1.26.2`, `pandas==2.1.4`.
- **Обработка документов и шаблоны:** `python-docx==1.1.0`, `PyPDF2==3.0.1`, `pdfplumber==0.10.3`, `beautifulsoup4==4.12.2`, `lxml==5.1.0`, `jinja2==3.1.2`.
- **Безопасность и мониторинг:** `pyjwt==2.8.0`, `passlib[bcrypt]==1.7.4`, `python-jose[cryptography]==3.3.0`, `bcrypt==4.1.2`, `prometheus-client==0.19.0`.
- **Инфраструктура, тестирование и качество кода:** Docker Compose, Kubernetes (`k8s/`), Prometheus/Grafana (`monitoring/`), `pytest==7.4.3`, `pytest-cov`, `pytest-asyncio`, `black`, `flake8`, `mypy`, `pre-commit`.

### Структура каталогов

Ветка `main`:

```text
data10/
├── LICENSE                              # Лицензия GNU AGPLv3 (в ветке main)
├── README.md                            # Описание репозитория
└── dynamic_content_blocks_methodology.md # Методология динамических информационных блоков (193 КБ, 5946 строк)
```

Ветка `claude/review-repository-DMl4A` (полная структура реализации):

```text
data10/
├── app/                                 # FastAPI-приложение (api, core, middleware, models, repositories, services, utils)
├── data/                                # Данные (raw, processed, samples)
├── docker/                              # Dockerfile и конфигурация контейнеров
├── docs/                                # Дополнительная документация
├── examples/                            # Примеры использования на Python (01_create_blocks.py и др.)
├── k8s/                                 # Манифесты Kubernetes (7 файлов: HPA, Ingress, StatefulSets и др.)
├── monitoring/                          # Конфигурация Prometheus и дашборды Grafana
├── scripts/                             # Скрипты автоматизации (quickstart.py, import_sgb9.py и др.)
├── tests/                               # Тесты (unit, integration, e2e)
├── docker-compose.yml                   # Сервисы Neo4j, MongoDB, Elasticsearch, Redis
├── requirements.txt                     # Основные зависимости Python
├── requirements-dev.txt                 # Зависимости для разработки и тестирования
├── pytest.ini                           # Конфигурация pytest
├── setup.cfg                            # Настройки инструментов кода
├── CONTRIBUTING.md                      # Руководство для контрибьюторов
└── .env.example                         # Пример переменных окружения
```

### Запуск (для ветки `claude/review-repository-DMl4A`)

> Команды ниже относятся к ветке `claude/review-repository-DMl4A`, где размещён исходный код и `docker-compose.yml`:

```bash
cp .env.example .env
docker-compose up -d
pip install -r requirements.txt
python scripts/quickstart.py
# или запуск API вручную:
uvicorn app.main:app --reload
```

## Ветки и статус разработки

- **`main`** — базовая ветка, содержащая методологическое руководство `dynamic_content_blocks_methodology.md`, краткий обзор и файл `LICENSE` (AGPLv3).
- **`claude/review-repository-DMl4A`** — ветка с завершённой 4-фазной реализацией приложения на FastAPI:
  - *Phase 1 (MVP)*: парсинг SGB IX, Neo4j, MongoDB, движок правил, сборка и экспорт документов (`DOCX`/`MD`/`TXT`), базовое REST API и Docker Compose.
  - *Phase 2 (Advanced Features)*: Elasticsearch, Redis-кеширование, версионирование с diff/откатом, bulk-операции.
  - *Phase 3 (AI/ML Integration)*: `NLPService` на spaCy, 384-мерные семантические эмбеддинги, kNN-поиск в Elasticsearch, автоклассификация и суммаризация.
  - *Phase 4 (Production & Scale)*: JWT/API-ключи/RBAC/multi-tenancy, rate limiting, аудит-логирование, метрики Prometheus/Grafana и манифесты Kubernetes.
- **Открытые Pull Requests:** отсутствуют (на момент анализа).

## Лицензия

Обратите внимание на различие файлов лицензий между ветками:
- В ветке **`main`** размещена лицензия **GNU Affero General Public License v3.0 (AGPL-3.0)** (файл `LICENSE`).
- В ветке **`claude/review-repository-DMl4A`** размещена лицензия **MIT License** (`Copyright (c) 2026 Dynamic Content Blocks System`, файл `LICENSE`).
