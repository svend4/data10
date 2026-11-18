# Технический аудит кода `svend4/data10` (Wave 2)

- **Ветка аудита:** `audit/code-review` (создана от `consolidate/ready-for-main`, базовый коммит `a025efe96d84474cde0e238ab0a0024e78478c67`)
- **Проверенные файлы и директории:** `app/main.py`, `app/config.py`, `app/core/security.py`, `app/api/auth.py`, `app/repositories/*.py`, `app/services/auth_service.py`, `app/services/audit_service.py`, `app/services/block_service.py`, `app/services/cache_service.py`, `app/services/nlp_service.py`, `app/services/search_service.py`, `app/services/version_service.py`, `app/middleware/rate_limiter.py`, `.env.example`, `requirements.txt`, `requirements-dev.txt`, `docker-compose.yml`, `docker/Dockerfile`, `.dockerignore`, `k8s/` (`README.md`, `api-deployment.yaml`, `configmap.yaml`, `secrets.yaml`, `mongodb-statefulset.yaml`, `hpa.yaml`, `ingress.yaml`), `.github/workflows/ci.yml`, `pytest.ini`, `setup.cfg`, `tests/unit/test_main.py`, `tests/unit/test_security.py`, `tests/integration/conftest.py`.

---

## 1. Управление конфигурацией и переменными окружения

В проекте отсутствует единый источник конфигурации: настройки размазаны между `app/config.py` (`Settings(BaseSettings)`), прямыми вызовами `os.getenv(...)` и жёстко зашитыми значениями по умолчанию.

1. **Расхождение имён переменных для Elasticsearch и Redis**:
   - `app/config.py` объявляет `ELASTICSEARCH_HOST`, `ELASTICSEARCH_PORT`, `ELASTICSEARCH_INDEX`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, однако `app/repositories/elasticsearch_repo.py` читает `os.getenv("ELASTICSEARCH_URI", ...)`, `app/repositories/redis_repo.py` — `os.getenv("REDIS_HOST" / "REDIS_PORT" / "REDIS_DB" / "REDIS_PASSWORD")`, а `k8s/configmap.yaml` и `k8s/api-deployment.yaml` вообще передают `ELASTICSEARCH_URL` и `REDIS_URL`.
   - В `docker-compose.yml` закомментированный сервис `app` передаёт `ELASTICSEARCH_HOST=elasticsearch` и `REDIS_HOST=redis`, из-за чего `elasticsearch_repo.py` в Docker продолжит обращаться к `http://localhost:9200`.
2. **Игнорирование `settings` в `auth_service` и `audit_service`**:
   - В `app/main.py` при старте вызываются `await auth_service.initialize()` и `await audit_service.initialize()` без параметров. Обе функции имеют сигнатуру `initialize(mongo_uri: str = "mongodb://localhost:27017", db_name: str = "content_blocks")`, поэтому даже при переопределении `MONGODB_URI` / `MONGODB_DB` эти сервисы подключаются к `localhost`.
3. **Раздельные клиенты и модели**:
   - `app/services/nlp_service.py` читает `SPACY_MODEL` и `SENTENCE_TRANSFORMER_MODEL` напрямую через `os.getenv`, дублируя `app/config.py`.
   - В `app/config.py` используется устаревший для Pydantic v2 стиль `class Config:` (в `requirements.txt` указаны `pydantic==2.5.3` и `pydantic-settings==2.1.0`, где предпочтительнее `model_config = SettingsConfigDict(...)`).
   - В `app/main.py` метаданные `FastAPI(..., version="4.0.0")` расходятся с `GET /` (`"version": "1.0.0"`) и `APP_VERSION="1.0.0"` в `app/config.py`.

---

## 2. Безопасность: секреты по умолчанию, JWT и CORS

1. **Эфемерный `SECRET_KEY` в `app/core/security.py` (до правки)**:
   - Строка `SECRET_KEY = secrets.token_urlsafe(32)  # In production, load from environment` не читала переменные окружения. При наличии нескольких реплик (`replicas: 3` в `k8s/api-deployment.yaml`) или перезапуске контейнера каждый экземпляр генерировал собственный ключ, делая межподовую проверку JWT неработоспособной.
2. **Ошибка перехвата исключений PyJWT в `app/core/security.py` (до правки)**:
   - В файле импортирован `import jwt` (`pyjwt==2.8.0`), однако в `decode_token` перехватывалось `except jwt.JWTError:` (исключение из `python-jose`, отсутствующее в PyJWT). При передаче невалидного, пустого, повреждённого или `None` токена (например, в сценариях `tests/unit/test_security.py`) возникал `AttributeError: module 'jwt' has no attribute 'JWTError'`.
