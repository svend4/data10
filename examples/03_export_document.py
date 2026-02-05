#!/usr/bin/env python3
"""
Пример экспорта документа в различные форматы

Usage:
    python examples/03_export_document.py <document_id>
"""

import requests
import sys
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8000/api"


def export_text(document_id: str, output_path: str):
    """
    Экспорт документа в текстовый формат

    :param document_id: ID документа
    :param output_path: Путь для сохранения
    """
    response = requests.get(f"{API_BASE}/documents/{document_id}/export/text")
    response.raise_for_status()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.text)

    print(f"✅ Text exported to: {output_path}")


def export_markdown(document_id: str, output_path: str):
    """
    Экспорт документа в Markdown формат

    :param document_id: ID документа
    :param output_path: Путь для сохранения
    """
    response = requests.get(f"{API_BASE}/documents/{document_id}/export/markdown")
    response.raise_for_status()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.text)

    print(f"✅ Markdown exported to: {output_path}")


def export_docx(document_id: str, output_path: str):
    """
    Экспорт документа в DOCX формат (Microsoft Word)

    :param document_id: ID документа
    :param output_path: Путь для сохранения
    """
    response = requests.get(f"{API_BASE}/documents/{document_id}/export/docx")
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"✅ DOCX exported to: {output_path}")


def preview_document(document_id: str):
    """
    Предварительный просмотр документа

    :param document_id: ID документа
    """
    response = requests.get(f"{API_BASE}/documents/{document_id}")
    response.raise_for_status()

    document = response.json()

    print("\n" + "=" * 70)
    print(f"Document: {document['title']}")
    print("=" * 70)
    print(f"ID: {document['id']}")
    print(f"Status: {document['status']}")
    print(f"Template: {document.get('template_id', 'N/A')}")
    print(f"Created: {document['created_at']}")
    print(f"Blocks: {len(document['blocks'])}")

    if document.get('context'):
        print(f"\nContext variables:")
        for key, value in document['context'].items():
            print(f"  - {key}: {value}")

    print("\n" + "-" * 70)
    print("Content Preview:")
    print("-" * 70)

    for block in sorted(document['blocks'], key=lambda b: b['order']):
        indent = "  " * (block['level'] - 1)
        content = block['content'][:100] + "..." if len(block['content']) > 100 else block['content']
        print(f"{indent}[{block['order']}] {content}")

    print("=" * 70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python 03_export_document.py <document_id>")
        print("\nExample:")
        print("  python 03_export_document.py doc_abc123def456")
        sys.exit(1)

    document_id = sys.argv[1]

    print(f"📤 Exporting document: {document_id}\n")

    # Создать директорию для экспорта
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    # Предварительный просмотр
    print("Preview:")
    try:
        preview_document(document_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Document not found: {document_id}")
            print("\n💡 Tip: Run 02_assemble_document.py first to create a document")
            sys.exit(1)
        raise

    # Экспорт в различные форматы
    print("\nExporting to formats...")

    try:
        # Text
        text_path = export_dir / f"{document_id}.txt"
        export_text(document_id, str(text_path))

        # Markdown
        md_path = export_dir / f"{document_id}.md"
        export_markdown(document_id, str(md_path))

        # DOCX
        docx_path = export_dir / f"{document_id}.docx"
        export_docx(document_id, str(docx_path))

        print("\n✨ All exports completed successfully!")
        print(f"\n📁 Exported files in: {export_dir.absolute()}")
        print(f"   - {text_path.name} (Text)")
        print(f"   - {md_path.name} (Markdown)")
        print(f"   - {docx_path.name} (Microsoft Word)")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Export Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Export cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
