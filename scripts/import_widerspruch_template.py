#!/usr/bin/env python3
"""
Import Widerspruch template and blocks

This script imports the ready-to-use Widerspruch template including:
- Custom blocks for all sections
- Template definition with conditional sections
- Example contexts for testing

Usage:
    python scripts/import_widerspruch_template.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import block_service, assembly_service
from app.models import (
    Block,
    BlockCreate,
    BlockMetadata,
    BlockRelationships,
    Template,
    TemplateSection,
    AssemblyRequest
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def import_widerspruch_template():
    """Import Widerspruch template from JSON file"""

    # Read template file
    template_file = Path("data/templates/widerspruch_template.json")
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return False

    print_header("Importing Widerspruch Template")

    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
        return False

    # Initialize services
    print("\n🔌 Initializing services...")
    await block_service.initialize()
    print("✅ Services initialized")

    # Import blocks
    print(f"\n📦 Importing {len(data['blocks'])} blocks...")
    imported_count = 0
    skipped_count = 0

    for block_data in data['blocks']:
        # Check if block already exists
        existing = await block_service.get_block(block_data['id'])
        if existing:
            print(f"   ⚠️  Block exists, skipping: {block_data['id']}")
            skipped_count += 1
            continue

        try:
            # Create block
            block_create = BlockCreate(
                type=block_data['type'],
                title=block_data['title'],
                content=block_data['content'],
                source=block_data['source'],
                level=block_data['level'],
                metadata=BlockMetadata(**block_data['metadata']),
                relationships=BlockRelationships(**block_data['relationships'])
            )

            block = await block_service.create_block(block_create)
            print(f"   ✅ Created: {block.id} - {block.title}")
            imported_count += 1
        except Exception as e:
            print(f"   ❌ Failed to create {block_data['id']}: {e}")

    print(f"\n📊 Blocks: {imported_count} imported, {skipped_count} skipped")

    # Import template
    print(f"\n📋 Importing template...")
    template_data = data['template']

    # Check if template exists
    existing_template = await assembly_service.get_template(template_data['id'])
    if existing_template:
        print(f"   ⚠️  Template already exists: {template_data['id']}")
        print(f"   Skipping template import")
    else:
        try:
            # Parse sections
            sections = []
            for section_data in template_data['sections']:
                section = TemplateSection(
                    name=section_data['name'],
                    blocks=section_data['blocks'],
                    conditions=section_data.get('conditions', {})
                )
                sections.append(section)

            # Create template
            template = Template(
                id=template_data['id'],
                name=template_data['name'],
                description=template_data['description'],
                sections=sections,
                metadata=template_data['metadata']
            )

            success = await assembly_service.create_template(template)
            if success:
                print(f"   ✅ Template created: {template.id}")
                print(f"      Name: {template.name}")
                print(f"      Sections: {len(template.sections)}")
            else:
                print(f"   ❌ Failed to create template")
        except Exception as e:
            print(f"   ❌ Error creating template: {e}")

    # Show example contexts
    print(f"\n📝 Example contexts available:")
    for i, example in enumerate(data['example_contexts'], 1):
        print(f"   {i}. {example['name']}")
        print(f"      {example['description']}")

    # Cleanup
    await block_service.shutdown()

    print_header("Import Complete!")
    print("\n✨ Widerspruch template is ready to use!")
    print("\n🚀 Next steps:")
    print("   1. Start API: uvicorn app.main:app --reload")
    print("   2. Test assembly:")
    print("      python scripts/assemble_widerspruch_example.py")
    print("   3. View template:")
    print("      curl http://localhost:8000/api/templates/widerspruch_standard_v1")

    return True


async def show_template_info():
    """Show information about the imported template"""
    await block_service.initialize()

    template = await assembly_service.get_template("widerspruch_standard_v1")
    if not template:
        print("❌ Template not found. Run import first.")
        await block_service.shutdown()
        return

    print_header("Widerspruch Template Info")
    print(f"\nID: {template.id}")
    print(f"Name: {template.name}")
    print(f"Description: {template.description}")
    print(f"\nSections: {len(template.sections)}")

    for i, section in enumerate(template.sections, 1):
        print(f"\n  {i}. {section.name}")
        print(f"     Blocks: {len(section.blocks)}")
        if section.conditions:
            print(f"     Conditions: {section.conditions}")

    await block_service.shutdown()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import Widerspruch template"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show template information"
    )
    args = parser.parse_args()

    try:
        if args.info:
            asyncio.run(show_template_info())
        else:
            asyncio.run(import_widerspruch_template())
    except KeyboardInterrupt:
        print("\n\n⚠️  Import cancelled")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