3. **Открытые секреты и слабые пароли в репозитории**:
   - `k8s/secrets.yaml` содержит реальные Base64-значения учётных данных и ключа подписи (`admin` / `password`, `neo4j` / `password`, `super-secret-jwt-key-change-in-production`, `admin@example.com` / `adminpassword`), закоммиченные в Git.
   - `app/config.py` задаёт дефолтный пароль `NEO4J_PASSWORD: str = "password"`.
   - `docker-compose.yml` задаёт `NEO4J_AUTH=neo4j/password`, `MONGO_INITDB_ROOT_PASSWORD=password` и отключает безопасность Elasticsearch (`xpack.security.enabled=false`).
4. **CORS и аутентификация API-ключом**:
   - В `app/main.py` настроено `allow_origins=["*"]` одновременно с `allow_credentials=True` (нарушение спецификации CORS и риск при использовании cookie/авторизации); аналогично в `k8s/ingress.yaml` включён `cors-allow-origin: "*"`.
   - В `app/api/auth.py` зависимость `get_current_user_flexible` использует `security = HTTPBearer()` (где `auto_error=True` по умолчанию), из-за чего запрос с одним лишь заголовком `X-API-Key` без `Authorization: Bearer ...` будет отклонён до входа в обработчик.
   - `app/core/security.py` использует `datetime.utcnow()`, устаревший в Python 3.12+.

---

## 3. Зависимости (`requirements.txt`, `requirements-dev.txt`)

- Все пакеты зафиксированы точными версиями (`==`), что повышает воспроизводимость, но хэш-проверка (`--require-hashes` / lockfile) отсутствует.
- **Дублирование JWT-библиотек**: в `requirements.txt` одновременно присутствуют `pyjwt==2.8.0` и `python-jose[cryptography]==3.3.0`.
- **Риск `passlib` + `bcrypt`**: указаны `passlib[bcrypt]==1.7.4` и `bcrypt==4.1.2`. Версия `passlib==1.7.4` имеет известную несовместимость с `bcrypt>=4.1` (отсутствует `bcrypt.__about__`, а длинные пароли >72 байт, например `test_hash_long_password` с `"A" * 1000`, вызывают `ValueError` в `bcrypt>=4`).
- **Смешение слоёв зависимостей**: в основном `requirements.txt` находятся не только runtime-пакеты API, но и тяжёлый ML-стек (`torch==2.1.2`, `transformers==4.36.0`, `sentence-transformers==2.2.2`, `spacy==3.7.2`, `bertopic==0.16.0`, `gensim==4.3.2`), а также dev-инструменты (`pytest`, `pytest-cov`, `pytest-asyncio`, `black`, `flake8`, `mypy`, `pre-commit`), тогда как часть dev-утилит вынесена в `requirements-dev.txt`.

---

## 4. Готовность Docker и Kubernetes

### Docker (`docker-compose.yml`, `docker/Dockerfile`, `.dockerignore`)
- **Образ (`docker/Dockerfile`)**: одноэтапный `python:3.10-slim` с `build-essential`, `git`, установкой всех пакетов из `requirements.txt` и загрузкой `de_core_news_lg` (~560 МБ), что даёт многогигабайтный образ без multi-stage сборки. Плюс: используется непривилегированный пользователь `appuser` (UID 1000) и `HEALTHCHECK`.
- **Healthcheck**: `curl -f http://localhost:8000/health` не выявляет деградацию БД, так как `GET /health` возвращает HTTP `200` даже со статусом `"degraded"`.
- **Compose**: сервисы `app` и `celery-worker` закомментированы; отсутствуют контейнеры `healthcheck` и `depends_on: condition: service_healthy`.

### Kubernetes (`k8s/`)
1. **Неполный комплект манифестов**: на схеме в `k8s/README.md` описаны MongoDB, Neo4j, Redis и Elasticsearch, но в каталоге `k8s/` присутствует только `mongodb-statefulset.yaml` (манифестов для Neo4j, Redis, Elasticsearch нет).
2. **Сломанная сквозная конфигурация БД**:
   - `k8s/mongodb-statefulset.yaml` включает аутентификацию через `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD`, однако `k8s/configmap.yaml` передаёт `MONGODB_URI: "mongodb://mongodb:27017"` без логина/пароля, а `mongo_repo.py` игнорирует отдельные `MONGODB_USERNAME` / `MONGODB_PASSWORD`.
   - `k8s/api-deployment.yaml` передаёт `REDIS_URL` и `ELASTICSEARCH_URL`, которые не читаются кодом репозиториев (`REDIS_HOST`, `ELASTICSEARCH_URI`).
   - При несовпадении настроек Redis `RateLimiter` переходит на `in-memory` счётчик в каждом из 3–10 подов (`replicas: 3`, `HPA maxReplicas: 10`), делая rate limiting локальным на под.
