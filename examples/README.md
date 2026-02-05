# API Usage Examples

This directory contains examples demonstrating how to use the Dynamic Content Blocks API.

## Prerequisites

1. **Start the API server**:
   ```bash
   # Using Docker Compose (recommended)
   docker-compose up -d

   # Or directly with uvicorn
   uvicorn app.main:app --reload
   ```

2. **Install requests library**:
   ```bash
   pip install requests
   ```

3. **Verify API is running**:
   ```bash
   curl http://localhost:8000/health
   ```

## Examples

### 01_create_blocks.py

**Purpose**: Demonstrates creating blocks through the REST API.

**What it does**:
- Creates a paragraph block from SGB IX (§ 5)
- Creates a child absatz block (§ 5 Abs. 1)
- Creates a custom Widerspruch block with references
- Retrieves related blocks using graph traversal

**Usage**:
```bash
python examples/01_create_blocks.py
```

**Expected output**:
```
📦 Creating blocks via API

Creating paragraph block...
✅ Created block: sgb9_para5_abc123
   Title: § 5 SGB IX - Leistungen zur Teilhabe
   Type: paragraph

Creating absatz block (child of paragraph)...
✅ Created block: sgb9_para5_abs1_def456
   Title: § 5 Abs. 1 - Umfang der Leistungen
   Parent: ['sgb9_para5_abc123']

...
```

**Key concepts**:
- Block types: `paragraph`, `absatz`, `custom`
- Metadata: law references, tags, effective dates
- Relationships: parent-child hierarchy, references
- Graph traversal: finding related blocks

---

### 02_assemble_document.py

**Purpose**: Demonstrates document assembly from templates.

**What it does**:
- Creates sample blocks (intro, legal basis, reasoning)
- Creates a Widerspruch template with sections and conditions
- Assembles a document using the template
- Applies context variables
- Lists assembled documents

**Usage**:
```bash
python examples/02_assemble_document.py
```

**Expected output**:
```
📄 Assembling documents via API

Step 1: Creating sample blocks...
   ✅ Created: sgb9_para5
   ✅ Created: widerspruch_intro
   ✅ Created: widerspruch_grund

Step 2: Creating document template...
   ✅ Template created: widerspruch_template

Step 3: Assembling document...
   ✅ Document assembled: doc_abc123def456
   Title: Widerspruch - Hans Müller
   Blocks included: 3
   Rules applied: 0
   Status: ASSEMBLED

...
```

**Key concepts**:
- Templates: reusable document structures
- Sections: logical groupings of blocks
- Conditions: conditional block inclusion
- Context: variables for personalization
- Assembly process: template + context → document

---

### 03_export_document.py

**Purpose**: Demonstrates exporting documents to various formats.

**What it does**:
- Retrieves a document by ID
- Displays document preview with metadata
- Exports to Text format (.txt)
- Exports to Markdown format (.md)
- Exports to DOCX format (.docx / Microsoft Word)
- Saves all files to `exports/` directory

**Usage**:
```bash
# First, create a document using example 02
python examples/02_assemble_document.py

# Then export it (use the document ID from step 02)
python examples/03_export_document.py doc_abc123def456
```

**Expected output**:
```
📤 Exporting document: doc_abc123def456

Preview:
======================================================================
Document: Widerspruch - Hans Müller
======================================================================
ID: doc_abc123def456
Status: ASSEMBLED
Template: widerspruch_template
Created: 2024-01-20T14:30:00
Blocks: 3

...

Exporting to formats...
✅ Text exported to: exports/doc_abc123def456.txt
✅ Markdown exported to: exports/doc_abc123def456.md
✅ DOCX exported to: exports/doc_abc123def456.docx

✨ All exports completed successfully!
```

**Key concepts**:
- Export formats: Text, Markdown, DOCX
- Document preview and metadata
- File handling and streaming responses
- Microsoft Word integration (python-docx)

---

### 04_ml_text_analysis.py

**Purpose**: Demonstrates AI/ML text analysis features (Phase 3).

**What it does**:
- Performs comprehensive text analysis on German legal text
- Extracts text statistics (word/sentence count)
- Identifies keywords
- Performs Named Entity Recognition (NER)
- Extracts legal references (§, Art., Abs.)
- Tokenizes and lemmatizes text
- Generates POS (Part-of-Speech) tags
- Creates semantic embeddings (384-dimensional vectors)
- Auto-classifies text by type and category
- Summarizes long text

**Prerequisites**:
```bash
# Install NLP models first
python scripts/setup_nlp_models.py
```

**Usage**:
```bash
python examples/04_ml_text_analysis.py
```

**Expected output**:
```
==================================================================
  Example 4: ML Text Analysis
==================================================================

📦 Initializing NLP service...
✅ NLP service ready!

==================================================================
1. TEXT STATISTICS
==================================================================

📊 Statistics:
  • Total words: 62
  • Total sentences: 4
  • Unique words: 49
  • Average word length: 6.8 characters
  • Average sentence length: 15.5 words

==================================================================
2. KEYWORD EXTRACTION
==================================================================

🔑 Top keywords:
  1. Leistungen
  2. Teilhabe
  3. Rehabilitation
  4. Behinderung
  ...

==================================================================
3. NAMED ENTITY RECOGNITION (NER)
==================================================================

🏷️  Entities found:
  • Berlin (LOC)
    Position: 245-251
  • Berliner Senatsverwaltung (ORG)
    Position: 253-280
  ...
```

**Key concepts**:
- NLP processing with spaCy
- Semantic embeddings with sentence-transformers
- Named Entity Recognition (NER)
- Legal text pattern matching
- Auto-classification (types & categories)
- Extractive summarization

