"""
Integration tests for BlockService

These tests verify the integration between:
- BlockService
- MongoDB repository
- Neo4j repository
"""

import pytest
from app.services import block_service
from app.models import Block, BlockCreate, BlockMetadata, BlockRelationships


@pytest.mark.asyncio
async def test_create_block(setup_services, sample_block, cleanup_test_data):
    """Test creating a block through BlockService"""

    # Create block
    block_data = BlockCreate(
        type=sample_block.type,
        title=sample_block.title,
        content=sample_block.content,
        source=sample_block.source,
        level=sample_block.level,
        metadata=sample_block.metadata,
        relationships=sample_block.relationships
    )

    created_block = await block_service.create_block(block_data)

    # Assertions
    assert created_block is not None
    assert created_block.title == sample_block.title
    assert created_block.content == sample_block.content
    assert created_block.type == sample_block.type
    assert created_block.level == sample_block.level

    # Verify block exists in MongoDB
    mongo_block = await block_service.get_block(created_block.id)
    assert mongo_block is not None
    assert mongo_block.id == created_block.id


@pytest.mark.asyncio
async def test_create_block_with_parent(setup_services, sample_block, sample_child_block, cleanup_test_data):
    """Test creating a block with parent-child relationship"""

    # Create parent block first
    parent_data = BlockCreate(
        type=sample_block.type,
        title=sample_block.title,
        content=sample_block.content,
        source=sample_block.source,
        level=sample_block.level,
        metadata=sample_block.metadata,
        relationships=sample_block.relationships
    )
    parent_block = await block_service.create_block(parent_data)

    # Create child block with parent reference
    child_relationships = BlockRelationships(
        parent_ids=[parent_block.id],
        child_ids=[],
        references=[],
        related_to=[]
    )

    child_data = BlockCreate(
        type=sample_child_block.type,
        title=sample_child_block.title,
        content=sample_child_block.content,
        source=sample_child_block.source,
        level=sample_child_block.level,
        metadata=sample_child_block.metadata,
        relationships=child_relationships
    )
    child_block = await block_service.create_block(child_data)

    # Assertions
    assert child_block is not None
    assert parent_block.id in child_block.relationships.parent_ids

    # Verify relationship exists in Neo4j by getting related blocks
    related_blocks = await block_service.get_related_blocks(parent_block.id, max_depth=1)
    related_ids = [b.id for b in related_blocks]
    assert child_block.id in related_ids


@pytest.mark.asyncio
async def test_get_block(setup_services, sample_block, cleanup_test_data):
    """Test retrieving a block by ID"""

    # Create block
    block_data = BlockCreate(
        type=sample_block.type,
        title=sample_block.title,
        content=sample_block.content,
        source=sample_block.source,
        level=sample_block.level,
        metadata=sample_block.metadata,
        relationships=sample_block.relationships
    )
    created_block = await block_service.create_block(block_data)

    # Retrieve block
    retrieved_block = await block_service.get_block(created_block.id)

    # Assertions
    assert retrieved_block is not None
    assert retrieved_block.id == created_block.id
    assert retrieved_block.title == created_block.title
    assert retrieved_block.content == created_block.content


@pytest.mark.asyncio
async def test_get_nonexistent_block(setup_services):
    """Test retrieving a non-existent block returns None"""

    block = await block_service.get_block("nonexistent_id")
    assert block is None


@pytest.mark.asyncio
async def test_update_block(setup_services, sample_block, cleanup_test_data):
    """Test updating a block"""

    # Create block
    block_data = BlockCreate(
        type=sample_block.type,
        title=sample_block.title,
        content=sample_block.content,
        source=sample_block.source,
        level=sample_block.level,
        metadata=sample_block.metadata,
        relationships=sample_block.relationships
    )
    created_block = await block_service.create_block(block_data)

    # Update block
    new_title = "Updated Title"
    new_content = "Updated content for testing."

    updated = await block_service.update_block(
        created_block.id,
        {"title": new_title, "content": new_content}
    )

    # Assertions
    assert updated is True

    # Verify update
    retrieved_block = await block_service.get_block(created_block.id)
    assert retrieved_block.title == new_title
    assert retrieved_block.content == new_content


