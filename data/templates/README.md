# Document Templates

This directory contains ready-to-use document templates with their blocks and example contexts.

## Widerspruch Template

The Widerspruch template (`widerspruch_template.json`) is a comprehensive template for creating formal objections (Widerspruch) against administrative decisions according to German social law (SGB IX).

### Features

- **Complete Structure**: All necessary sections from sender info to legal signature
- **Flexible Sections**: Conditional blocks based on context variables
- **Multiple Reasons**: Different reasoning blocks for various legal grounds
- **Legal References**: Integration with SGB IX paragraphs (§5, §29)
- **Example Contexts**: 3 pre-configured examples for different use cases

### Template Structure

The template consists of the following sections:

1. **Absender** (Sender) - Your personal information
2. **Empfänger** (Recipient) - Authority/agency information
3. **Betreff** (Subject) - Reference numbers and dates
4. **Einleitung** (Introduction) - Formal objection declaration
5. **Antrag** (Request) - Specific legal request
6. **Rechtsgrundlage** (Legal Basis) - Conditional SGB IX references
   - § 5 SGB IX - Leistungen zur Teilhabe
   - § 29 SGB IX - Persönliches Budget
7. **Begründung** (Reasoning) - Various types of reasoning:
   - Mangelnde Begründung (Insufficient reasoning)
   - Rechtsverletzung (Legal violation)
   - Falsche Tatsachen (Incorrect facts)
   - Ermessensfehler (Discretion error)
8. **Fristwahrung** (Time limit) - Optional deadline reference
9. **Akteneinsicht** (File inspection) - Optional request for file access
10. **Schluss** (Conclusion) - Formal closing and signature

### Blocks

The template includes 12 custom blocks:

- `widerspruch_absender` - Sender information
- `widerspruch_empfaenger` - Recipient information
- `widerspruch_betreff` - Subject line
- `widerspruch_einleitung` - Introduction
- `widerspruch_antrag` - Legal request
- `widerspruch_grund_begruendung` - Reasoning: insufficient justification
- `widerspruch_grund_rechtsverletzung` - Reasoning: legal violation
- `widerspruch_grund_tatsachen` - Reasoning: incorrect facts
- `widerspruch_grund_ermessen` - Reasoning: discretion error
- `widerspruch_frist` - Time limit notice
- `widerspruch_akteneinsicht` - File inspection request
- `widerspruch_schluss` - Conclusion and signature

### Context Variables

The template uses the following placeholders that should be provided in the context:

**Personal Information:**
- `VORNAME` - First name
- `NACHNAME` - Last name
- `STRASSE` - Street
- `HAUSNUMMER` - House number
- `PLZ` - Postal code
- `STADT` - City
- `TELEFON` - Phone number
- `EMAIL` - Email address

**Agency Information:**
- `BEHÖRDE` - Authority name
- `ABTEILUNG` - Department

**Case Information:**
- `BESCHEID_DATUM` - Decision date
- `AKTENZEICHEN` - Reference number
- `LEISTUNGSART` - Type of benefit

**Conditional Flags:**
- `include_sgb9_para5` (boolean) - Include § 5 SGB IX
- `include_sgb9_para29` (boolean) - Include § 29 SGB IX
- `grund_type` (string) - Type of reasoning:
  - `"mangelnde_begruendung"`
  - `"rechtsverletzung"`
  - `"falsche_tatsachen"`
  - `"ermessensfehler"`
- `include_frist` (boolean) - Include time limit notice
- `request_akteneinsicht` (boolean) - Request file inspection

### Example Contexts

The template includes 3 pre-configured examples:

#### Example 1: Full Objection with Legal Violation
Complete objection with all elements including legal basis and file inspection request.

```json
{
  "grund_type": "rechtsverletzung",
  "include_sgb9_para5": true,
  "include_sgb9_para29": false,
  "include_frist": true,
  "request_akteneinsicht": true
}
```

#### Example 2: Simple Objection with Insufficient Reasoning
Basic objection when the decision lacks proper justification.

```json
{
  "grund_type": "mangelnde_begruendung",
  "include_sgb9_para5": false,
  "include_sgb9_para29": false,
  "include_frist": false,
  "request_akteneinsicht": false
}
```

#### Example 3: Objection for Personal Budget
Objection against denial of Personal Budget (Persönliches Budget).

```json
{
  "grund_type": "rechtsverletzung",
  "include_sgb9_para5": true,
  "include_sgb9_para29": true,
  "include_frist": true,
  "request_akteneinsicht": true
}
```