---

### 05_ml_semantic_search.py

**Purpose**: Demonstrates semantic search and similarity features (Phase 3).

**What it does**:
- Generates semantic embeddings for multiple blocks
- Calculates similarity scores between texts
- Performs batch similarity search
- Finds most similar blocks for natural language queries
- Creates similarity matrices
- Demonstrates content clustering by similarity

**Prerequisites**:
```bash
# Install NLP models and import sample data
python scripts/setup_nlp_models.py
python scripts/quickstart.py
```

**Usage**:
```bash
python examples/05_ml_semantic_search.py
```

**Expected output**:
```
==================================================================
  Example 5: ML Semantic Search
==================================================================

📦 Initializing services...
✅ Services ready!

==================================================================
1. GENERATING EMBEDDINGS
==================================================================

🔄 Generating embeddings for all blocks...
  ✅ block1: § 5 Leistungen zur Teilhabe
  ✅ block2: § 29 Persönliches Budget
  ...

✅ Generated 5 embeddings (384 dimensions each)

==================================================================
2. SEMANTIC SIMILARITY
==================================================================

🔍 Query block: § 5 Leistungen zur Teilhabe
   Content: Menschen mit Behinderung haben Anspruch auf Leistungen...

📊 Similarity scores:

  § 42 Leistungen zur Teilhabe am Arbeitsleben
    Similarity: 0.8542 🟢
    Zur Teilhabe am Arbeitsleben werden Leistungen erbracht...

  § 29 Persönliches Budget
    Similarity: 0.7234 🟢
    Auf Antrag werden Leistungen zur Teilhabe als Persönliches Budget...
  ...
```

**Key concepts**:
- Semantic embeddings (384-dim vectors)
- Cosine similarity (0-1 scale)
- Batch processing for efficiency
- Natural language queries
- Similarity thresholds
- Content clustering

---

## Complete Workflow Example

Here's a typical workflow combining all examples:

```bash
# Step 1: Start the services
docker-compose up -d

# Step 2: Wait for services to be ready (about 30 seconds)
sleep 30

# Step 3: Import SGB IX sample data
python scripts/import_sgb9.py --file data/samples/sgb9_sample.txt

# Step 4: Create custom blocks
python examples/01_create_blocks.py

# Step 5: Assemble a document
python examples/02_assemble_document.py

# Step 6: Export the document (use ID from step 5)
python examples/03_export_document.py doc_abc123def456

# Step 7: View the exported files
ls -lh exports/
```

## API Endpoints Reference

### Blocks

- `POST /api/blocks` - Create a block
- `GET /api/blocks/{block_id}` - Get block by ID
- `PUT /api/blocks/{block_id}` - Update block
- `DELETE /api/blocks/{block_id}` - Delete block
- `GET /api/blocks` - List blocks (with filters)
- `GET /api/blocks/{block_id}/related` - Get related blocks

### Documents

- `POST /api/documents/assemble` - Assemble document from template
- `GET /api/documents/{document_id}` - Get document
- `GET /api/documents` - List documents
- `GET /api/documents/{document_id}/export/text` - Export as text
- `GET /api/documents/{document_id}/export/markdown` - Export as markdown
- `GET /api/documents/{document_id}/export/docx` - Export as DOCX

### Templates

- `POST /api/templates` - Create template
- `GET /api/templates/{template_id}` - Get template
- `GET /api/templates` - List templates

### Search & ML (Phase 2 & 3)

- `POST /api/search` - Full-text search
- `GET /api/search/suggest` - Autocomplete suggestions
- `GET /api/search/similar/{block_id}` - Find similar blocks
- `POST /api/search/semantic` - Semantic search (AI-powered)
- `POST /api/search/reindex` - Reindex with embeddings
- `GET /api/ml/status` - NLP service status
- `POST /api/ml/analyze` - Full text analysis
- `POST /api/ml/embedding` - Generate embeddings
- `POST /api/ml/similarity` - Calculate similarity
- `POST /api/ml/ner` - Named Entity Recognition
- `POST /api/ml/classify` - Auto-classify blocks
- `POST /api/ml/summarize` - Text summarization

### Version Control (Phase 2)

- `GET /api/versions/{block_id}/history` - Version history
- `GET /api/versions/{block_id}/current` - Current version
- `POST /api/versions/{block_id}/restore` - Restore version
- `GET /api/versions/{block_id}/compare` - Compare versions

### Bulk Operations (Phase 2)

- `POST /api/bulk/create` - Bulk create blocks
- `POST /api/bulk/update` - Bulk update blocks
- `POST /api/bulk/delete` - Bulk delete blocks
- `POST /api/bulk/export` - Export blocks as JSON
- `POST /api/bulk/import` - Import blocks from file

## Troubleshooting

**Connection refused error**:
```
❌ API Error: Connection refused
```
- Make sure the API server is running: `docker-compose up -d`
- Check if port 8000 is available: `curl http://localhost:8000/health`

**Document not found**:
```
❌ Document not found: doc_xyz
```
- Run `02_assemble_document.py` first to create a document
- Use the correct document ID returned from the assembly step

**Import errors**:
```
ModuleNotFoundError: No module named 'requests'
```
- Install dependencies: `pip install requests`

## Next Steps

- Explore the API documentation: http://localhost:8000/docs
- Review the codebase in `app/` directory
- Create your own templates and blocks
- Implement custom rule logic
- Integrate with your own frontend application

## Support

For more information, see:
- Main README: [../README.md](../README.md)
- API Documentation: http://localhost:8000/docs
- Methodology: [../docs/dynamic_content_blocks_methodology.md](../docs/dynamic_content_blocks_methodology.md)