@pytest.mark.asyncio
async def test_delete_block(setup_services, sample_block, cleanup_test_data):
    """Test deleting a block"""

    # Create block
    block_data = BlockCreate(
        type=sample_block.type,
        title=sample_block.title,
        content=sample_block.content,
        source=sample_block.source,
        level=sample_block.level,
        metadata=sample_block.metadata,
        relationships=sample_block.relationships
    )
    created_block = await block_service.create_block(block_data)

    # Delete block
    deleted = await block_service.delete_block(created_block.id)

    # Assertions
    assert deleted is True

    # Verify deletion
    retrieved_block = await block_service.get_block(created_block.id)
    assert retrieved_block is None


@pytest.mark.asyncio
async def test_list_blocks(setup_services, sample_block, cleanup_test_data):
    """Test listing blocks with pagination"""

    # Create multiple blocks
    for i in range(5):
        block_data = BlockCreate(
            type=sample_block.type,
            title=f"Test Block {i}",
            content=f"Content {i}",
            source=sample_block.source,
            level=sample_block.level,
            metadata=sample_block.metadata,
            relationships=sample_block.relationships
        )
        await block_service.create_block(block_data)

    # List blocks with limit
    blocks = await block_service.list_blocks(limit=3)

    # Assertions
    assert len(blocks) >= 3
    assert all(isinstance(b, Block) for b in blocks)


@pytest.mark.asyncio
async def test_search_blocks_by_tag(setup_services, sample_block, cleanup_test_data):
    """Test searching blocks by tag"""

    # Create blocks with specific tags
    for i in range(3):
        metadata = BlockMetadata(
            law_reference="TEST",
            tags=["integration_test", f"tag_{i}"]
        )
        block_data = BlockCreate(
            type=sample_block.type,
            title=f"Tagged Block {i}",
            content=f"Content {i}",
            source=sample_block.source,
            level=sample_block.level,
            metadata=metadata,
            relationships=sample_block.relationships
        )
        await block_service.create_block(block_data)

    # Search by tag
    results = await block_service.search_blocks(tags=["integration_test"])

    # Assertions
    assert len(results) >= 3
    for block in results:
        assert "integration_test" in block.metadata.tags


@pytest.mark.asyncio
async def test_get_related_blocks_depth(setup_services, cleanup_test_data):
    """Test getting related blocks with depth traversal"""

    # Create a chain of related blocks: block1 -> block2 -> block3

    # Block 1 (root)
    block1_data = BlockCreate(
        type="paragraph",
        title="Block 1",
        content="Root block",
        source="Test",
        level=1,
        metadata=BlockMetadata(tags=["root"]),
        relationships=BlockRelationships(parent_ids=[], child_ids=[], references=[], related_to=[])
    )
    block1 = await block_service.create_block(block1_data)

    # Block 2 (child of block1)
    block2_data = BlockCreate(
        type="absatz",
        title="Block 2",
        content="Child block",
        source="Test",
        level=2,
        metadata=BlockMetadata(tags=["child"]),
        relationships=BlockRelationships(parent_ids=[block1.id], child_ids=[], references=[], related_to=[])
    )
    block2 = await block_service.create_block(block2_data)

    # Block 3 (child of block2)
    block3_data = BlockCreate(
        type="absatz",
        title="Block 3",
        content="Grandchild block",
        source="Test",
        level=3,
        metadata=BlockMetadata(tags=["grandchild"]),
        relationships=BlockRelationships(parent_ids=[block2.id], child_ids=[], references=[], related_to=[])
    )
    block3 = await block_service.create_block(block3_data)

    # Get related blocks with depth 1 (should only get block2)
    related_depth1 = await block_service.get_related_blocks(block1.id, max_depth=1)
    related_ids_depth1 = [b.id for b in related_depth1]
    assert block2.id in related_ids_depth1

    # Get related blocks with depth 2 (should get both block2 and block3)
    related_depth2 = await block_service.get_related_blocks(block1.id, max_depth=2)
    related_ids_depth2 = [b.id for b in related_depth2]
    assert block2.id in related_ids_depth2
    assert block3.id in related_ids_depth2
