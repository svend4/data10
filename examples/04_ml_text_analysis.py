#!/usr/bin/env python3
"""
Example 4: ML Text Analysis
Demonstrates AI/ML text analysis features
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.nlp_service import nlp_service


async def main():
    """Main example function"""
    print("=" * 70)
    print("  Example 4: ML Text Analysis")
    print("=" * 70)

    # Initialize NLP service
    print("\n📦 Initializing NLP service...")
    await nlp_service.initialize()

    if not nlp_service.is_ready():
        print("\n❌ NLP service not ready!")
        print("Please run: python scripts/setup_nlp_models.py")
        return

    print("✅ NLP service ready!")

    # Sample German legal text
    text = """
    Nach § 5 SGB IX haben Menschen mit Behinderung Anspruch auf Leistungen
    zur Teilhabe am Arbeitsleben. Diese Leistungen umfassen medizinische
    Rehabilitation, berufliche Rehabilitation und soziale Teilhabe. Die
    Leistungen werden durch die zuständigen Rehabilitationsträger erbracht.
    Menschen mit Behinderung in Berlin können sich an die Berliner
    Senatsverwaltung wenden.
    """

    # 1. Text Statistics
    print("\n" + "=" * 70)
    print("1. TEXT STATISTICS")
    print("=" * 70)

    stats = nlp_service.get_text_stats(text)
    print(f"\n📊 Statistics:")
    print(f"  • Total words: {stats['total_words']}")
    print(f"  • Total sentences: {stats['total_sentences']}")
    print(f"  • Unique words: {stats['unique_words']}")
    print(f"  • Average word length: {stats['avg_word_length']:.1f} characters")
    print(f"  • Average sentence length: {stats['avg_sentence_length']:.1f} words")

    # 2. Keyword Extraction
    print("\n" + "=" * 70)
    print("2. KEYWORD EXTRACTION")
    print("=" * 70)

    keywords = nlp_service.extract_keywords(text, top_n=10)
    print(f"\n🔑 Top keywords:")
    for i, keyword in enumerate(keywords, 1):
        print(f"  {i}. {keyword}")

    # 3. Named Entity Recognition
    print("\n" + "=" * 70)
    print("3. NAMED ENTITY RECOGNITION (NER)")
    print("=" * 70)

    entities = nlp_service.extract_entities(text)
    print(f"\n🏷️  Entities found:")
    for entity in entities:
        print(f"  • {entity['text']} ({entity['label']})")
        print(f"    Position: {entity['start']}-{entity['end']}")

    # 4. Legal References
    print("\n" + "=" * 70)
    print("4. LEGAL REFERENCE EXTRACTION")
    print("=" * 70)

    legal_refs = nlp_service.extract_legal_references(text)
    print(f"\n⚖️  Legal references:")
    for ref in legal_refs:
        print(f"  • {ref}")

    # 5. Text Tokenization
    print("\n" + "=" * 70)
    print("5. TOKENIZATION")
    print("=" * 70)

    tokens = nlp_service.tokenize(text)
    print(f"\n📝 Tokens (first 20):")
    print(f"  {' | '.join(tokens[:20])}")

    # 6. Lemmatization
    print("\n" + "=" * 70)
    print("6. LEMMATIZATION")
    print("=" * 70)

    lemmas = nlp_service.lemmatize(text)
    print(f"\n🔤 Lemmas (first 20):")
    print(f"  {' | '.join(lemmas[:20])}")

    # 7. POS Tagging
    print("\n" + "=" * 70)
    print("7. PART-OF-SPEECH TAGGING")
    print("=" * 70)

    pos_tags = nlp_service.get_pos_tags(text)
    print(f"\n🏷️  POS tags (first 15):")
    for token, pos in pos_tags[:15]:
        print(f"  {token:20} → {pos}")

    # 8. Semantic Embedding
    print("\n" + "=" * 70)
    print("8. SEMANTIC EMBEDDING GENERATION")
    print("=" * 70)

    embedding = nlp_service.generate_embedding(text)
    print(f"\n🧠 Embedding:")
    print(f"  • Dimension: {len(embedding)}")
    print(f"  • First 10 values: {embedding[:10]}")
    print(f"  • Min value: {min(embedding):.4f}")
    print(f"  • Max value: {max(embedding):.4f}")

    # 9. Text Classification
    print("\n" + "=" * 70)
    print("9. AUTOMATIC CLASSIFICATION")
    print("=" * 70)

    title = "§ 5 Leistungen zur Teilhabe"
    classification = nlp_service.classify_block(text, title)

    print(f"\n📁 Classification:")
    print(f"  • Type: {classification['type']}")
    print(f"  • Category: {classification['category']}")
    print(f"  • Confidence: {classification['confidence']:.2%}")
    print(f"  • Entities found: {len(classification['entities'])}")

    # 10. Text Summarization
    print("\n" + "=" * 70)
    print("10. TEXT SUMMARIZATION")
    print("=" * 70)

    summary = nlp_service.summarize_text(text, max_sentences=2, method="frequency")
    print(f"\n📝 Summary (2 sentences):")
    print(f"  {summary}")

    compression_ratio = len(summary) / len(text)
    print(f"\n  Compression ratio: {compression_ratio:.2%}")

    # Summary points
    points = nlp_service.generate_summary_points(text, max_points=3)
    print(f"\n📌 Key points:")
    for i, point in enumerate(points, 1):
        print(f"  {i}. {point[:100]}...")

    # Shutdown
    await nlp_service.shutdown()

    print("\n" + "=" * 70)
    print("  Example Complete!")
    print("=" * 70)
    print("\n✅ All ML text analysis features demonstrated successfully!")
    print("\n📚 Next steps:")
    print("  • Try example 05: python examples/05_ml_semantic_search.py")
    print("  • Read ML guide: docs/ml_usage_guide.md")
    print("  • View API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
