#!/usr/bin/env python3
"""
Demo ML Features
Demonstrates AI/ML capabilities of the Dynamic Content Blocks System
"""

import asyncio
import httpx
import json
from typing import Dict, Any


API_BASE = "http://localhost:8000"


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def print_result(result: Dict[str, Any], title: str = "Result"):
    """Pretty print JSON result"""
    print(f"\n{title}:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


async def check_health():
    """Check API health"""
    print_section("1. Checking API Health")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/health")
        data = response.json()

        print("\n📊 Service Status:")
        for service, status in data.get("services", {}).items():
            icon = "✅" if status.get("status") == "up" else "❌"
            latency = status.get("latency_ms", "N/A")
            print(f"  {icon} {service}: {status.get('status')} ({latency}ms)")

        return response.status_code == 200


async def check_nlp_status():
    """Check NLP service status"""
    print_section("2. Checking NLP Service Status")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/ml/status")
        data = response.json()
        print_result(data, "NLP Service Status")

        if data.get("status") != "ready":
            print("\n⚠️  NLP service is not ready!")
            print("Please run: python scripts/setup_nlp_models.py")
            return False
        return True


async def demo_text_analysis():
    """Demo full text analysis"""
    print_section("3. Text Analysis (Full NLP Pipeline)")

    text = """
    Nach § 5 SGB IX haben Menschen mit Behinderung Anspruch auf Leistungen
    zur Teilhabe am Arbeitsleben. Diese Leistungen umfassen medizinische
    Rehabilitation, berufliche Rehabilitation und soziale Teilhabe.
    """

    payload = {"text": text.strip()}

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n📝 Analyzing text: {text[:100]}...")
        response = await client.post(
            f"{API_BASE}/api/ml/analyze",
            json=payload
        )
        data = response.json()

        print("\n📊 Statistics:")
        for key, value in data.get("stats", {}).items():
            print(f"  • {key}: {value}")

        print("\n🔑 Keywords:")
        for keyword in data.get("keywords", [])[:10]:
            print(f"  • {keyword}")

        print("\n🏷️  Entities:")
        for entity in data.get("entities", []):
            print(f"  • {entity['text']} ({entity['label']})")

        print("\n⚖️  Legal References:")
        for ref in data.get("legal_references", []):
            print(f"  • {ref}")

        print(f"\n🧠 Embedding: {len(data.get('embedding', []))} dimensions")


async def demo_classification():
    """Demo auto-classification"""
    print_section("4. Auto-Classification")

    text = """
    Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe.
    Die Leistungen werden durch die Rehabilitationsträger erbracht.
    """
    title = "§ 5 Leistungen zur Teilhabe"

    payload = {
        "text": text,
        "title": title
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n📝 Classifying: '{title}'")
        response = await client.post(
            f"{API_BASE}/api/ml/classify",
            json=payload
        )
        data = response.json()

        print(f"\n🏷️  Type: {data.get('type')}")
        print(f"📁 Category: {data.get('category')}")
        print(f"📊 Confidence: {data.get('confidence'):.2%}")

        if data.get('entities'):
            print("\n🏷️  Entities found:")
            for entity in data['entities'][:5]:
                print(f"  • {entity['text']} ({entity['label']})")


async def demo_summarization():
    """Demo text summarization"""
    print_section("5. Text Summarization")

    long_text = """
    Menschen mit Behinderung haben Anspruch auf Leistungen zur Teilhabe am
    Arbeitsleben. Diese Leistungen sollen ihre Teilhabe am Arbeitsleben
    entsprechend ihren Leistungen und unter Berücksichtigung ihrer berechtigten
    Wünsche dauerhaft sichern. Die Leistungen umfassen insbesondere Hilfen zur
    Erhaltung oder Erlangung eines Arbeitsplatzes. Zu den Leistungen gehören
    auch Leistungen zur medizinischen Rehabilitation. Die Leistungen werden
    durch die zuständigen Rehabilitationsträger erbracht. Die
    Rehabilitationsträger sind verpflichtet, die Leistungen rechtzeitig zu
    erbringen. Eine rechtzeitige Leistungserbringung liegt vor, wenn der
    Rehabilitationsträger innerhalb der gesetzlichen Fristen entscheidet.
    """

    payload = {
        "text": long_text.strip(),
        "max_sentences": 3,
        "method": "frequency"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n📄 Original text: {len(long_text)} characters")
        response = await client.post(
            f"{API_BASE}/api/ml/summarize",
            json=payload
        )
        data = response.json()

        print(f"\n📝 Summary ({data.get('compression_ratio', 0):.0%} of original):")
        print(f"{data.get('summary')}")

        print("\n📌 Key Points:")
        for i, point in enumerate(data.get('summary_points', [])[:3], 1):
            print(f"  {i}. {point[:100]}...")


async def demo_semantic_search():
    """Demo semantic search"""
    print_section("6. Semantic Search")

    query = "Wie bekomme ich Unterstützung für die Arbeit?"

    payload = {
        "query": query,
        "limit": 3,
        "min_score": 0.3
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n🔍 Searching: '{query}'")
        print("(Using semantic embeddings, not keyword matching)")

        response = await client.post(
            f"{API_BASE}/api/search/semantic",
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

            if results:
                print(f"\n✅ Found {len(results)} semantically similar blocks:")
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. {result.get('title')} (similarity: {result.get('similarity', 0):.2%})")
                    print(f"     {result.get('content')[:150]}...")
            else:
                print("\n⚠️  No results found. Make sure blocks are indexed with embeddings.")
                print("Run: curl -X POST http://localhost:8000/api/search/reindex")
        else:
            print(f"\n⚠️  Search failed: {response.status_code}")
            print("Make sure you have indexed blocks with embeddings.")


async def demo_similarity():
    """Demo text similarity"""
    print_section("7. Text Similarity")

    text1 = "Persönliches Budget für Menschen mit Behinderung"
    text2 = "Individuelles Budget zur Teilhabe"

    payload = {
        "text1": text1,
        "text2": text2
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n📝 Text 1: '{text1}'")
        print(f"📝 Text 2: '{text2}'")

        response = await client.post(
            f"{API_BASE}/api/ml/similarity",
            json=payload
        )
        data = response.json()

        similarity = data.get('similarity', 0)
        print(f"\n🎯 Similarity: {similarity:.2%}")

        if similarity > 0.8:
            print("   → Very similar (semantically equivalent)")
        elif similarity > 0.6:
            print("   → Similar (related concepts)")
        elif similarity > 0.4:
            print("   → Somewhat similar (some overlap)")
        else:
            print("   → Not very similar")


async def demo_ner():
    """Demo Named Entity Recognition"""
    print_section("8. Named Entity Recognition (NER)")

    text = """
    Nach § 5 SGB IX haben Menschen mit Behinderung in Berlin Anspruch auf
    Leistungen. Die Berliner Senatsverwaltung ist zuständig für die Umsetzung.
    """

    payload = {"text": text.strip()}

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n📝 Extracting entities from:")
        print(f"{text}")

        response = await client.post(
            f"{API_BASE}/api/ml/ner",
            json=payload
        )
        data = response.json()

        print("\n🏷️  Entities:")
        for entity in data.get('entities', []):
            print(f"  • {entity['text']} ({entity['label']}) at position {entity['start']}-{entity['end']}")

        print("\n⚖️  Legal References:")
        for ref in data.get('legal_references', []):
            print(f"  • {ref}")


async def main():
    """Main demo function"""
    print("\n" + "="*70)
    print("  🧠 Dynamic Content Blocks - AI/ML Features Demo")
    print("="*70)
    print("\nThis script demonstrates the AI/ML capabilities:")
    print("  • Text analysis with NLP")
    print("  • Auto-classification")
    print("  • Summarization")
    print("  • Semantic search")
    print("  • Text similarity")
    print("  • Named Entity Recognition")

    try:
        # Check health
        if not await check_health():
            print("\n❌ API is not healthy. Please start the server:")
            print("   uvicorn app.main:app --reload")
            return

        # Check NLP service
        if not await check_nlp_status():
            return

        # Run demos
        await demo_text_analysis()
        await demo_classification()
        await demo_summarization()
        await demo_semantic_search()
        await demo_similarity()
        await demo_ner()

        # Success
        print_section("Demo Complete!")
        print("\n🎉 All ML features demonstrated successfully!")
        print("\n📚 For more information:")
        print("  • API Documentation: http://localhost:8000/docs")
        print("  • README: ./README.md")
        print("  • Full Methodology: ./dynamic_content_blocks_methodology.md")

    except httpx.ConnectError:
        print("\n❌ Cannot connect to API!")
        print("Please start the server: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
