#!/usr/bin/env python3
"""
Assemble Widerspruch documents using the template

This script demonstrates how to assemble different types of Widerspruch
documents using the imported template and various contexts.

Usage:
    python scripts/assemble_widerspruch_example.py [--example 1|2|3] [--export]
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import assembly_service, block_service
from app.models import AssemblyRequest


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def assemble_widerspruch(example_num: int = 1, export: bool = False):
    """
    Assemble a Widerspruch document

    :param example_num: Example context number (1-3)
    :param export: Export to files
    """

    # Read template file for example contexts
    template_file = Path("data/templates/widerspruch_template.json")
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        print(f"💡 Run: python scripts/import_widerspruch_template.py")
        return None

    with open(template_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if example_num < 1 or example_num > len(data['example_contexts']):
        print(f"❌ Invalid example number. Choose 1-{len(data['example_contexts'])}")
        return None

    example = data['example_contexts'][example_num - 1]

    print_header(f"Assembling: {example['name']}")
    print(f"\n📝 {example['description']}")

    # Initialize services
    print("\n🔌 Initializing services...")
    await block_service.initialize()

    # Check template exists
    template = await assembly_service.get_template("widerspruch_standard_v1")
    if not template:
        print("❌ Template not found!")
        print("💡 Run: python scripts/import_widerspruch_template.py")
        await block_service.shutdown()
        return None

    print(f"✅ Template loaded: {template.name}")

    # Assemble document
    print(f"\n📄 Assembling document...")

    try:
        request = AssemblyRequest(
            template_id="widerspruch_standard_v1",
            title=f"Widerspruch - {example['context']['VORNAME']} {example['context']['NACHNAME']}",
            context=example['context']
        )

        result = await assembly_service.assemble_document(request)
        document = result.document

        print(f"✅ Document assembled!")
        print(f"   ID: {document.id}")
        print(f"   Title: {document.title}")
        print(f"   Status: {document.status}")
        print(f"   Blocks: {result.blocks_included}")
        print(f"   Rules applied: {result.rules_applied}")

        # Display document preview
        print(f"\n{'='*70}")
        print("DOCUMENT PREVIEW")
        print(f"{'='*70}\n")

        text = await assembly_service.render_document_text(document.id)
        print(text)

        print(f"\n{'='*70}\n")

        # Export if requested
        if export:
            print("📤 Exporting document...")
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)

            # Text
            text_path = export_dir / f"{document.id}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"   ✅ Text: {text_path}")

            # Markdown
            markdown = await assembly_service.export_document_markdown(document.id)
            md_path = export_dir / f"{document.id}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"   ✅ Markdown: {md_path}")

            # DOCX
            docx_buffer = await assembly_service.export_document_docx(document.id)
            docx_path = export_dir / f"{document.id}.docx"
            with open(docx_path, 'wb') as f:
                f.write(docx_buffer.read())
            print(f"   ✅ DOCX: {docx_path}")

            print(f"\n   📁 Files saved to: {export_dir.absolute()}")

        # Cleanup
        await block_service.shutdown()

        return document.id

    except ValueError as e:
        print(f"❌ Assembly error: {e}")
        await block_service.shutdown()
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        await block_service.shutdown()
        return None


async def list_examples():
    """List available example contexts"""

    template_file = Path("data/templates/widerspruch_template.json")
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return

    with open(template_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print_header("Available Widerspruch Examples")

    for i, example in enumerate(data['example_contexts'], 1):
        print(f"\n{i}. {example['name']}")
        print(f"   {example['description']}")
        print(f"   Client: {example['context']['VORNAME']} {example['context']['NACHNAME']}")
        print(f"   Bescheid: {example['context']['BESCHEID_DATUM']}")
        print(f"   Leistung: {example['context']['LEISTUNGSART']}")
        print(f"   Grund: {example['context'].get('grund_type', 'N/A')}")

    print(f"\n💡 Usage: python {Path(__file__).name} --example <number> [--export]")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Assemble Widerspruch documents from template"
    )
    parser.add_argument(
        "--example",
        type=int,
        default=1,
        help="Example number (1-3, default: 1)"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export document to files (TXT, MD, DOCX)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available examples"
    )
    args = parser.parse_args()

    try:
        if args.list:
            asyncio.run(list_examples())
        else:
            document_id = asyncio.run(assemble_widerspruch(
                example_num=args.example,
                export=args.export
            ))

            if document_id:
                print(print_header("Assembly Complete!"))
                print(f"\n✨ Document ID: {document_id}")
                print(f"\n🔗 API Endpoints:")
                print(f"   GET http://localhost:8000/api/documents/{document_id}")
                print(f"   GET http://localhost:8000/api/documents/{document_id}/export/text")
                print(f"   GET http://localhost:8000/api/documents/{document_id}/export/markdown")
                print(f"   GET http://localhost:8000/api/documents/{document_id}/export/docx")

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
