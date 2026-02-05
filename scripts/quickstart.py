#!/usr/bin/env python3
"""
Quickstart script for Dynamic Content Blocks System

This script helps you get started quickly by:
1. Checking service health
2. Importing sample data
3. Creating a sample template
4. Assembling a sample document
5. Exporting the document

Usage:
    python scripts/quickstart.py [--skip-import] [--skip-demo]
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import block_service, assembly_service
from app.repositories import mongo_repo, neo4j_repo
from app.models import (
    BlockCreate,
    BlockMetadata,
    BlockRelationships,
    Template,
    TemplateSection,
    AssemblyRequest
)
from app.utils.parsers import parse_sgb_file


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step_num: int, description: str):
    """Print a step description"""
    print(f"\n📌 Step {step_num}: {description}")
    print("-" * 70)


def check_service(name: str, check_func) -> bool:
    """Check if a service is available"""
    try:
        check_func()
        print(f"   ✅ {name} is available")
        return True
    except Exception as e:
        print(f"   ❌ {name} is NOT available: {e}")
        return False


async def check_services() -> bool:
    """
    Check if required services are available

    :return: True if all services are available
    """
    print_step(1, "Checking service health")

    # Check MongoDB
    mongo_ok = check_service(
        "MongoDB",
        lambda: mongo_repo.client.admin.command('ping')
    )

    # Check Neo4j
    neo4j_ok = check_service(
        "Neo4j",
        lambda: neo4j_repo.driver.verify_connectivity()
    )

    if not (mongo_ok and neo4j_ok):
        print("\n❌ Some services are not available!")
        print("\n💡 Start services with: docker-compose up -d")
        return False

    print("\n✅ All core services are healthy!")
    return True


async def check_nlp_models():
    """
    Check if NLP models are available (optional)

    This is not a blocking check - the system works without ML features
    """
    print("\n🧠 Checking AI/ML models (Phase 3 features):")

    try:
        # Check spaCy model
        import spacy
        try:
            nlp = spacy.load("de_core_news_lg")
            print("   ✅ spaCy German model (de_core_news_lg) is installed")
        except OSError:
            try:
                nlp = spacy.load("de_core_news_md")
                print("   ⚠️  Using fallback spaCy model (de_core_news_md)")
            except OSError:
                try:
                    nlp = spacy.load("de_core_news_sm")
                    print("   ⚠️  Using minimal spaCy model (de_core_news_sm)")
                except OSError:
                    print("   ❌ No German spaCy model found")
                    print("      Install with: python -m spacy download de_core_news_lg")
                    print("      Or run: python scripts/setup_nlp_models.py")
                    return False

        # Check sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("   ✅ Sentence Transformers model is ready")

        print("\n✅ AI/ML models are ready!")
        print("   You can use semantic search, NER, classification, and summarization.")
        return True

    except Exception as e:
        print(f"   ⚠️  AI/ML models not fully available: {e}")
        print("   Note: This is optional - system works without ML features")
        print("   To enable ML: python scripts/setup_nlp_models.py")
        return False


async def import_sample_data(skip_import: bool = False) -> bool:
    """
    Import sample SGB IX data

    :param skip_import: Skip if data already exists
    :return: True if import successful
    """
    print_step(2, "Importing sample SGB IX data")

    # Check if data already exists
    existing_blocks = await block_service.list_blocks(limit=1)
    if existing_blocks and skip_import:
        print("   ⚠️  Data already exists, skipping import")
        return True

    # Import from sample file
    sample_file = Path("data/samples/sgb9_sample.txt")
    if not sample_file.exists():
        print(f"   ❌ Sample file not found: {sample_file}")
        return False

    try:
        blocks = parse_sgb_file(str(sample_file), law_name="SGB IX")
        print(f"   📖 Parsed {len(blocks)} blocks from sample file")

        result = await block_service.import_blocks(blocks)
        print(f"   ✅ Imported {result['success']}/{result['total']} blocks")

        if result['failed'] > 0:
            print(f"   ⚠️  {result['failed']} blocks failed to import")

        return result['success'] > 0
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


async def create_sample_blocks() -> list:
    """
    Create custom sample blocks for Widerspruch

    :return: List of created block IDs
    """
    print_step(3, "Creating custom Widerspruch blocks")

    blocks_data = [
        {
            "id": "widerspruch_intro",
            "type": "custom",
            "title": "Widerspruch - Einleitung",
            "content": "Hiermit lege ich Widerspruch gegen den Bescheid vom [DATUM] mit dem Aktenzeichen [AKTENZEICHEN] ein.",
            "metadata": {"category": "widerspruch", "tags": ["widerspruch", "einleitung"]},
        },
        {
            "id": "widerspruch_antrag",
            "type": "custom",
            "title": "Widerspruch - Antrag",
            "content": "Ich beantrage, den angefochtenen Bescheid aufzuheben und die beantragten Leistungen zur Teilhabe zu bewilligen.",
            "metadata": {"category": "widerspruch", "tags": ["widerspruch", "antrag"]},
        },
        {
            "id": "widerspruch_begruendung",
            "type": "custom",
            "title": "Widerspruch - Begründung",
            "content": "Die Ablehnung ist rechtswidrig und verletzt meine Rechte. Nach § 5 SGB IX habe ich Anspruch auf Leistungen zur Teilhabe am Leben in der Gesellschaft.",
            "metadata": {"category": "widerspruch", "tags": ["widerspruch", "begründung"]},
        },
        {
            "id": "widerspruch_schluss",
            "type": "custom",
            "title": "Widerspruch - Schluss",
            "content": "Ich bitte um Aufhebung des Bescheides und um eine positive Entscheidung.\n\nMit freundlichen Grüßen\n[NAME]",
            "metadata": {"category": "widerspruch", "tags": ["widerspruch", "schluss"]},
        }
    ]

    created_ids = []
    for block_data in blocks_data:
        try:
            # Check if block already exists
            existing = await block_service.get_block(block_data["id"])
            if existing:
                print(f"   ⚠️  Block already exists: {block_data['id']}")
                created_ids.append(block_data["id"])
                continue

            # Create block
            block_create = BlockCreate(
                type=block_data["type"],
                title=block_data["title"],
                content=block_data["content"],
                source="Custom",
                level=1,
                metadata=BlockMetadata(**block_data["metadata"]),
                relationships=BlockRelationships(
                    parent_ids=[],
                    child_ids=[],
                    references=[],
                    related_to=[]
                )
            )

            block = await block_service.create_block(block_create)
            print(f"   ✅ Created block: {block.id}")
            created_ids.append(block.id)
        except Exception as e:
            print(f"   ❌ Failed to create block {block_data['id']}: {e}")

    return created_ids


async def create_sample_template(block_ids: list) -> Optional[str]:
    """
    Create a sample Widerspruch template

    :param block_ids: IDs of blocks to include
    :return: Template ID or None
    """
    print_step(4, "Creating Widerspruch template")

    template_id = "widerspruch_standard_template"

    # Check if template already exists
    existing = await assembly_service.get_template(template_id)
    if existing:
        print(f"   ⚠️  Template already exists: {template_id}")
        return template_id

    try:
        # Get SGB IX § 5 block if it exists
        sgb9_blocks = await block_service.search_blocks(
            source="SGB IX",
            tags=["§5"]
        )
        sgb9_block_ids = [b.id for b in sgb9_blocks[:1]] if sgb9_blocks else []

        template = Template(
            id=template_id,
            name="Widerspruch gegen Ablehnungsbescheid",
            description="Standardvorlage für Widerspruch gegen Ablehnungsbescheid nach SGB IX",
            sections=[
                TemplateSection(
                    name="einleitung",
                    blocks=[block_ids[0]] if len(block_ids) > 0 else [],
                    conditions={}
                ),
                TemplateSection(
                    name="antrag",
                    blocks=[block_ids[1]] if len(block_ids) > 1 else [],
                    conditions={}
                ),
                TemplateSection(
                    name="rechtsgrundlage",
                    blocks=sgb9_block_ids,
                    conditions={"include_legal_basis": True}
                ),
                TemplateSection(
                    name="begruendung",
                    blocks=[block_ids[2]] if len(block_ids) > 2 else [],
                    conditions={}
                ),
                TemplateSection(
                    name="schluss",
                    blocks=[block_ids[3]] if len(block_ids) > 3 else [],
                    conditions={}
                )
            ],
            metadata={
                "category": "widerspruch",
                "version": "1.0",
                "author": "System"
            }
        )

        success = await assembly_service.create_template(template)
        if success:
            print(f"   ✅ Created template: {template_id}")
            print(f"      Name: {template.name}")
            print(f"      Sections: {len(template.sections)}")
            return template_id
        else:
            print(f"   ❌ Failed to create template")
            return None
    except Exception as e:
        print(f"   ❌ Error creating template: {e}")
        return None


async def assemble_sample_document(template_id: str) -> Optional[str]:
    """
    Assemble a sample document from template

    :param template_id: Template ID
    :return: Document ID or None
    """
    print_step(5, "Assembling sample document")

    try:
        request = AssemblyRequest(
            template_id=template_id,
            title="Widerspruch - Max Mustermann",
            context={
                "include_legal_basis": True,
                "client_name": "Max Mustermann",
                "bescheid_date": "15.01.2024",
                "case_number": "12345/2024"
            }
        )

        result = await assembly_service.assemble_document(request)

        print(f"   ✅ Document assembled: {result.document.id}")
        print(f"      Title: {result.document.title}")
        print(f"      Status: {result.document.status}")
        print(f"      Blocks: {result.blocks_included}")
        print(f"      Rules applied: {result.rules_applied}")

        return result.document.id
    except Exception as e:
        print(f"   ❌ Error assembling document: {e}")
        return None


async def export_sample_document(document_id: str):
    """
    Export sample document to various formats

    :param document_id: Document ID
    """
    print_step(6, "Exporting document")

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    try:
        # Export as text
        text = await assembly_service.render_document_text(document_id)
        text_path = export_dir / f"{document_id}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"   ✅ Text: {text_path}")

        # Export as Markdown
        markdown = await assembly_service.export_document_markdown(document_id)
        md_path = export_dir / f"{document_id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"   ✅ Markdown: {md_path}")

        # Export as DOCX
        docx_buffer = await assembly_service.export_document_docx(document_id)
        docx_path = export_dir / f"{document_id}.docx"
        with open(docx_path, 'wb') as f:
            f.write(docx_buffer.read())
        print(f"   ✅ DOCX: {docx_path}")

        print(f"\n   📁 All exports saved to: {export_dir.absolute()}")
    except Exception as e:
        print(f"   ❌ Error exporting document: {e}")


async def show_statistics():
    """Show database statistics"""
    print_step(7, "Database statistics")

    try:
        stats = mongo_repo.get_stats()
        print(f"   📊 Blocks: {stats['blocks']}")
        print(f"   📊 Rules: {stats['rules']}")
        print(f"   📊 Documents: {stats['documents']}")
        print(f"   📊 Templates: {stats['templates']}")

        # Show sample blocks
        blocks = await block_service.list_blocks(limit=5)
        if blocks:
            print(f"\n   📦 Sample blocks:")
            for block in blocks[:5]:
                print(f"      - {block.id}: {block.title}")
    except Exception as e:
        print(f"   ⚠️  Could not retrieve statistics: {e}")


async def run_quickstart(skip_import: bool = False, skip_demo: bool = False):
    """
    Run the quickstart flow

    :param skip_import: Skip data import if data exists
    :param skip_demo: Skip demo document assembly
    """
    print_header("Dynamic Content Blocks - Quickstart")
    print("This script will set up a demo environment for you.\n")

    start_time = time.time()

    # Initialize services
    print("🔌 Initializing services...")
    await block_service.initialize()

    # Step 1: Check services
    if not await check_services():
        await block_service.shutdown()
        return False

    # Step 1.5: Check NLP models (optional, non-blocking)
    await check_nlp_models()

    # Step 2: Import sample data
    if not await import_sample_data(skip_import):
        print("\n⚠️  Warning: Sample data import failed, continuing anyway...")

    # Step 3-6: Demo flow
    if not skip_demo:
        # Create custom blocks
        block_ids = await create_sample_blocks()

        if len(block_ids) >= 4:
            # Create template
            template_id = await create_sample_template(block_ids)

            if template_id:
                # Assemble document
                document_id = await assemble_sample_document(template_id)

                if document_id:
                    # Export document
                    await export_sample_document(document_id)

    # Step 7: Show statistics
    await show_statistics()

    # Cleanup
    await block_service.shutdown()

    elapsed_time = time.time() - start_time

    # Success message
    print_header("Quickstart Complete!")
    print(f"\n✨ Setup completed in {elapsed_time:.2f} seconds\n")

    print("🚀 Next steps:")
    print("   1. Start the API server: uvicorn app.main:app --reload")
    print("   2. Open API docs: http://localhost:8000/docs")
    print("   3. Try the examples: python examples/01_create_blocks.py")
    print("   4. View exported documents in: exports/")
    print("   5. Demo AI/ML features: python scripts/demo_ml_features.py")

    print("\n📚 Learn more:")
    print("   - README.md - Project overview")
    print("   - docs/dynamic_content_blocks_methodology.md - Full methodology")
    print("   - examples/README.md - API usage examples")

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Quickstart script for Dynamic Content Blocks System"
    )
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Skip data import if data already exists"
    )
    parser.add_argument(
        "--skip-demo",
        action="store_true",
        help="Skip demo document assembly"
    )
    args = parser.parse_args()

    try:
        success = asyncio.run(run_quickstart(
            skip_import=args.skip_import,
            skip_demo=args.skip_demo
        ))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Quickstart cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
