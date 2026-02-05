#!/usr/bin/env python3
"""
Setup NLP Models
Downloads and installs required NLP models for the Dynamic Content Blocks System
"""

import subprocess
import sys
import os


def print_step(step: str, message: str):
    """Print formatted step message"""
    print(f"\n{'='*70}")
    print(f"{step}: {message}")
    print('='*70)


def run_command(cmd: list, description: str):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} - Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} - Unexpected error!")
        print(f"Error: {str(e)}")
        return False


def main():
    """Main setup function"""
    print_step("STEP 1", "NLP Models Setup")
    print("This script will download and install:")
    print("  1. spaCy German model (de_core_news_lg) - ~500MB")
    print("  2. Sentence Transformers model (paraphrase-multilingual-MiniLM-L12-v2)")
    print("\nNote: This may take several minutes depending on your internet connection.")

    # Confirm
    response = input("\nDo you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        sys.exit(0)

    # Check Python version
    print_step("STEP 2", "Checking Python version")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

    # Download spaCy model
    print_step("STEP 3", "Downloading spaCy German model")
    print("Model: de_core_news_lg (~500MB)")

    # Try different spaCy models (fallback strategy)
    spacy_models = [
        ("de_core_news_lg", "Large model with word vectors (recommended)"),
        ("de_core_news_md", "Medium model (fallback)"),
        ("de_core_news_sm", "Small model (minimal fallback)")
    ]

    spacy_installed = False
    for model_name, description in spacy_models:
        print(f"\n📦 Trying to install: {model_name}")
        print(f"   {description}")

        if run_command(
            [sys.executable, "-m", "spacy", "download", model_name],
            f"Installing {model_name}"
        ):
            spacy_installed = True
            print(f"\n✅ Successfully installed: {model_name}")
            break
        else:
            print(f"\n⚠️  Failed to install {model_name}, trying next option...")

    if not spacy_installed:
        print("\n❌ Failed to install any spaCy model!")
        print("Please check your internet connection and try again.")
        sys.exit(1)

    # Test spaCy installation
    print_step("STEP 4", "Testing spaCy installation")
    try:
        import spacy
        nlp = spacy.load(model_name)
        doc = nlp("Dies ist ein Test.")
        print(f"✅ spaCy model loaded successfully!")
        print(f"   Tokenized: {[token.text for token in doc]}")
    except Exception as e:
        print(f"❌ Failed to load spaCy model!")
        print(f"Error: {str(e)}")
        sys.exit(1)

    # Download sentence-transformers model
    print_step("STEP 5", "Downloading Sentence Transformers model")
    print("Model: paraphrase-multilingual-MiniLM-L12-v2")
    print("This will be downloaded automatically on first use.")

    try:
        from sentence_transformers import SentenceTransformer
        print("\n🔄 Loading model (first time will download ~120MB)...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Model loaded successfully!")

        # Test embedding generation
        test_text = "Dies ist ein Test für Embeddings."
        embedding = model.encode(test_text)
        print(f"✅ Generated embedding: {len(embedding)} dimensions")

    except Exception as e:
        print(f"❌ Failed to load Sentence Transformers model!")
        print(f"Error: {str(e)}")
        sys.exit(1)

    # Update .env file
    print_step("STEP 6", "Updating .env configuration")
    env_file = ".env"
    env_example = ".env.example"

    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print(f"📋 Creating {env_file} from {env_example}")
            with open(env_example, 'r') as src:
                with open(env_file, 'w') as dst:
                    dst.write(src.read())
            print(f"✅ Created {env_file}")
        else:
            print(f"⚠️  {env_example} not found, creating basic {env_file}")
            with open(env_file, 'w') as f:
                f.write(f"SPACY_MODEL={model_name}\n")
                f.write("SENTENCE_TRANSFORMER_MODEL=paraphrase-multilingual-MiniLM-L12-v2\n")
            print(f"✅ Created {env_file}")
    else:
        print(f"✅ {env_file} already exists")

    # Check if model is correctly configured
    with open(env_file, 'r') as f:
        env_content = f.read()
        if f"SPACY_MODEL={model_name}" in env_content:
            print(f"✅ SPACY_MODEL already configured: {model_name}")
        else:
            print(f"⚠️  Updating SPACY_MODEL to: {model_name}")
            # Update or add the line
            lines = env_content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('SPACY_MODEL='):
                    lines[i] = f"SPACY_MODEL={model_name}"
                    updated = True
                    break
            if not updated:
                lines.append(f"SPACY_MODEL={model_name}")

            with open(env_file, 'w') as f:
                f.write('\n'.join(lines))
            print(f"✅ Updated {env_file}")

    # Success message
    print_step("SETUP COMPLETE", "All NLP models installed successfully!")
    print("\n🎉 Your NLP environment is ready!")
    print("\nInstalled models:")
    print(f"  ✅ spaCy: {model_name}")
    print(f"  ✅ Sentence Transformers: paraphrase-multilingual-MiniLM-L12-v2")
    print("\nYou can now:")
    print("  1. Start the API server: uvicorn app.main:app --reload")
    print("  2. Test ML endpoints: curl http://localhost:8000/api/ml/status")
    print("  3. Run quickstart: python scripts/quickstart.py")
    print("\nDocumentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
