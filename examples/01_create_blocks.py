#!/usr/bin/env python3
"""
Пример создания блоков через API

Usage:
    python examples/01_create_blocks.py
"""

import requests
import json
from typing import Dict, Any

# API base URL
API_BASE = "http://localhost:8000/api"


def create_block(block_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать блок через API

    :param block_data: Данные блока
    :return: Созданный блок
    """
    response = requests.post(
        f"{API_BASE}/blocks",
        json=block_data,
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def get_block(block_id: str) -> Dict[str, Any]:
    """
    Получить блок по ID

    :param block_id: ID блока
    :return: Блок
    """
    response = requests.get(f"{API_BASE}/blocks/{block_id}")
    response.raise_for_status()
    return response.json()


def main():
    print("📦 Creating blocks via API\n")

    # Пример 1: Создание блока параграфа
    paragraph_block = {
        "type": "paragraph",
        "title": "§ 5 SGB IX - Leistungen zur Teilhabe",
        "content": "Die Leistungen zur Teilhabe umfassen die notwendigen Sozialleistungen, um unabhängig von der Ursache der Behinderung...",
        "source": "SGB IX",
        "level": 1,
        "metadata": {
            "law_reference": "SGB IX",
            "paragraph": "5",
            "effective_date": "2018-01-01",
            "tags": ["teilhabe", "leistungen", "behinderung"]
        },
        "relationships": {
            "parent_ids": [],
            "child_ids": [],
            "references": [],
            "related_to": []
        }
    }

    print("Creating paragraph block...")
    block1 = create_block(paragraph_block)
    print(f"✅ Created block: {block1['id']}")
    print(f"   Title: {block1['title']}")
    print(f"   Type: {block1['type']}")
    print()

    # Пример 2: Создание блока абзаца (дочерний блок)
    absatz_block = {
        "type": "absatz",
        "title": "§ 5 Abs. 1 - Umfang der Leistungen",
        "content": "Die Leistungen zur Teilhabe werden zur Förderung der Selbstbestimmung und gleichberechtigten Teilhabe am Leben in der Gesellschaft erbracht.",
        "source": "SGB IX",
        "level": 2,
        "metadata": {
            "law_reference": "SGB IX",
            "paragraph": "5",
            "absatz": "1",
            "effective_date": "2018-01-01",
            "tags": ["teilhabe", "selbstbestimmung", "gleichberechtigung"]
        },
        "relationships": {
            "parent_ids": [block1['id']],  # Ссылка на родительский параграф
            "child_ids": [],
            "references": [],
            "related_to": []
        }
    }

    print("Creating absatz block (child of paragraph)...")
    block2 = create_block(absatz_block)
    print(f"✅ Created block: {block2['id']}")
    print(f"   Title: {block2['title']}")
    print(f"   Parent: {block2['relationships']['parent_ids']}")
    print()

    # Пример 3: Создание кастомного блока
    custom_block = {
        "type": "custom",
        "title": "Widerspruchsgrund: Unzureichende Begründung",
        "content": "Die Ablehnung der Leistung wurde nicht ausreichend begründet. Es fehlt eine nachvollziehbare Darlegung, warum die beantragte Maßnahme nicht erforderlich sein soll.",
        "source": "Custom",
        "level": 1,
        "metadata": {
            "category": "widerspruch",
            "subcategory": "begründungsmangel",
            "tags": ["widerspruch", "begründung", "rechtsmittel"]
        },
        "relationships": {
            "parent_ids": [],
            "child_ids": [],
            "references": [block1['id']],  # Ссылается на § 5
            "related_to": []
        }
    }

    print("Creating custom block with reference...")
    block3 = create_block(custom_block)
    print(f"✅ Created block: {block3['id']}")
    print(f"   Title: {block3['title']}")
    print(f"   References: {block3['relationships']['references']}")
    print()

    # Получение связанных блоков
    print(f"Getting related blocks for {block1['id']}...")
    response = requests.get(f"{API_BASE}/blocks/{block1['id']}/related?max_depth=2")
    related = response.json()
    print(f"✅ Found {len(related)} related blocks")
    for rel_block in related:
        print(f"   - {rel_block['id']}: {rel_block['title']}")

    print("\n✨ Example completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