## Installation

### 1. Import the Template

```bash
python scripts/import_widerspruch_template.py
```

This will:
- Create all custom blocks in the database
- Create the template structure
- Make it available via API

### 2. Verify Import

```bash
python scripts/import_widerspruch_template.py --info
```

Or via API:
```bash
curl http://localhost:8000/api/templates/widerspruch_standard_v1
```

## Usage

### Command Line

List available examples:
```bash
python scripts/assemble_widerspruch_example.py --list
```

Assemble example 1 (full objection):
```bash
python scripts/assemble_widerspruch_example.py --example 1
```

Assemble and export to files:
```bash
python scripts/assemble_widerspruch_example.py --example 1 --export
```

### Python API

```python
from app.services import assembly_service
from app.models import AssemblyRequest

# Create assembly request
request = AssemblyRequest(
    template_id="widerspruch_standard_v1",
    title="Widerspruch - Max Mustermann",
    context={
        "VORNAME": "Max",
        "NACHNAME": "Mustermann",
        "STRASSE": "Hauptstraße",
        "HAUSNUMMER": "1",
        "PLZ": "12345",
        "STADT": "Berlin",
        "TELEFON": "030-12345678",
        "EMAIL": "max@example.com",
        "BEHÖRDE": "Integrationsamt Berlin",
        "ABTEILUNG": "Abteilung Rehabilitation",
        "BESCHEID_DATUM": "15.01.2024",
        "AKTENZEICHEN": "12345/2024",
        "LEISTUNGSART": "Arbeitsassistenz",
        "grund_type": "rechtsverletzung",
        "include_sgb9_para5": True,
        "include_sgb9_para29": False,
        "include_frist": True,
        "request_akteneinsicht": True
    }
)

# Assemble document
result = await assembly_service.assemble_document(request)
document = result.document

# Export to DOCX
docx_buffer = await assembly_service.export_document_docx(document.id)
with open("widerspruch.docx", "wb") as f:
    f.write(docx_buffer.read())
```

### REST API

```bash
# Assemble document
curl -X POST http://localhost:8000/api/documents/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "widerspruch_standard_v1",
    "title": "Widerspruch - Max Mustermann",
    "context": {
      "VORNAME": "Max",
      "NACHNAME": "Mustermann",
      "grund_type": "rechtsverletzung",
      "include_sgb9_para5": true
    }
  }'

# Export as DOCX
curl http://localhost:8000/api/documents/{document_id}/export/docx \
  --output widerspruch.docx
```

## Customization

You can customize the template by:

1. **Adding new blocks**: Create blocks with specific content
2. **Modifying sections**: Add/remove sections in the template
3. **Creating variants**: Create alternative templates for different scenarios
4. **Adding conditions**: Use context variables for more dynamic behavior

Example - Add a custom block:
```python
from app.services import block_service
from app.models import BlockCreate, BlockMetadata, BlockRelationships

block = BlockCreate(
    type="custom",
    title="Custom Section",
    content="Your custom content here",
    source="Custom",
    level=1,
    metadata=BlockMetadata(
        category="widerspruch",
        tags=["custom"]
    ),
    relationships=BlockRelationships(
        parent_ids=[],
        child_ids=[],
        references=[],
        related_to=[]
    )
)

created_block = await block_service.create_block(block)
```

## Legal Disclaimer

This template is provided for informational purposes only. While it follows standard German administrative law practices:

- **Not Legal Advice**: This is not a substitute for professional legal advice
- **Individual Cases**: Each case has unique circumstances
- **Review Required**: Have your objection reviewed by a qualified attorney
- **Deadlines**: Ensure compliance with applicable time limits (typically 1 month)
- **Local Requirements**: Check for specific requirements of your jurisdiction

Always consult with a qualified attorney (Rechtsanwalt) for:
- Complex cases
- High-value claims
- Legal uncertainties
- Important deadlines

## Support

For questions or issues:
- Review the main README: [../../README.md](../../README.md)
- Check API documentation: http://localhost:8000/docs
- Review examples: [../../examples/](../../examples/)
- Consult methodology: [../../docs/dynamic_content_blocks_methodology.md](../../docs/dynamic_content_blocks_methodology.md)

## Version History

- **v1.0** (2024) - Initial release
  - Complete Widerspruch structure
  - 12 custom blocks
  - 4 reasoning types
  - 3 example contexts
  - SGB IX integration
