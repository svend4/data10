# Integration Tests

This directory contains integration tests that verify the interaction between multiple components of the system.

## Test Coverage

### test_block_service.py

Tests for `BlockService` integration with MongoDB and Neo4j:
- ✅ Create block and store in both databases
- ✅ Create block with parent-child relationships
- ✅ Get block by ID
- ✅ Update block
- ✅ Delete block from both databases
- ✅ List blocks with pagination
- ✅ Search blocks by tags
- ✅ Get related blocks with depth traversal (graph)

### test_rule_engine.py

Tests for `RuleEngine` conditional logic:
- ✅ Evaluate EQUALS operator
- ✅ Evaluate GREATER operator
- ✅ Evaluate IN operator
- ✅ Evaluate CONTAINS operator
- ✅ Evaluate single condition rules
- ✅ Evaluate AND condition groups
- ✅ Evaluate OR condition groups
- ✅ Disabled rules handling
- ✅ Get blocks to include based on rules
- ✅ Rule priority ordering

### test_assembly_service.py

Tests for `AssemblyService` document assembly:
- ✅ Create template
- ✅ Get template by ID
- ✅ List templates
- ✅ Assemble document from template
- ✅ Conditional section inclusion
- ✅ Invalid template handling
- ✅ Get document by ID
- ✅ List documents with pagination
- ✅ Update document status
- ✅ Render document as text
- ✅ Export document as Markdown
- ✅ Export document as DOCX
- ✅ Export non-existent document error handling
- ✅ Block ordering in assembled documents

### test_ml_service.py

Tests for `NLPService` AI/ML functionality:
- ✅ NLP service initialization and shutdown
- ✅ Text tokenization
- ✅ Lemmatization
- ✅ Stopword removal
- ✅ POS (Part-of-Speech) tagging
- ✅ Named Entity Recognition (NER)
- ✅ Legal reference extraction (§, Art., Abs.)
- ✅ Semantic embedding generation (single & batch)
- ✅ Embedding consistency
- ✅ Cosine similarity calculation
- ✅ Find most similar texts
- ✅ Block type classification (right, definition, procedure, etc.)
- ✅ Category classification (health, employment, etc.)
- ✅ Full block classification
- ✅ Frequency-based summarization
- ✅ Position-based summarization
- ✅ Summary points generation
- ✅ Text statistics (word count, sentences, etc.)
- ✅ Keyword extraction
- ✅ Error handling (empty text, long text, special characters)

### test_ml_api.py

Tests for ML REST API endpoints:
- ✅ GET /api/ml/status - NLP service status
- ✅ POST /api/ml/analyze - Full text analysis
- ✅ POST /api/ml/embedding - Generate embeddings
- ✅ POST /api/ml/similarity - Calculate text similarity
- ✅ POST /api/ml/ner - Named Entity Recognition
- ✅ POST /api/ml/classify - Auto-classify blocks
- ✅ POST /api/ml/summarize - Text summarization
- ✅ POST /api/ml/semantic-search - Semantic search in blocks
- ✅ POST /api/search/semantic - Elasticsearch semantic search
- ✅ API error handling (503, 422 errors)
- ✅ Invalid JSON handling
- ✅ Malformed request handling
- ✅ Full workflow integration tests

## Prerequisites

### Required Services

Integration tests require the following services to be running:

1. **MongoDB** - Document storage
2. **Neo4j** - Graph database for relationships
3. **NLP Models** (optional, for ML tests) - spaCy and sentence-transformers

Start services with Docker Compose:
```bash
docker-compose up -d mongodb neo4j
```

Install NLP models for ML tests:
```bash
python scripts/setup_nlp_models.py
```

**Note**: ML tests will be skipped automatically if NLP models are not installed.

### Environment Variables

Ensure the following environment variables are set (or use `.env` file):
```bash
MONGODB_URI=mongodb://localhost:27017
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Running Tests

### Run All Integration Tests

```bash
pytest tests/integration/ -v
```

### Run Specific Test File

```bash
# Test BlockService
pytest tests/integration/test_block_service.py -v

# Test RuleEngine
pytest tests/integration/test_rule_engine.py -v

# Test AssemblyService
pytest tests/integration/test_assembly_service.py -v

# Test ML/NLP Service
pytest tests/integration/test_ml_service.py -v

# Test ML API endpoints
pytest tests/integration/test_ml_api.py -v
```

### Run Specific Test

```bash
pytest tests/integration/test_block_service.py::test_create_block -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=app --cov-report=html
```

### Run with Output

```bash
pytest tests/integration/ -v -s
```

## Test Fixtures

### conftest.py

Provides shared fixtures for all integration tests:

- **event_loop**: Async event loop for pytest-asyncio
- **setup_services**: Initializes and cleans up services
- **sample_block**: Creates a sample paragraph block
- **sample_child_block**: Creates a sample child block
- **sample_template**: Creates a sample document template
- **cleanup_test_data**: Cleans up test data after each test

## Test Data Cleanup

Tests use the `cleanup_test_data` fixture to ensure:
- Test blocks are removed from MongoDB and Neo4j
- Test templates are deleted
- Test documents are cleaned up

This prevents test data pollution between test runs.

## Async Testing

All integration tests use `pytest-asyncio` for async/await support:

```python
@pytest.mark.asyncio
async def test_something(setup_services):
    result = await some_async_function()
    assert result is not None
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always use cleanup fixtures
3. **Descriptive Names**: Test names should describe what they verify
4. **Assertions**: Include meaningful assertion messages
5. **Setup**: Use fixtures for common setup tasks

## Troubleshooting

### Connection Errors

```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused
```

**Solution**: Ensure MongoDB is running:
```bash
docker-compose up -d mongodb
```

### Neo4j Authentication Errors

```
neo4j.exceptions.AuthError: The client is unauthorized
```

**Solution**: Check Neo4j credentials in `.env` file

### Test Data Conflicts

```
DuplicateKeyError: E11000 duplicate key error
```

**Solution**: Run cleanup script:
```bash
python scripts/cleanup_test_data.py
```

Or manually clean databases:
```bash
# MongoDB
mongosh
> use dynamic_blocks_test
> db.dropDatabase()

# Neo4j
cypher-shell
> MATCH (n) WHERE n.id STARTS WITH 'test_' DELETE n;
```

## CI/CD Integration

Integration tests are run in GitHub Actions CI pipeline:

```yaml
- name: Run Integration Tests
  run: |
    docker-compose up -d mongodb neo4j
    sleep 10  # Wait for services
    pytest tests/integration/ -v
```

See `.github/workflows/ci.yml` for full configuration.

## Performance

Integration tests are slower than unit tests due to:
- Database I/O operations
- Network calls to MongoDB and Neo4j
- Service initialization overhead

Expected run time: **30-60 seconds** for full suite

## Future Improvements

- [x] Add tests for ML/NLP Service (Phase 3)
- [x] Add tests for ML API endpoints (Phase 3)
- [ ] Add tests for Elasticsearch integration (full-text search)
- [ ] Add tests for Redis caching
- [ ] Add tests for version control API
- [ ] Add tests for bulk operations
- [ ] Add tests for concurrent operations
- [ ] Add performance benchmarks
- [ ] Add load testing scenarios
- [ ] Add transaction rollback tests
- [ ] Add error recovery tests

## Support

For issues with integration tests:
1. Check service logs: `docker-compose logs mongodb neo4j`
2. Verify service health: `curl http://localhost:8000/health`
3. Review test output: `pytest tests/integration/ -v -s`
4. Check database connections in `app/repositories/`
