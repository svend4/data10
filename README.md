# Система динамических информационных блоков (`data10`)

Модульная система для работы со структурированным контентом и законодательными текстами (в том числе немецким правом: SGB IX и др.), основанная на методологии переиспользуемых информационных блоков, графе зависимостей и автоматической сборке документов по правилам.

Основной методический документ: [`dynamic_content_blocks_methodology.md`](dynamic_content_blocks_methodology.md) (193 КБ, совпадает на `main` и ветке разработки).

---

## Возможности реализации (ветка `claude/review-repository-DMl4A`)

- **REST API на FastAPI** (`app/main.py`, `app/api/`): роутеры `blocks.py`, `documents.py`, `search.py`, `versions.py`, `bulk.py`, `ml.py`, `auth.py`, `audit.py`, `metrics.py`.
- **Хранение и граф связей**: MongoDB (`pymongo==4.6.1`, `motor==3.3.2`) для блоков, шаблонов и документов; Neo4j (`neo4j==5.15.0`) для графа связей; Redis (`redis==5.0.1`) для кэширования и rate limiting; Elasticsearch (`elasticsearch==8.11.1`) для полнотекстового и векторного kNN-поиска.
- **Сборка и экспорт документов**: условный движок правил (`RuleEngine`), шаблоны (в т.ч. `data/templates/widerspruch_template.json`), экспорт в Text, Markdown и DOCX (`python-docx==1.1.0`).
- **Версионирование и массовые операции**: история версий блоков, сравнение и откат; bulk-импорт/экспорт и переиндексация.
- **NLP и ML (`app/api/ml.py`)**: обработка немецких юридических текстов на базе `spaCy==3.7.2`, эмбеддинги `sentence-transformers==2.2.2` / `transformers==4.36.0` / `torch==2.1.2`, тематическое моделирование (`gensim`, `bertopic`), NER, автоклассификация и экстрактивное резюмирование.
- **Безопасность и эксплуатация**: JWT/API-ключи/RBAC (`pyjwt`, `passlib[bcrypt]`, `python-jose`), аудит-логирование, метрики Prometheus (`prometheus-client==0.19.0`), конфигурации мониторинга (`monitoring/`) и манифесты Kubernetes (`k8s/`).

---

## Структура репозитория

```text
data10/
├── dynamic_content_blocks_methodology.md   # Полная методология (193 464 байта)
├── app/
│   ├── main.py                             # Точка входа FastAPI
│   ├── config.py                           # Настройки (pydantic-settings)
│   ├── api/                                # REST-эндпоинты (auth, audit, blocks, bulk, documents, metrics, ml, search, versions)
│   ├── core/                               # Безопасность и базовые утилиты
│   ├── middleware/                         # Rate limiting, аудит, метрики
│   ├── models/                             # Pydantic-модели блоков, правил, документов, версий, аудита, auth
│   ├── repositories/                       # Neo4j, MongoDB, Elasticsearch, Redis
│   ├── services/                           # Бизнес-логика (Block, Rule, Assembly, Search, Cache, Version, NLP, Auth, Audit, Metrics)
│   └── utils/                              # Парсеры SGB и экспортёры
├── data/                                   # Примеры текстов (SGB IX), блоков и шаблонов (Widerspruch)
├── docker/                                 # Dockerfile и конфигурация контейнера
├── docker-compose.yml                      # Инфраструктура: neo4j:5.15.0, mongo:7.0, elasticsearch:8.11.1, redis:7.2-alpine
├── k8s/                                    # Манифесты Kubernetes (Deployment, StatefulSet, HPA, Ingress)
├── monitoring/                             # Prometheus, alert rules, Grafana dashboard
├── scripts/                                # Скрипты импорта, quickstart, setup_nlp_models.py, demo_ml_features.py
├── examples/                               # Примеры работы с API и ML-поиском (01–05)
├── tests/                                  # Модульные, интеграционные и e2e-тесты (pytest.ini)
├── docs/                                   # PROJECT_OVERVIEW.md, DEPLOYMENT_GUIDE.md, ml_usage_guide.md, PHASE3_SUMMARY.md, PHASE4_SUMMARY.md
├── CONTRIBUTING.md
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── LICENSE                                 # GNU AGPL v3.0 (синхронизировано с main)
```

---

## Быстрый старт

Требуется Python 3.10+ и Docker / Docker Compose.

```bash
git clone https://github.com/svend4/data10.git
cd data10
cp .env.example .env

# Поднять БД и кэш (Neo4j, MongoDB, Elasticsearch, Redis)
docker compose up -d

# Установить Python-зависимости
pip install -r requirements.txt

# Демонстрационная инициализация и проверка
python scripts/quickstart.py

# Запуск API-сервера
uvicorn app.main:app --reload
```

> [!NOTE]
> В `docker-compose.yml` сервисы `neo4j`, `mongodb`, `elasticsearch` и `redis` активны по умолчанию, а блоки `app` и `celery-worker` закомментированы для локального запуска API через `uvicorn`.

- Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## Тестирование и качество кода

```bash
pytest
pytest tests/unit/
pytest tests/integration/
```

Dev-инструменты из `requirements-dev.txt` и `setup.cfg`: `pytest`, `pytest-cov`, `pytest-asyncio`, `black`, `flake8`, `mypy`, `pre-commit`.

## Документация

- [`dynamic_content_blocks_methodology.md`](dynamic_content_blocks_methodology.md) — полная методология
- [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) — обзор проекта
- [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) — руководство по развёртыванию (Docker Compose, Kubernetes, мониторинг)
- [`docs/ml_usage_guide.md`](docs/ml_usage_guide.md) — руководство по NLP/ML-эндпоинтам
- [`docs/BRANCH_README_ORIG.md`](docs/BRANCH_README_ORIG.md) — исходный `README.md` ветки `claude/review-repository-DMl4A`

## Лицензия

В ветке `main` проект распространяется под лицензией **GNU Affero General Public License v3.0 (AGPL-3.0)** — см. [`LICENSE`](LICENSE). (В исходной ветке `claude/review-repository-DMl4A` присутствовал файл лицензии MIT.)
