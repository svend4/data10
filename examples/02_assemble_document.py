#!/usr/bin/env python3
"""
Пример сборки документа из блоков через API

Usage:
    python examples/02_assemble_document.py
"""

import requests
import json
from typing import Dict, Any, List

# API base URL
API_BASE = "http://localhost:8000/api"


def create_template(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать шаблон документа

    :param template_data: Данные шаблона
    :return: Созданный шаблон
    """
    response = requests.post(
        f"{API_BASE}/templates",
        json=template_data,
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def assemble_document(assembly_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Собрать документ из блоков

    :param assembly_request: Запрос на сборку
    :return: Результат сборки
    """
    response = requests.post(
        f"{API_BASE}/documents/assemble",
        json=assembly_request,
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def get_document(document_id: str) -> Dict[str, Any]:
    """
    Получить документ по ID

    :param document_id: ID документа
    :return: Документ
    """
    response = requests.get(f"{API_BASE}/documents/{document_id}")
    response.raise_for_status()
    return response.json()


def list_documents(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Получить список документов

    :param limit: Лимит
    :return: Список документов
    """
    response = requests.get(f"{API_BASE}/documents?limit={limit}")
    response.raise_for_status()
    return response.json()


def main():
    print("📄 Assembling documents via API\n")

    # Шаг 1: Создание блоков (для примера)
    print("Step 1: Creating sample blocks...")

    blocks_data = [
        {
            "id": "sgb9_para5",
            "type": "paragraph",
            "title": "§ 5 SGB IX - Leistungen zur Teilhabe",
            "content": "Die Leistungen zur Teilhabe umfassen die notwendigen Sozialleistungen...",
            "source": "SGB IX",
            "level": 1,
            "metadata": {"law_reference": "SGB IX", "paragraph": "5", "tags": ["teilhabe"]},
            "relationships": {"parent_ids": [], "child_ids": [], "references": [], "related_to": []}
        },
        {
            "id": "widerspruch_intro",
            "type": "custom",
            "title": "Widerspruch - Einleitung",
            "content": "Hiermit lege ich Widerspruch gegen den Bescheid vom [DATUM] ein.",
            "source": "Custom",
            "level": 1,
            "metadata": {"category": "widerspruch", "tags": ["widerspruch", "einleitung"]},
            "relationships": {"parent_ids": [], "child_ids": [], "references": [], "related_to": []}
        },
        {
            "id": "widerspruch_grund",
            "type": "custom",
            "title": "Widerspruchsgrund",
            "content": "Die Ablehnung ist rechtswidrig, da die Voraussetzungen nach § 5 SGB IX erfüllt sind.",
            "source": "Custom",
            "level": 1,
            "metadata": {"category": "widerspruch", "tags": ["widerspruch", "begründung"]},
            "relationships": {"parent_ids": [], "child_ids": [], "references": ["sgb9_para5"], "related_to": []}
        }
    ]

    created_blocks = []
    for block_data in blocks_data:
        try:
            response = requests.post(f"{API_BASE}/blocks", json=block_data)
            if response.status_code in [200, 201]:
                created_blocks.append(response.json())
                print(f"   ✅ Created: {block_data['id']}")
        except:
            print(f"   ⚠️  Block {block_data['id']} may already exist")

    print()

    # Шаг 2: Создание шаблона документа
    print("Step 2: Creating document template...")

    template_data = {
        "id": "widerspruch_template",
        "name": "Widerspruch gegen Bescheid",
        "description": "Standardvorlage für Widerspruch gegen Ablehnungsbescheid",
        "sections": [
            {
                "name": "header",
                "blocks": ["widerspruch_intro"],
                "conditions": {}
            },
            {
                "name": "legal_basis",
                "blocks": ["sgb9_para5"],
                "conditions": {"include_legal_basis": True}
            },
            {
                "name": "reasoning",
                "blocks": ["widerspruch_grund"],
                "conditions": {}
            }
        ],
        "metadata": {
            "category": "widerspruch",
            "version": "1.0"
        }
    }

    try:
        template = create_template(template_data)
        print(f"   ✅ Template created: {template['id']}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print(f"   ⚠️  Template already exists, using existing one")
            template = {"id": "widerspruch_template"}
        else:
            raise

    print()

    # Шаг 3: Сборка документа
    print("Step 3: Assembling document...")

    assembly_request = {
        "template_id": "widerspruch_template",
        "title": "Widerspruch - Hans Müller",
        "context": {
            "include_legal_basis": True,
            "client_name": "Hans Müller",
            "bescheid_date": "2024-01-15",
            "case_number": "12345/2024"
        }
    }

    result = assemble_document(assembly_request)
    document = result['document']

    print(f"   ✅ Document assembled: {document['id']}")
    print(f"   Title: {document['title']}")
    print(f"   Blocks included: {result['blocks_included']}")
    print(f"   Rules applied: {result['rules_applied']}")
    print(f"   Status: {document['status']}")
    print()

    # Шаг 4: Просмотр содержимого документа
    print("Step 4: Document content:")
    print("   " + "=" * 60)

    for block in sorted(document['blocks'], key=lambda b: b['order']):
        indent = "   " + ("  " * (block['level'] - 1))
        print(f"{indent}[{block['order']}] {block['content'][:80]}...")

    print("   " + "=" * 60)
    print()

    # Шаг 5: Список всех документов
    print("Step 5: Listing all documents...")
    documents = list_documents(limit=5)
    print(f"   Found {len(documents)} documents:")
    for doc in documents:
        print(f"   - {doc['id']}: {doc['title']} ({doc['status']})")

    print("\n✨ Example completed successfully!")
    print(f"\n💡 Document ID for export: {document['id']}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
