#!/usr/bin/env python3
"""
Скрипт импорта SGB IX данных из sample файла

Usage:
    python scripts/import_sgb9.py [--file PATH]
"""

import asyncio
import sys
from pathlib import Path

# Добавить родительскую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.parsers import parse_sgb_file
from app.services import block_service
from app.repositories import mongo_repo, neo4j_repo


async def import_sgb9_data(file_path: str):
    """
    Импортировать SGB IX данные из файла

    :param file_path: Путь к файлу с текстом SGB IX
    """
    print(f"📖 Reading SGB IX from: {file_path}")

    # Парсинг файла
    try:
        blocks = parse_sgb_file(file_path, law_name="SGB IX")
        print(f"✅ Parsed {len(blocks)} blocks")
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return

    # Инициализация сервисов
    print("\n🔌 Connecting to databases...")
    await block_service.initialize()
    print("✅ Connected to databases")

    # Импорт блоков
    print(f"\n📥 Importing {len(blocks)} blocks...")
    result = await block_service.import_blocks(blocks)

    print(f"\n📊 Import Results:")
    print(f"   Total: {result['total']}")
    print(f"   Success: {result['success']} ✅")
    print(f"   Failed: {result['failed']} ❌")

    if result['failed_ids']:
        print(f"\n❌ Failed IDs:")
        for failed_id in result['failed_ids']:
            print(f"   - {failed_id}")

    # Закрытие соединений
    await block_service.shutdown()
    print("\n👋 Import complete!")


async def show_stats():
    """Показать статистику импортированных данных"""
    await block_service.initialize()

    stats = mongo_repo.get_stats()
    print("\n📊 Database Statistics:")
    print(f"   Blocks: {stats['blocks']}")
    print(f"   Rules: {stats['rules']}")
    print(f"   Documents: {stats['documents']}")
    print(f"   Templates: {stats['templates']}")

    # Показать несколько примеров блоков
    blocks = await block_service.list_blocks(limit=5)
    print(f"\n📦 Sample Blocks:")
    for block in blocks:
        print(f"   - {block.id}: {block.title}")

    await block_service.shutdown()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Import SGB IX data")
    parser.add_argument(
        "--file",
        default="data/samples/sgb9_sample.txt",
        help="Path to SGB IX file (default: data/samples/sgb9_sample.txt)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics after import"
    )
    args = parser.parse_args()

    # Проверить существование файла
    if not Path(args.file).exists():
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    # Запустить импорт
    asyncio.run(import_sgb9_data(args.file))

    # Показать статистику если запрошено
    if args.stats:
        asyncio.run(show_stats())


if __name__ == "__main__":
    main()