3. **Хранилище и пробы**:
   - `ml-models-pvc` запрашивает `accessModes: [ReadOnlyMany]` в `storageClassName: standard` и монтируется в `/app/ml_models`, тогда как `app/config.py` ожидает `MODELS_DIR=./data/models`.
   - `livenessProbe` и `readinessProbe` используют один и тот же `/health`, который не отдаёт `503` при падении обязательных БД.

---

## 5. Тестирование и CI/CD (`.github/workflows/ci.yml`, `pytest.ini`, `setup.cfg`, `tests/`)

- **Триггеры CI**: `push: branches: [ main, develop, claude/* ]`, `pull_request: branches: [ main, develop ]` — ветки `consolidate/*` и `audit/*` не запускают CI.
- **Устаревшие GitHub Actions и права**: используются `actions/cache@v3` и `codecov/codecov-action@v3`; отсутствует блок `permissions:`.
- **Невыполнимость полного `pytest tests/` в текущем CI**:
  - В `ci.yml` запускается `pytest tests/ --cov=app ...` без поднятия MongoDB/Neo4j/Redis/Elasticsearch и без фильтрации `-m unit`, тогда как в `tests/integration/` находится 8 интеграционных тест-файлов.
  - Даже unit-тест `tests/unit/test_main.py::test_health_endpoint` вызывает `GET /health` без моков репозиториев и ожидает `data["status"] == "healthy"`, что падает без запущенных MongoDB и Neo4j.
  - В `tests/unit/test_security.py::test_token_replay_attack_prevention` задержка `time.sleep(0.1)` сопоставляется с целочисленным `iat` JWT, что создаёт риск флаков на границах секунды.
- **Проверка Docker-образа**: `docker run --rm content-blocks-api:latest python -c "import app; print('Image OK')"` импортирует пустой файл `app/__init__.py` и не проверяет импорт `app.main` и маршрутов.

---

## 6. Безопасные улучшения, внесённые в ветке `audit/code-review`

1. **`app/core/security.py`**:
   - Реализовано чтение `JWT_SECRET_KEY` (с резервом `SECRET_KEY` и безопасным локальным fallback `secrets.token_urlsafe(32)` для dev/тестов), что позволяет разделять единый секрет между репликами в Kubernetes/Docker без поломки локального запуска.
   - Исправлен перехват исключений в `decode_token`: `except jwt.JWTError:` заменён на корректный для PyJWT `except jwt.PyJWTError:`, устраняя `AttributeError` при декодировании невалидных токенов.
2. **`.env.example`**:
   - Добавлены проверенные по коду и манифестам переменные `JWT_SECRET_KEY=` (используется в `app/core/security.py` и `k8s/api-deployment.yaml`) и `REDIS_PASSWORD=` (используется в `app/repositories/redis_repo.py` и `k8s/api-deployment.yaml`), а также примечание о расхождении `ELASTICSEARCH_URI` и `ELASTICSEARCH_HOST`/`ELASTICSEARCH_PORT`.

---

## 7. Рекомендуемые следующие инженерные шаги

1. **Удалить реальные секреты из Git**: заменить `k8s/secrets.yaml` на шаблон без зашитых учётных данных и перейти на External Secrets / Sealed Secrets; убрать дефолтный `NEO4J_PASSWORD="password"` из `app/config.py`.
2. **Унифицировать конфигурацию**: перевести `mongo_repo`, `neo4j_repo`, `redis_repo`, `elasticsearch_repo`, `auth_service`, `audit_service` и `nlp_service` на единый `settings` (`app/config.py`), поддержав `REDIS_URL` и `ELASTICSEARCH_URL` (или приведя `k8s/configmap.yaml` к единым именам переменных) и собирая `MONGODB_URI` с учётными данными в K8s.
3. **Разделить пробы здоровья и починить CORS/API-key auth**: возвращать HTTP `503` из `/health/ready` при падении обязательных БД (MongoDB, Neo4j), оставить `/health/live` легковесным, настроить конкретные `allow_origins` вместо `"*"` при `allow_credentials=True`, и перевести `HTTPBearer(auto_error=False)` в `app/api/auth.py` для корректной работы `X-API-Key`.
4. **Очистить и разделить зависимости**: удалить дублирующий `python-jose` (или привести `passlib`/`bcrypt` к совместимым версиям), вынести тестовые/ML-зависимости в extras/отдельные requirements и разделить unit и integration тесты в `.github/workflows/ci.yml` (добавив сервисы или моки для `test_health_endpoint`).
