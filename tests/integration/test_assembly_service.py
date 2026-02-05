"""
Integration tests for AssemblyService

These tests verify document assembly, template processing, and export functionality.
"""

import pytest
from io import BytesIO
from app.services import assembly_service, block_service
from app.models import (
    Block,
    BlockCreate,
    BlockMetadata,
    BlockRelationships,
    Template,
    TemplateSection,
    AssemblyRequest,
    DocumentStatus
)


@pytest.fixture
async def setup_test_blocks(setup_services, cleanup_test_data):
    """Create test blocks for assembly"""

    blocks_data = [
        BlockCreate(
            type="paragraph",
            title="Introduction Block",
            content="This is an introduction to the document.",
            source="Test",
            level=1,
            metadata=BlockMetadata(tags=["intro"]),
            relationships=BlockRelationships(parent_ids=[], child_ids=[], references=[], related_to=[])
        ),
        BlockCreate(
            type="paragraph",
            title="Main Content Block",
            content="This is the main content of the document.",
            source="Test",
            level=1,
            metadata=BlockMetadata(tags=["main"]),
            relationships=BlockRelationships(parent_ids=[], child_ids=[], references=[], related_to=[])
        ),
        BlockCreate(
            type="paragraph",
            title="Conclusion Block",
            content="This is the conclusion of the document.",
            source="Test",
            level=1,
            metadata=BlockMetadata(tags=["conclusion"]),
            relationships=BlockRelationships(parent_ids=[], child_ids=[], references=[], related_to=[])
        )
    ]

    created_blocks = []
    for block_data in blocks_data:
        block = await block_service.create_block(block_data)
        created_blocks.append(block)

    return created_blocks


@pytest.fixture
async def setup_test_template(setup_test_blocks):
    """Create a test template using test blocks"""

    blocks = setup_test_blocks

    template = Template(
        id="test_assembly_template",
        name="Test Assembly Template",
        description="Template for testing document assembly",
        sections=[
            TemplateSection(
                name="intro",
                blocks=[blocks[0].id],
                conditions={}
            ),
            TemplateSection(
                name="main",
                blocks=[blocks[1].id],
                conditions={"include_main": True}
            ),
            TemplateSection(
                name="conclusion",
                blocks=[blocks[2].id],
                conditions={}
            )
        ],
        metadata={"category": "test", "version": "1.0"}
    )

    # Create template
    success = await assembly_service.create_template(template)
    assert success is True

    return template


@pytest.mark.asyncio
async def test_create_template(setup_services, cleanup_test_data):
    """Test creating a template"""

    template = Template(
        id="test_template_create",
        name="Test Template",
        description="A test template",
        sections=[
            TemplateSection(
                name="section1",
                blocks=["block1"],
                conditions={}
            )
        ],
        metadata={"test": True}
    )

    success = await assembly_service.create_template(template)
    assert success is True

    # Verify template exists
    retrieved = await assembly_service.get_template(template.id)
    assert retrieved is not None
    assert retrieved.id == template.id
    assert retrieved.name == template.name


@pytest.mark.asyncio
async def test_get_template(setup_services, setup_test_template):
    """Test retrieving a template"""

    template = setup_test_template

    retrieved = await assembly_service.get_template(template.id)
    assert retrieved is not None
    assert retrieved.id == template.id
    assert retrieved.name == template.name
    assert len(retrieved.sections) == len(template.sections)


@pytest.mark.asyncio
async def test_list_templates(setup_services, setup_test_template):
    """Test listing templates"""

    templates = await assembly_service.list_templates()
    assert len(templates) > 0
    assert any(t.id == setup_test_template.id for t in templates)


@pytest.mark.asyncio
async def test_assemble_document_basic(setup_services, setup_test_template):
    """Test basic document assembly"""

    template = setup_test_template

    request = AssemblyRequest(
        template_id=template.id,
        title="Test Assembled Document",
        context={"include_main": True}
    )

    result = await assembly_service.assemble_document(request)

    # Assertions
    assert result is not None
    assert result.document is not None
    assert result.document.title == "Test Assembled Document"
    assert result.document.status == DocumentStatus.ASSEMBLED
    assert result.blocks_included == 3  # intro + main + conclusion
    assert len(result.document.blocks) == 3


@pytest.mark.asyncio
async def test_assemble_document_with_conditions(setup_services, setup_test_template):
    """Test document assembly with conditional sections"""

    template = setup_test_template

    # Assemble with main section excluded
    request = AssemblyRequest(
        template_id=template.id,
        title="Test Conditional Document",
        context={"include_main": False}
    )

    result = await assembly_service.assemble_document(request)

    # Assertions - should only have intro and conclusion (main excluded)
    assert result.blocks_included == 2
    assert len(result.document.blocks) == 2


@pytest.mark.asyncio
async def test_assemble_document_invalid_template(setup_services):
    """Test assembly with invalid template ID"""

    request = AssemblyRequest(
        template_id="nonexistent_template",
        title="Test Invalid",
        context={}
    )

    with pytest.raises(ValueError, match="Template .* not found"):
        await assembly_service.assemble_document(request)


