"""
NLP Service для обработки текстов и генерации embeddings
Использует spaCy для немецкого языка и sentence-transformers для семантических векторов
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np


class NLPService:
    """Сервис для NLP обработки текстов"""

    def __init__(self):
        """Initialize NLP Service"""
        self.spacy_model_name = os.getenv("SPACY_MODEL", "de_core_news_lg")
        self.transformer_model_name = os.getenv(
            "SENTENCE_TRANSFORMER_MODEL",
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        self.nlp = None
        self.embedder = None
        self.initialized = False

    async def initialize(self):
        """
        Инициализация NLP моделей

        Загружает:
        - spaCy модель для немецкого языка (токенизация, POS, NER)
        - Sentence-Transformer модель для embeddings
        """
        try:
            # Загрузить spaCy модель
            print(f"🔄 Loading spaCy model: {self.spacy_model_name}")
            try:
                self.nlp = spacy.load(self.spacy_model_name)
                print(f"✅ spaCy model loaded: {self.spacy_model_name}")
            except OSError:
                print(f"⚠️  spaCy model {self.spacy_model_name} not found")
                print(f"💡 Install with: python -m spacy download {self.spacy_model_name}")
                # Fallback к базовой модели
                try:
                    self.nlp = spacy.load("de_core_news_sm")
                    print("✅ Fallback to de_core_news_sm")
                except:
                    print("⚠️  No German spaCy model available")

            # Загрузить Sentence-Transformer модель
            print(f"🔄 Loading Sentence-Transformer: {self.transformer_model_name}")
            self.embedder = SentenceTransformer(self.transformer_model_name)
            print(f"✅ Sentence-Transformer loaded")

            self.initialized = True
            print("✅ NLP Service initialized")

        except Exception as e:
            print(f"⚠️  NLP Service initialization failed: {e}")
            self.initialized = False

    def is_ready(self) -> bool:
        """Проверить готовность сервиса"""
        return self.initialized and self.nlp is not None and self.embedder is not None

    # === Tokenization & Preprocessing ===

    def tokenize(self, text: str) -> List[str]:
        """
        Токенизация текста

        :param text: Исходный текст
        :return: Список токенов
        """
        if not self.is_ready():
            # Fallback на простую токенизацию
            return text.split()

        doc = self.nlp(text)
        return [token.text for token in doc]

    def lemmatize(self, text: str) -> List[str]:
        """
        Лемматизация текста

        :param text: Исходный текст
        :return: Список лемм
        """
        if not self.is_ready():
            return text.split()

        doc = self.nlp(text)
        return [token.lemma_ for token in doc]

    def remove_stopwords(self, text: str) -> str:
        """
        Удалить стоп-слова

        :param text: Исходный текст
        :return: Текст без стоп-слов
        """
        if not self.is_ready():
            return text

        doc = self.nlp(text)
        filtered = [token.text for token in doc if not token.is_stop]
        return " ".join(filtered)

    # === Named Entity Recognition ===

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Извлечь именованные сущности

        :param text: Текст для анализа
        :return: Список сущностей с типами
        """
        if not self.is_ready():
            return []

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })

        return entities

    def extract_legal_references(self, text: str) -> List[str]:
        """
        Извлечь юридические ссылки (§, Art., etc.)

        :param text: Текст для анализа
        :return: Список найденных ссылок
        """
        import re

        # Паттерны для юридических ссылок
        patterns = [
            r'§\s*\d+[a-z]?',  # § 5, § 29a
            r'Art\.\s*\d+',     # Art. 12
            r'Abs\.\s*\d+',     # Abs. 1
            r'Satz\s*\d+',      # Satz 2
        ]

        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)

        return list(set(references))  # Уникальные

    # === Embeddings ===

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Генерировать embedding для текста

        :param text: Текст для векторизации
        :return: Вектор embeddings или None
        """
        if not self.is_ready():
            return None

        try:
            embedding = self.embedder.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠️  Embedding generation failed: {e}")
            return None

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Генерировать embeddings для нескольких текстов

        Более эффективно чем по одному
        :param texts: Список текстов
        :return: Список векторов
        """
        if not self.is_ready():
            return []

        try:
            embeddings = self.embedder.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"⚠️  Batch embedding failed: {e}")
            return []

    # === Similarity ===

    def calculate_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Вычислить семантическое сходство между текстами

        :param text1: Первый текст
        :param text2: Второй текст
        :return: Косинусное сходство (0-1)
        """
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)

        if emb1 is None or emb2 is None:
            return 0.0

        # Косинусное сходство
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

    def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Найти наиболее похожие тексты

        :param query: Запрос
        :param candidates: Список кандидатов
        :param top_k: Количество результатов
        :return: Список (индекс, score)
        """
        if not self.is_ready() or not candidates:
            return []

        query_emb = self.generate_embedding(query)
        if query_emb is None:
            return []

        candidate_embs = self.generate_embeddings_batch(candidates)
        if not candidate_embs:
            return []

        # Вычислить косинусное сходство для всех
        similarities = []
        query_norm = np.linalg.norm(query_emb)

        for idx, cand_emb in enumerate(candidate_embs):
            cand_norm = np.linalg.norm(cand_emb)
            if query_norm == 0 or cand_norm == 0:
                similarity = 0.0
            else:
                similarity = float(
                    np.dot(query_emb, cand_emb) / (query_norm * cand_norm)
                )
            similarities.append((idx, similarity))

        # Сортировать по убыванию сходства
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    # === Text Analysis ===

    def get_pos_tags(self, text: str) -> List[Dict[str, str]]:
        """
        Получить POS теги (части речи)

        :param text: Текст для анализа
        :return: Список {token, pos, tag}
        """
        if not self.is_ready():
            return []

        doc = self.nlp(text)
        return [
            {
                "token": token.text,
                "pos": token.pos_,
                "tag": token.tag_
            }
            for token in doc
        ]

    def extract_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[str]:
        """
        Извлечь ключевые слова

        Использует частоту и POS теги
        :param text: Текст для анализа
        :param top_n: Количество ключевых слов
        :return: Список ключевых слов
        """
        if not self.is_ready():
            return []

        doc = self.nlp(text)

        # Фильтровать только существительные и прилагательные
        keywords = [
            token.lemma_.lower()
            for token in doc
            if token.pos_ in ["NOUN", "PROPN", "ADJ"]
            and not token.is_stop
            and len(token.text) > 2
        ]

        # Подсчитать частоты
        from collections import Counter
        freq = Counter(keywords)

        # Вернуть top_n
        return [word for word, count in freq.most_common(top_n)]

    # === Classification ===

    def classify_block_type(self, text: str, title: str = "") -> str:
        """
        Автоматическая классификация типа блока

        Использует ключевые слова и структуру для определения типа
        :param text: Текст блока
        :param title: Заголовок блока
        :return: Предполагаемый тип блока
        """
        combined_text = f"{title} {text}".lower()

        # Паттерны для разных типов блоков
        type_patterns = {
            "paragraph": [
                "§", "absatz", "satz", "nummer",
                "vorschrift", "bestimmung", "regelung"
            ],
            "definition": [
                "definition", "bedeutung", "gilt als", "versteht man",
                "bezeichnet", "umfasst", "ist", "sind"
            ],
            "procedure": [
                "verfahren", "antrag", "prüfung", "entscheidung",
                "feststellung", "genehmigung", "ablauf", "schritt"
            ],
            "requirement": [
                "voraussetzung", "erforderlich", "bedingung", "muss",
                "erfüllen", "notwendig", "erfordert"
            ],
            "right": [
                "anspruch", "recht", "berechtigt", "können", "darf",
                "zusteht", "beanspruchen"
            ],
            "obligation": [
                "pflicht", "verpflichtung", "muss", "hat zu", "ist verpflichtet",
                "obliegt", "aufgabe"
            ],
            "sanction": [
                "strafe", "busse", "sanktion", "ordnungswidrigkeit",
                "ahndung", "verstoss"
            ]
        }

        # Подсчитать совпадения для каждого типа
        scores = {}
        for block_type, patterns in type_patterns.items():
            score = sum(1 for pattern in patterns if pattern in combined_text)
            if score > 0:
                scores[block_type] = score

        # Вернуть тип с наибольшим количеством совпадений
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        # По умолчанию
        return "paragraph"

    def classify_category(self, text: str, entities: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Классификация категории блока

        Использует ключевые слова и NER для определения категории
        :param text: Текст блока
        :param entities: Опционально уже извлечённые сущности
        :return: Категория или None
        """
        text_lower = text.lower()

        # Категории с ключевыми словами
        category_keywords = {
            "employment": [
                "arbeit", "beschäftigung", "arbeitsplatz", "beruf",
                "erwerbstätigkeit", "job"
            ],
            "health": [
                "gesundheit", "medizin", "behandlung", "therapie",
                "pflege", "rehabilitation", "krankheit"
            ],
            "education": [
                "bildung", "ausbildung", "schule", "studium",
                "qualifizierung", "weiterbildung", "lernen"
            ],
            "social_security": [
                "sozial", "versicherung", "rente", "leistung",
                "unterstützung", "hilfe", "förderung"
            ],
            "participation": [
                "teilhabe", "integration", "inklusion", "zugang",
                "barrierefreiheit", "selbstbestimmung"
            ],
            "administration": [
                "verwaltung", "behörde", "antrag", "verfahren",
                "zuständigkeit", "genehmigung"
            ]
        }

        # Подсчитать совпадения
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score

        # Вернуть категорию с наибольшим счётом
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return None

    def classify_block(self, text: str, title: str = "") -> Dict[str, Any]:
        """
        Полная классификация блока

        Определяет тип и категорию блока
        :param text: Текст блока
        :param title: Заголовок блока
        :return: Словарь с классификацией
        """
        # Извлечь сущности для анализа
        entities = self.extract_entities(text)

        return {
            "type": self.classify_block_type(text, title),
            "category": self.classify_category(text, entities),
            "entities": entities,
            "confidence": 0.7  # Базовая уверенность для rule-based системы
        }

    # === Summarization ===

    def summarize_text(
        self,
        text: str,
        max_sentences: int = 3,
        method: str = "frequency"
    ) -> str:
        """
        Extractive summarization (резюмирование)

        Выбирает наиболее важные предложения из текста
        :param text: Исходный текст
        :param max_sentences: Максимальное количество предложений в резюме
        :param method: Метод выбора ('frequency' или 'position')
        :return: Резюмированный текст
        """
        if not self.is_ready():
            # Fallback: просто вернуть первые предложения
            sentences = text.split('. ')
            return '. '.join(sentences[:max_sentences]) + '.'

        doc = self.nlp(text)
        sentences = list(doc.sents)

        if len(sentences) <= max_sentences:
            return text

        if method == "position":
            # Простой метод: первые N предложений
            selected = sentences[:max_sentences]
        else:
            # Frequency-based: выбрать предложения с наиболее важными словами
            # 1. Подсчитать частоту значимых слов
            word_freq = {}
            for token in doc:
                if (not token.is_stop and not token.is_punct and
                    token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]):
                    lemma = token.lemma_.lower()
                    word_freq[lemma] = word_freq.get(lemma, 0) + 1

            # 2. Оценить важность каждого предложения
            sentence_scores = []
            for i, sent in enumerate(sentences):
                score = 0
                for token in sent:
                    lemma = token.lemma_.lower()
                    score += word_freq.get(lemma, 0)

                # Бонус для первых предложений
                if i < 2:
                    score *= 1.5

                sentence_scores.append((score, i, sent))

            # 3. Выбрать top N предложений
            sentence_scores.sort(reverse=True, key=lambda x: x[0])
            selected_with_idx = sentence_scores[:max_sentences]

            # 4. Отсортировать по исходному порядку
            selected_with_idx.sort(key=lambda x: x[1])
            selected = [sent for _, _, sent in selected_with_idx]

        # Объединить предложения
        summary = ' '.join(sent.text.strip() for sent in selected)
        return summary

    def generate_summary_points(self, text: str, max_points: int = 5) -> List[str]:
        """
        Генерация списка ключевых пунктов

        :param text: Исходный текст
        :param max_points: Максимальное количество пунктов
        :return: Список ключевых пунктов
        """
        if not self.is_ready():
            # Fallback: разбить на предложения
            sentences = text.split('. ')
            return sentences[:max_points]

        doc = self.nlp(text)
        sentences = list(doc.sents)

        # Извлечь короткие информативные предложения
        points = []
        for sent in sentences:
            sent_text = sent.text.strip()

            # Фильтр: не слишком длинные и не слишком короткие
            if 10 < len(sent_text) < 200:
                points.append(sent_text)

            if len(points) >= max_points:
                break

        return points

    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """
        Получить статистику текста

        :param text: Текст для анализа
        :return: Словарь со статистикой
        """
        if not self.is_ready():
            words = text.split()
            return {
                "char_count": len(text),
                "word_count": len(words),
                "sentence_count": text.count('.') + text.count('!') + text.count('?'),
                "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0
            }

        doc = self.nlp(text)

        return {
            "char_count": len(text),
            "word_count": len([t for t in doc if not t.is_punct]),
            "sentence_count": len(list(doc.sents)),
            "token_count": len(doc),
            "avg_word_length": sum(len(t.text) for t in doc) / len(doc) if len(doc) > 0 else 0,
            "unique_words": len(set(t.lemma_.lower() for t in doc if not t.is_stop)),
            "entities_count": len(doc.ents)
        }

    async def shutdown(self):
        """Освободить ресурсы"""
        self.nlp = None
        self.embedder = None
        self.initialized = False


# Singleton instance
nlp_service = NLPService()
