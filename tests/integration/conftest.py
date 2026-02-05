"""
Pytest fixtures for integration tests
"""

import pytest
import asyncio
from typing import AsyncGenerator
from app.services import block_service, assembly_service
from app.repositories import mongo_repo, neo4j_repo
from app.models import Block, BlockMetadata, BlockRelationships, Template, TemplateSection


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def setup_services():
    """
    Initialize services before each test and cleanup after
    """
    # Initialize services
    await block_service.initialize()

    yield

    # Cleanup after test
    # Note: In production, you might want to clean up test data here
    await block_service.shutdown()


@pytest.fixture
def sample_block():
    """Create a sample block for testing"""
    return Block(
        id="test_block_001",
        type="paragraph",
        title="Test Paragraph",
        content="This is a test paragraph content.",
        source="Test",
        level=1,
        metadata=BlockMetadata(
            law_reference="TEST",
            paragraph="1",
            tags=["test", "sample"]
        ),
        relationships=BlockRelationships(
            parent_ids=[],
            child_ids=[],
            references=[],
            related_to=[]
        )
    )


@pytest.fixture
def sample_child_block():
    """Create a sample child block for testing"""
    return Block(
        id="test_block_002",
        type="absatz",
        title="Test Absatz",
        content="This is a test absatz content.",
        source="Test",
        level=2,
        metadata=BlockMetadata(
            law_reference="TEST",
            paragraph="1",
            absatz="1",
            tags=["test", "sample", "child"]
        ),
        relationships=BlockRelationships(
            parent_ids=["test_block_001"],
            child_ids=[],
            references=[],
            related_to=[]
        )
    )


@pytest.fixture
def sample_template():
    """Create a sample template for testing"""
    return Template(
        id="test_template_001",
        name="Test Template",
        description="A template for testing",
        sections=[
            TemplateSection(
                name="section_1",
                blocks=["test_block_001"],
                conditions={}
            ),
            TemplateSection(
                name="section_2",
                blocks=["test_block_002"],
                conditions={"include_section_2": True}
            )
        ],
        metadata={"category": "test", "version": "1.0"}
    )


@pytest.fixture
async def cleanup_test_data():
    """
    Cleanup test data after test execution
    """
    yield

    # Clean up test blocks
    test_block_ids = ["test_block_001", "test_block_002", "test_block_003"]
    for block_id in test_block_ids:
        try:
            mongo_repo.delete_block(block_id)
            neo4j_repo.delete_block_node(block_id)
        except:
            pass

    # Clean up test templates
    try:
        mongo_repo.db.templates.delete_many({"id": {"$regex": "^test_"}})
    except:
        pass

    # Clean up test documents
    try:
        mongo_repo.db.documents.delete_many({"id": {"$regex": "^doc_test_"}})
    except:
        pass
