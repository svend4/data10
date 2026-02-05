#!/usr/bin/env python3
"""
Example 5: ML Semantic Search
Demonstrates semantic search and similarity features
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.nlp_service import nlp_service
from app.services import block_service


async def main():
    """Main example function"""
    print("=" * 70)
    print("  Example 5: ML Semantic Search")
    print("=" * 70)

    # Initialize services
    print("\n📦 Initializing services...")
    await nlp_service.initialize()
    await block_service.initialize()

    if not nlp_service.is_ready():
        print("\n❌ NLP service not ready!")
        print("Please run: python scripts/setup_nlp_models.py")
        return

    print("✅ Services ready!")

    # Sample blocks (in real scenario, these would be in database)
    sample_texts = {
        "block1": {
            "title": "§ 5 Leistungen zur Teilhabe",
            "content": "Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe am Arbeitsleben."
        },
        "block2": {
            "title": "§ 29 Persönliches Budget",
            "content": "Auf Antrag werden Leistungen zur Teilhabe als Persönliches Budget ausgeführt."
        },
        "block3": {
            "title": "§ 17 Rehabilitationsträger",
            "content": "Die Rehabilitationsträger sind für die Leistungen zur Teilhabe zuständig."
        },
        "block4": {
            "title": "§ 42 Leistungen zur Teilhabe am Arbeitsleben",
            "content": "Zur Teilhabe am Arbeitsleben werden Leistungen erbracht, die erforderlich sind."
        },
        "block5": {
            "title": "§ 64 Medizinische Rehabilitation",
            "content": "Leistungen zur medizinischen Rehabilitation umfassen Behandlung und Therapie."
        }
    }

    # 1. Generate Embeddings
    print("\n" + "=" * 70)
    print("1. GENERATING EMBEDDINGS")
    print("=" * 70)

    embeddings = {}
    print("\n🔄 Generating embeddings for all blocks...")

    for block_id, block_data in sample_texts.items():
        text = f"{block_data['title']} {block_data['content']}"
        embedding = nlp_service.generate_embedding(text)
        embeddings[block_id] = embedding
        print(f"  ✅ {block_id}: {block_data['title']}")

    print(f"\n✅ Generated {len(embeddings)} embeddings (384 dimensions each)")

    # 2. Semantic Similarity
    print("\n" + "=" * 70)
    print("2. SEMANTIC SIMILARITY")
    print("=" * 70)

    # Compare block1 with all others
    query_block = "block1"
    query_text = f"{sample_texts[query_block]['title']} {sample_texts[query_block]['content']}"

    print(f"\n🔍 Query block: {sample_texts[query_block]['title']}")
    print(f"   Content: {sample_texts[query_block]['content'][:80]}...\n")

    similarities = []
    for block_id, block_data in sample_texts.items():
        if block_id == query_block:
            continue

        text = f"{block_data['title']} {block_data['content']}"
        similarity = nlp_service.calculate_similarity(query_text, text)
        similarities.append((block_id, similarity, block_data))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    print("📊 Similarity scores:")
    for block_id, score, block_data in similarities:
        print(f"\n  {block_data['title']}")
        print(f"    Similarity: {score:.4f} {'🟢' if score > 0.7 else '🟡' if score > 0.5 else '⚪'}")
        print(f"    {block_data['content'][:80]}...")

    # 3. Find Most Similar (Batch)
    print("\n" + "=" * 70)
    print("3. BATCH SIMILARITY SEARCH")
    print("=" * 70)

    query = "Wie bekomme ich finanzielle Unterstützung für die Arbeit?"
    print(f"\n🔍 Query: \"{query}\"")

    # Prepare candidates
    candidates = [
        f"{block_data['title']} {block_data['content']}"
        for block_data in sample_texts.values()
    ]

    # Find most similar
    top_results = nlp_service.find_most_similar(query, candidates, top_k=3)

    print(f"\n📊 Top 3 most similar blocks:\n")
    for rank, (idx, similarity) in enumerate(top_results, 1):
        block_id = list(sample_texts.keys())[idx]
        block_data = sample_texts[block_id]

        print(f"  {rank}. {block_data['title']}")
        print(f"     Similarity: {similarity:.4f}")
        print(f"     {block_data['content'][:80]}...\n")

    # 4. Semantic Search in Real Database
    print("\n" + "=" * 70)
    print("4. SEMANTIC SEARCH IN DATABASE")
    print("=" * 70)

    # Try to search actual blocks if they exist
    try:
        blocks = await block_service.list_blocks(limit=10)

        if len(blocks) > 0:
            print(f"\n🔍 Searching through {len(blocks)} blocks from database...")

            # Natural language queries
            queries = [
                "Welche Leistungen gibt es für Menschen mit Behinderung?",
                "Wie beantrage ich ein persönliches Budget?",
                "Was ist medizinische Rehabilitation?"
            ]

            for query in queries:
                print(f"\n📝 Query: \"{query}\"")

                # Prepare candidates from database blocks
                db_candidates = [
                    f"{block.title} {block.content}"
                    for block in blocks
                ]

                # Find similar
                results = nlp_service.find_most_similar(query, db_candidates, top_k=2)

                if results:
                    print("  Results:")
                    for idx, similarity in results:
                        block = blocks[idx]
                        print(f"    • {block.title} (similarity: {similarity:.4f})")
                        print(f"      {block.content[:100]}...")
                else:
                    print("  No similar blocks found.")
        else:
            print("\n⚠️  No blocks in database.")
            print("  Run: python scripts/quickstart.py")

    except Exception as e:
        print(f"\n⚠️  Could not access database: {e}")
        print("  Make sure MongoDB is running and blocks are imported.")

    # 5. Similarity Matrix
    print("\n" + "=" * 70)
    print("5. SIMILARITY MATRIX")
    print("=" * 70)

    print("\n📊 Pairwise similarities between all sample blocks:\n")

    # Header
    block_ids = list(sample_texts.keys())
    print("         ", end="")
    for block_id in block_ids:
        print(f" {block_id:8}", end="")
    print()

    # Matrix
    for i, block_id1 in enumerate(block_ids):
        print(f"{block_id1:8} ", end="")

        text1 = f"{sample_texts[block_id1]['title']} {sample_texts[block_id1]['content']}"

        for j, block_id2 in enumerate(block_ids):
            if i == j:
                print("  1.0000", end="")
            else:
                text2 = f"{sample_texts[block_id2]['title']} {sample_texts[block_id2]['content']}"
                similarity = nlp_service.calculate_similarity(text1, text2)
                print(f"  {similarity:.4f}", end="")
        print()

    # 6. Clustering by Similarity
    print("\n" + "=" * 70)
    print("6. CONTENT CLUSTERING")
    print("=" * 70)

    # Group blocks by similarity threshold
    threshold = 0.7
    print(f"\n🔗 Finding clusters (threshold: {threshold}):\n")

    clusters = []
    processed = set()

    for block_id1 in sample_texts.keys():
        if block_id1 in processed:
            continue

        cluster = [block_id1]
        text1 = f"{sample_texts[block_id1]['title']} {sample_texts[block_id1]['content']}"

        for block_id2 in sample_texts.keys():
            if block_id1 == block_id2 or block_id2 in processed:
                continue

            text2 = f"{sample_texts[block_id2]['title']} {sample_texts[block_id2]['content']}"
            similarity = nlp_service.calculate_similarity(text1, text2)

            if similarity >= threshold:
                cluster.append(block_id2)
                processed.add(block_id2)

        processed.add(block_id1)
        clusters.append(cluster)

    for i, cluster in enumerate(clusters, 1):
        print(f"  Cluster {i}:")
        for block_id in cluster:
            print(f"    • {sample_texts[block_id]['title']}")
        print()

    # Shutdown
    await block_service.shutdown()
    await nlp_service.shutdown()

    print("=" * 70)
    print("  Example Complete!")
    print("=" * 70)
    print("\n✅ All semantic search features demonstrated successfully!")
    print("\n💡 Key Takeaways:")
    print("  • Embeddings capture semantic meaning (384 dimensions)")
    print("  • Cosine similarity measures how related texts are (0-1)")
    print("  • Batch processing is more efficient for multiple comparisons")
    print("  • Semantic search works even with different wording")
    print("\n📚 Next steps:")
    print("  • Read ML guide: docs/ml_usage_guide.md")
    print("  • Try API endpoints: http://localhost:8000/docs")
    print("  • Run tests: pytest tests/integration/test_ml_api.py")


if __name__ == "__main__":
    asyncio.run(main())