@pytest.mark.asyncio
async def test_get_document(setup_services, setup_test_template):
    """Test retrieving a document"""

    # First assemble a document
    request = AssemblyRequest(
        template_id=setup_test_template.id,
        title="Test Document Retrieval",
        context={"include_main": True}
    )
    result = await assembly_service.assemble_document(request)
    document_id = result.document.id

    # Retrieve document
    retrieved = await assembly_service.get_document(document_id)

    # Assertions
    assert retrieved is not None
    assert retrieved.id == document_id
    assert retrieved.title == "Test Document Retrieval"
    assert len(retrieved.blocks) == 3


@pytest.mark.asyncio
async def test_list_documents(setup_services, setup_test_template):
    """Test listing documents"""

    # Create a document
    request = AssemblyRequest(
        template_id=setup_test_template.id,
        title="Test Document List",
        context={"include_main": True}
    )
    await assembly_service.assemble_document(request)

    # List documents
    documents = await assembly_service.list_documents(limit=10)

    # Assertions
    assert len(documents) > 0
    assert any(d.title == "Test Document List" for d in documents)


@pytest.mark.asyncio
async def test_update_document_status(setup_services, setup_test_template):
    """Test updating document status"""

    # Create document
    request = AssemblyRequest(
        template_id=setup_test_template.id,
        title="Test Status Update",
        context={"include_main": True}
    )
    result = await assembly_service.assemble_document(request)
    document_id = result.document.id

    # Update status
    success = await assembly_service.update_document_status(
        document_id,
        DocumentStatus.REVIEWED
    )

    # Assertions
    assert success is True

    # Verify update
    document = await assembly_service.get_document(document_id)
    assert document.status == DocumentStatus.REVIEWED


@pytest.mark.asyncio
async def test_render_document_text(setup_services, setup_test_template):
    """Test rendering document as text"""

    # Create document
    request = AssemblyRequest(
        template_id=setup_test_template.id,
        title="Test Text Rendering",
        context={"include_main": True}
    )
    result = await assembly_service.assemble_document(request)
    document_id = result.document.id

    # Render as text
    text = await assembly_service.render_document_text(document_id)

    # Assertions
    assert text is not None
    assert "Test Text Rendering" in text
    assert "introduction" in text.lower()
    assert "main content" in text.lower()
    assert "conclusion" in text.lower()


@pytest.mark.asyncio
async def test_export_document_markdown(setup_services, setup_test_template):
    """Test exporting document as Markdown"""

    # Create document
    request = AssemblyRequest(
        template_id=setup_test_template.id,
        title="Test Markdown Export",
        context={"include_main": True}
    )
    result = await assembly_service.assemble_document(request)
    document_id = result.document.id

    # Export as Markdown
    markdown = await assembly_service.export_document_markdown(document_id)

    # Assertions
    assert markdown is not None
    assert "# Test Markdown Export" in markdown
    assert "**Status**:" in markdown
    assert "**Created**:" in markdown
    assert "##" in markdown  # Block headers


@pytest.mark.asyncio
async def test_export_document_docx(setup_services, setup_test_template):
    """Test exporting document as DOCX"""

    # Create document
    request = AssemblyRequest(
        template_id=setup_test_template.id,
        title="Test DOCX Export",
        context={"include_main": True}
    )
    result = await assembly_service.assemble_document(request)
    document_id = result.document.id

    # Export as DOCX
    docx_buffer = await assembly_service.export_document_docx(document_id)

    # Assertions
    assert docx_buffer is not None
    assert isinstance(docx_buffer, BytesIO)
    assert docx_buffer.tell() == 0  # Buffer should be at start

    # Verify buffer has content
    content = docx_buffer.read()
    assert len(content) > 0
    assert content[:4] == b'PK\x03\x04'  # DOCX is a ZIP file


@pytest.mark.asyncio
async def test_export_nonexistent_document(setup_services):
    """Test exporting non-existent document raises error"""

    with pytest.raises(ValueError, match="Document .* not found"):
        await assembly_service.render_document_text("nonexistent_doc")

    with pytest.raises(ValueError, match="Document .* not found"):
        await assembly_service.export_document_markdown("nonexistent_doc")

    with pytest.raises(ValueError, match="Document .* not found"):
        await assembly_service.export_document_docx("nonexistent_doc")


@pytest.mark.asyncio
async def test_document_block_ordering(setup_services, setup_test_blocks):
    """Test that blocks are ordered correctly in assembled document"""

    blocks = setup_test_blocks

    # Create template with specific block order
    template = Template(
        id="test_ordering_template",
        name="Order Test Template",
        description="Test block ordering",
        sections=[
            TemplateSection(name="s1", blocks=[blocks[2].id], conditions={}),  # Conclusion first
            TemplateSection(name="s2", blocks=[blocks[0].id], conditions={}),  # Intro second
            TemplateSection(name="s3", blocks=[blocks[1].id], conditions={})   # Main third
        ],
        metadata={}
    )
    await assembly_service.create_template(template)

    # Assemble document
    request = AssemblyRequest(
        template_id=template.id,
        title="Order Test",
        context={}
    )
    result = await assembly_service.assemble_document(request)

    # Verify order matches template section order
    doc_blocks = sorted(result.document.blocks, key=lambda b: b.order)
    assert doc_blocks[0].block_id == blocks[2].id  # Conclusion
    assert doc_blocks[1].block_id == blocks[0].id  # Intro
    assert doc_blocks[2].block_id == blocks[1].id  # Main
