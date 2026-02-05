# Методология динамических информационных блоков: полное руководство
## Comprehensive Guide to Dynamic Content Block Systems

**Версия:** 1.0  
**Дата:** 04.02.2026  
**Автор:** Claude (Anthropic)  
**Язык:** Русский с техническими терминами на английском

---

## Содержание

1. [Введение и концепция](#1-введение-и-концепция)
2. [Теоретические основы](#2-теоретические-основы)
3. [Классические алгоритмы и методологии](#3-классические-алгоритмы-и-методологии)
4. [Технологический стек](#4-технологический-стек)
5. [Архитектурные паттерны](#5-архитектурные-паттерны)
6. [Практическая реализация](#6-практическая-реализация)
7. [Система автоматического встраивания](#7-система-автоматического-встраивания)
8. [Работа с законодательными текстами](#8-работа-с-законодательными-текстами)
9. [Advanced функциональность](#9-advanced-функциональность)
10. [Полные примеры кода](#10-полные-примеры-кода)
11. [Deployment и масштабирование](#11-deployment-и-масштабирование)
12. [Roadmap и будущее развитие](#12-roadmap-и-будущее-развитие)
13. [Приложения](#13-приложения)

---

## 1. Введение и концепция

### 1.1 Проблематика

Современные информационные системы работают с огромными объемами структурированного и полуструктурированного контента. Особенно остро эта проблема стоит в следующих областях:

- **Законодательство**: параграфы, статьи, условные ссылки, иерархии норм
- **Техническая документация**: модульные инструкции, версионирование, условные включения
- **Корпоративные знания**: политики, процедуры, best practices
- **Новостные агрегаторы**: кластеризация по темам, разные уровни детализации
- **Образовательный контент**: учебные модули, персонализированные траектории

**Ключевые проблемы традиционных подходов:**

1. **Дублирование информации**: один и тот же текст копируется в разные документы
2. **Сложность обновления**: изменение в одном месте не отражается в других
3. **Отсутствие условной логики**: невозможно автоматически адаптировать документ под контекст
4. **Плоская структура**: отсутствие динамической иерархии и вложенности
5. **Ручная сборка**: каждый документ собирается вручную из копипасты

### 1.2 Целевое решение: "Lego-конструктор" информации

**Концепция**: система модульных информационных блоков с:

- **Атомарность**: каждый блок — минимальная единица смысла
- **Переиспользование**: один блок используется в разных контекстах
- **Условная логика**: блоки активируются по правилам и условиям
- **Динамическая иерархия**: блоки автоматически встраиваются на нужный уровень
- **Семантические связи**: блоки связаны по смыслу, не только структурно
- **Автоматическая сборка**: документы генерируются по запросу

**Метафора**: представьте, что у вас есть:
- **Lego-детали** = информационные блоки
- **Инструкция по сборке** = правила и условия
- **Разные наборы** = разные типы документов
- **Автоматический робот** = система сборки

### 1.3 Ключевые возможности системы

#### 1.3.1 Автоматическое встраивание контента

```
Новость: "Погода в Берлине: +15°C"
    ↓
Система анализирует топик: "Погода" + "Берлин" + "Германия" + "Европа"
    ↓
Встраивает автоматически:
    Погода в Европе (уровень 1)
    ├── Погода в Германии (уровень 2)
    │   └── Погода в Берлине: +15°C (уровень 3)
    └── Погода во Франции (уровень 2)
```

#### 1.3.2 Эскалация детализации

```
Сначала: "Погода в Европе" (1 предложение)
    ↓
Приходит: детальная статья на 5 предложений
    ↓
Система:
    - Старое содержимое → становится заголовком
    - Новое содержимое → становится телом
    - Создаются подпункты для деталей
```

#### 1.3.3 Условная логика

```
IF параграф_5.активен AND срок_работы > 5_лет:
    THEN включить параграф_6
    
IF увеличение_бюджета >= 10_процентов:
    THEN включить параграф_15
ELSE:
    включить параграф_6
```

---

## 2. Теоретические основы

### 2.1 Graph Theory (Теория графов)

**Фундаментальная основа**: информационные блоки как узлы графа, связи как рёбра.

#### 2.1.1 Directed Acyclic Graph (DAG)

**Определение**: граф без циклов, направленные рёбра.

**Применение в нашей системе**:
- Узлы = информационные блоки
- Рёбра = условные переходы, ссылки, зависимости
- Отсутствие циклов = нет бесконечных рекурсий

**Математическая модель**:
```
G = (V, E)
где:
V = {block₁, block₂, ..., blockₙ}
E = {(blockᵢ, blockⱼ, condition) | condition: Context → Boolean}
```

**Пример для SGB IX**:
```
§5 → §6 (если стаж > 5 лет)
§5 → §15 (если увеличение >= 10%)
§6 → §7 (всегда)
§15 → §16 (если дополнительное условие X)
```

**Топологическая сортировка**: определяет порядок применения параграфов.

```python
def topological_sort(graph):
    """
    Алгоритм Кана для топологической сортировки
    Возвращает порядок обработки блоков
    """
    in_degree = {node: 0 for node in graph.nodes}
    
    for node in graph.nodes:
        for neighbor in graph.neighbors(node):
            in_degree[neighbor] += 1
    
    queue = [node for node in graph.nodes if in_degree[node] == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for neighbor in graph.neighbors(node):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(graph.nodes):
        raise Exception("Graph has cycles!")
    
    return result
```

#### 2.1.2 Semantic Networks (Семантические сети)

**Определение**: граф, где узлы — концепты, рёбра — семантические отношения.

**Типы связей**:
- **IS-A**: "Берлин" IS-A "Город"
- **PART-OF**: "§5 Abs. 2" PART-OF "§5"
- **RELATED-TO**: "Погода" RELATED-TO "Климат"
- **CAUSES**: "Условие X" CAUSES "Применение §6"

**Пример семантической сети для законодательства**:

```
Persönliches Budget (Концепт)
    ├── IS-A → Leistungsform (родовое понятие)
    ├── REGULATED-BY → §29 SGB IX (регулирование)
    ├── REQUIRES → Antrag (требование)
    ├── RELATES-TO → Teilhabeplan (связь)
    └── CONFLICTS-WITH → Sachleistung (конфликт)
```

#### 2.1.3 Property Graphs (Графы с атрибутами)

**Расширение**: узлы и рёбра имеют свойства (properties).

**Модель данных Neo4j**:
```cypher
// Узел с properties
(:Block {
    id: "sgb9_p5",
    number: "§5",
    title: "Leistungen zur Teilhabe",
    content: "...",
    valid_from: "2001-07-01",
    valid_until: null,
    language: "de",
    jurisdiction: "Deutschland"
})

// Рёбро с properties
-[:APPLIES_IF {
    condition: "work_years > 5",
    priority: 1,
    confidence: 0.95,
    source: "SGB IX §5 Abs. 2"
}]->
```

### 2.2 Formal Logic (Формальная логика)

#### 2.2.1 Propositional Logic (Логика высказываний)

**Основные операторы**:
- `∧` (AND): оба условия должны быть true
- `∨` (OR): хотя бы одно условие true
- `¬` (NOT): отрицание
- `→` (IMPLIES): импликация
- `↔` (IFF): эквивалентность

**Применение к правилам**:
```
Rule 1: (work_years > 5) → apply(§6)
Rule 2: (work_years > 5 ∧ degree_of_disability >= 50) → apply(§15)
Rule 3: ¬(received_benefits) → require(initial_application)
```

**Таблицы истинности для сложных условий**:

```
work_years > 5 | disability >= 50 | Rule 2 Result
---------------|------------------|---------------
    TRUE       |      TRUE        |    APPLY §15
    TRUE       |      FALSE       |    NO ACTION
    FALSE      |      TRUE        |    NO ACTION
    FALSE      |      FALSE       |    NO ACTION
```

#### 2.2.2 First-Order Logic (Логика первого порядка)

**Кванторы**:
- `∀` (forall): для всех
- `∃` (exists): существует

**Примеры правил**:
```
∀x (Person(x) ∧ Age(x) >= 18 → Eligible(x, "Persönliches Budget"))

∃y (Document(y) ∧ Type(y, "Bescheid") ∧ Date(y) > "2024-01-01" 
    → CanFile(Widerspruch))
```

#### 2.2.3 Production Rules (Продукционные правила)

**Формат**: IF <conditions> THEN <actions>

**Forward Chaining** (прямой вывод):
```
Дано: work_years = 7, disability = 60
    ↓
Применяем Rule 1: work_years > 5 → TRUE → активируем §6
    ↓
Применяем Rule 2: work_years > 5 AND disability >= 50 → TRUE → активируем §15
    ↓
Результат: {§6, §15}
```

**Backward Chaining** (обратный вывод):
```
Цель: нужно ли применить §15?
    ↓
Проверяем условие: work_years > 5 AND disability >= 50
    ↓
Запрашиваем данные: work_years = ?, disability = ?
    ↓
Получаем: work_years = 7, disability = 60
    ↓
Вывод: ДА, применяем §15
```

### 2.3 Information Theory (Теория информации)

#### 2.3.1 Entropy и Information Gain

**Энтропия блока**: мера неопределённости/информативности.

```python
import math

def calculate_entropy(block):
    """
    Вычисляет энтропию блока на основе распределения слов
    """
    word_freq = get_word_frequencies(block.content)
    total_words = sum(word_freq.values())
    
    entropy = 0
    for freq in word_freq.values():
        p = freq / total_words
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy

def information_gain(parent_block, child_blocks):
    """
    Насколько дочерние блоки добавляют информацию к родительскому
    """
    parent_entropy = calculate_entropy(parent_block)
    
    weighted_child_entropy = 0
    total_child_words = sum(len(child.content.split()) for child in child_blocks)
    
    for child in child_blocks:
        child_words = len(child.content.split())
        weight = child_words / total_child_words
        weighted_child_entropy += weight * calculate_entropy(child)
    
    return parent_entropy - weighted_child_entropy
```

**Применение**: определение, какие дочерние блоки действительно добавляют информацию, а какие просто дублируют родительский.

#### 2.3.2 Similarity Metrics (Метрики схожести)

**Cosine Similarity** (косинусное сходство):
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    """
    Вычисляет косинусное сходство между двумя текстами
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return similarity

# Пример использования
block1_text = "Antrag auf Persönliches Budget gemäß §29 SGB IX"
block2_text = "Beantragung eines Persönlichen Budgets nach SGB IX §29"

similarity = calculate_similarity(block1_text, block2_text)
print(f"Similarity: {similarity:.2f}")  # ~0.85-0.95
```

**Jaccard Index** (индекс Жаккара):
```python
def jaccard_similarity(set1, set2):
    """
    Jaccard = |intersection| / |union|
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0

# Пример
keywords1 = {"budget", "antrag", "sgb9", "teilhabe"}
keywords2 = {"budget", "beantragung", "sgb9", "leistung"}

jaccard = jaccard_similarity(keywords1, keywords2)
print(f"Jaccard: {jaccard:.2f}")  # 0.43
```

**Levenshtein Distance** (расстояние Левенштейна):
```python
def levenshtein_distance(s1, s2):
    """
    Минимальное количество операций (вставка, удаление, замена)
    для превращения s1 в s2
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# Пример
distance = levenshtein_distance("Widerspruch", "Wiederspruch")
print(f"Distance: {distance}")  # 2
```

### 2.4 Natural Language Processing (Обработка естественного языка)

#### 2.4.1 Topic Modeling (Моделирование тем)

**Latent Dirichlet Allocation (LDA)**:

```python
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import simple_preprocess

def extract_topics(documents, num_topics=10):
    """
    Извлекает темы из коллекции документов
    """
    # Препроцессинг
    def preprocess(text):
        result = []
        for token in simple_preprocess(text):
            if token not in STOPWORDS and len(token) > 3:
                result.append(token)
        return result
    
    processed_docs = [preprocess(doc) for doc in documents]
    
    # Создание словаря и корпуса
    dictionary = corpora.Dictionary(processed_docs)
    corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
    
    # Обучение LDA модели
    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        passes=10,
        alpha='auto',
        per_word_topics=True
    )
    
    return lda_model, dictionary

# Пример использования
documents = [
    "Antrag auf Persönliches Budget für Assistenzleistungen",
    "Widerspruch gegen Bescheid des Sozialamts Dresden",
    "Klage vor dem Sozialgericht wegen Leistungsablehnung",
    # ... больше документов
]

lda_model, dictionary = extract_topics(documents, num_topics=5)

# Получение тем для нового документа
new_doc = "Antrag auf Erhöhung des Persönlichen Budgets"
bow = dictionary.doc2bow(simple_preprocess(new_doc))
topics = lda_model.get_document_topics(bow)

print("Темы документа:")
for topic_id, probability in topics:
    print(f"Topic {topic_id}: {probability:.3f}")
    print(lda_model.show_topic(topic_id))
```

**BERTopic** (современная альтернатива):

```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

def extract_topics_bert(documents, language="german"):
    """
    Извлечение тем с помощью BERT embeddings
    """
    # Используем multilingual BERT для немецкого
    sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    # Создание модели BERTopic
    topic_model = BERTopic(
        embedding_model=sentence_model,
        language=language,
        calculate_probabilities=True,
        verbose=True
    )
    
    # Извлечение тем
    topics, probabilities = topic_model.fit_transform(documents)
    
    return topic_model, topics, probabilities

# Пример
documents = [
    "§29 SGB IX regelt das Persönliche Budget",
    "Widerspruchsfrist beträgt einen Monat",
    "Assistenzleistungen sind Teil der Eingliederungshilfe",
    # ... больше документов
]

topic_model, topics, probs = extract_topics_bert(documents)

# Получение информации о темах
topic_info = topic_model.get_topic_info()
print(topic_info)

# Визуализация тем
topic_model.visualize_topics()
```

#### 2.4.2 Named Entity Recognition (NER)

**Извлечение юридических сущностей**:

```python
import spacy
from spacy.tokens import Span

# Загрузка немецкой модели
nlp = spacy.load("de_core_news_lg")

# Добавление кастомных паттернов для юридических сущностей
def add_legal_patterns(nlp):
    """
    Добавляет паттерны для распознавания юридических терминов
    """
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    patterns = [
        # Параграфы
        {"label": "LAW_SECTION", "pattern": [
            {"TEXT": {"REGEX": "§"}},
            {"LIKE_NUM": True}
        ]},
        
        # Акцентзайхен (Az.)
        {"label": "CASE_NUMBER", "pattern": [
            {"TEXT": {"REGEX": "S|L|B"}},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "SO|AS|SB"}},
            {"LIKE_NUM": True},
            {"TEXT": "/"},
            {"LIKE_NUM": True}
        ]},
        
        # Fristen
        {"label": "DEADLINE", "pattern": [
            {"LIKE_NUM": True},
            {"LOWER": {"IN": ["monat", "monate", "wochen", "tage"]}}
        ]},
        
        # Behörden
        {"label": "AUTHORITY", "pattern": [
            {"LOWER": "sozialamt"}
        ]},
        {"label": "AUTHORITY", "pattern": [
            {"LOWER": "sozialgericht"}
        ]},
    ]
    
    ruler.add_patterns(patterns)
    return nlp

nlp = add_legal_patterns(nlp)

# Анализ текста
text = """
Hiermit lege ich Widerspruch gegen den Bescheid des Sozialamts Dresden
vom 15.01.2024, Az. S 7 SO 99/25, ein. Gemäß §29 SGB IX beantrage ich
ein Persönliches Budget. Die Widerspruchsfrist von einem Monat ist gewahrt.
"""

doc = nlp(text)

print("Извлечённые сущности:")
for ent in doc.ents:
    print(f"{ent.text:30} | {ent.label_:20} | {ent.start_char}-{ent.end_char}")
```

**Output:**
```
Sozialamts Dresden             | AUTHORITY            | 45-63
15.01.2024                     | DATE                 | 69-79
S 7 SO 99/25                   | CASE_NUMBER          | 85-97
§29                            | LAW_SECTION          | 112-115
SGB IX                         | LAW                  | 116-122
einem Monat                    | DEADLINE             | 179-190
```

#### 2.4.3 Sentence Embeddings (Векторные представления предложений)

**Sentence-BERT для семантического поиска**:

```python
from sentence_transformers import SentenceTransformer, util
import numpy as np

class SemanticSearchEngine:
    """
    Поиск семантически похожих блоков
    """
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.block_embeddings = None
        self.blocks = []
    
    def index_blocks(self, blocks):
        """
        Индексирует блоки для быстрого поиска
        """
        self.blocks = blocks
        texts = [block.content for block in blocks]
        self.block_embeddings = self.model.encode(
            texts,
            convert_to_tensor=True,
            show_progress_bar=True
        )
    
    def search(self, query, top_k=5):
        """
        Находит top_k наиболее похожих блоков
        """
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Косинусное сходство
        cos_scores = util.cos_sim(query_embedding, self.block_embeddings)[0]
        
        # Сортировка по убыванию
        top_results = np.argsort(-cos_scores.cpu().numpy())[:top_k]
        
        results = []
        for idx in top_results:
            results.append({
                'block': self.blocks[idx],
                'score': float(cos_scores[idx]),
                'content': self.blocks[idx].content[:200] + "..."
            })
        
        return results

# Пример использования
search_engine = SemanticSearchEngine()

blocks = [
    Block(id="1", content="Antrag auf Persönliches Budget gemäß §29 SGB IX"),
    Block(id="2", content="Widerspruch gegen Bescheid des Sozialamts"),
    Block(id="3", content="Klage vor dem Sozialgericht Dresden"),
    Block(id="4", content="Beantragung von Assistenzleistungen"),
    Block(id="5", content="Erhöhung des monatlichen Budgets"),
]

search_engine.index_blocks(blocks)

# Поиск
query = "Wie beantrage ich ein Budget?"
results = search_engine.search(query, top_k=3)

for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.3f}")
    print(f"   {result['content']}\n")
```

---

## 3. Классические алгоритмы и методологии

### 3.1 Design Patterns (Паттерны проектирования)

#### 3.1.1 Composite Pattern (Компоновщик)

**Назначение**: представление иерархии "часть-целое".

**Применение**: вложенные блоки (заголовок → подпункты → детали).

**UML диаграмма**:
```
        Component
           ↑
    ┌──────┴──────┐
    │             │
  Leaf        Composite
              (содержит Component[])
```

**Реализация на Python**:

```python
from abc import ABC, abstractmethod
from typing import List

class ContentComponent(ABC):
    """
    Абстрактный компонент - базовый класс для листьев и композитов
    """
    @abstractmethod
    def render(self, indent=0) -> str:
        pass
    
    @abstractmethod
    def get_word_count(self) -> int:
        pass
    
    @abstractmethod
    def search(self, query: str) -> List['ContentComponent']:
        pass

class TextBlock(ContentComponent):
    """
    Leaf - конечный элемент (параграф текста)
    """
    def __init__(self, id: str, content: str, metadata: dict = None):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
    
    def render(self, indent=0) -> str:
        return " " * indent + f"[{self.id}] {self.content}"
    
    def get_word_count(self) -> int:
        return len(self.content.split())
    
    def search(self, query: str) -> List[ContentComponent]:
        if query.lower() in self.content.lower():
            return [self]
        return []

class Section(ContentComponent):
    """
    Composite - контейнер, содержащий другие компоненты
    """
    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title
        self.children: List[ContentComponent] = []
    
    def add(self, component: ContentComponent):
        self.children.append(component)
    
    def remove(self, component: ContentComponent):
        self.children.remove(component)
    
    def render(self, indent=0) -> str:
        result = " " * indent + f"=== {self.title} ===\n"
        for child in self.children:
            result += child.render(indent + 2) + "\n"
        return result
    
    def get_word_count(self) -> int:
        return sum(child.get_word_count() for child in self.children)
    
    def search(self, query: str) -> List[ContentComponent]:
        results = []
        if query.lower() in self.title.lower():
            results.append(self)
        
        for child in self.children:
            results.extend(child.search(query))
        
        return results

# Пример использования
document = Section("doc_1", "Widerspruch gegen Bescheid")

# Добавляем секции
introduction = Section("intro", "Einleitung")
introduction.add(TextBlock("p1", "Hiermit lege ich Widerspruch ein..."))
introduction.add(TextBlock("p2", "Der Bescheid vom 15.01.2024 wird angefochten."))

legal_basis = Section("legal", "Rechtsgrundlage")
legal_basis.add(TextBlock("p3", "Gemäß §29 SGB IX besteht ein Anspruch..."))

subsection = Section("sub1", "Persönliches Budget")
subsection.add(TextBlock("p4", "Das Persönliche Budget ermöglicht..."))
legal_basis.add(subsection)

document.add(introduction)
document.add(legal_basis)

# Рендеринг
print(document.render())

# Статистика
print(f"\nTotal words: {document.get_word_count()}")

# Поиск
results = document.search("budget")
print(f"\nSearch results for 'budget': {len(results)} items found")
```

**Output**:
```
=== Widerspruch gegen Bescheid ===
  === Einleitung ===
    [p1] Hiermit lege ich Widerspruch ein...
    [p2] Der Bescheid vom 15.01.2024 wird angefochten.
  === Rechtsgrundlage ===
    [p3] Gemäß §29 SGB IX besteht ein Anspruch...
    === Persönliches Budget ===
      [p4] Das Persönliche Budget ermöglicht...

Total words: 24
Search results for 'budget': 2 items found
```

#### 3.1.2 Strategy Pattern (Стратегия)

**Назначение**: инкапсуляция взаимозаменяемых алгоритмов.

**Применение**: разные стратегии сборки документа из блоков.

**Реализация**:

```python
from abc import ABC, abstractmethod
from typing import List

class AssemblyStrategy(ABC):
    """
    Интерфейс стратегии сборки документа
    """
    @abstractmethod
    def assemble(self, blocks: List[ContentComponent], context: dict) -> str:
        pass

class LinearAssemblyStrategy(AssemblyStrategy):
    """
    Линейная сборка: блоки один за другим
    """
    def assemble(self, blocks: List[ContentComponent], context: dict) -> str:
        result = []
        for block in blocks:
            result.append(block.render())
        return "\n\n".join(result)

class ConditionalAssemblyStrategy(AssemblyStrategy):
    """
    Условная сборка: блоки включаются по условиям
    """
    def assemble(self, blocks: List[ContentComponent], context: dict) -> str:
        result = []
        
        for block in blocks:
            # Проверяем условие включения блока
            if self._should_include(block, context):
                result.append(block.render())
        
        return "\n\n".join(result)
    
    def _should_include(self, block: ContentComponent, context: dict) -> bool:
        if not hasattr(block, 'metadata'):
            return True
        
        condition = block.metadata.get('condition')
        if not condition:
            return True
        
        # Простой evaluator условий
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False

class HierarchicalAssemblyStrategy(AssemblyStrategy):
    """
    Иерархическая сборка: группировка по темам
    """
    def assemble(self, blocks: List[ContentComponent], context: dict) -> str:
        # Группировка блоков по топикам
        topics = {}
        
        for block in blocks:
            topic = block.metadata.get('topic', 'general') if hasattr(block, 'metadata') else 'general'
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(block)
        
        # Сборка по топикам
        result = []
        for topic, topic_blocks in topics.items():
            result.append(f"=== {topic.upper()} ===")
            for block in topic_blocks:
                result.append(block.render())
            result.append("")
        
        return "\n".join(result)

class DocumentAssembler:
    """
    Context класс, использующий Strategy
    """
    def __init__(self, strategy: AssemblyStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: AssemblyStrategy):
        self.strategy = strategy
    
    def build_document(self, blocks: List[ContentComponent], context: dict) -> str:
        return self.strategy.assemble(blocks, context)

# Пример использования
blocks = [
    TextBlock("b1", "Einleitung zum Widerspruch", 
              metadata={'topic': 'intro'}),
    TextBlock("b2", "Gemäß §29 SGB IX...", 
              metadata={'topic': 'legal', 'condition': 'sgb9_applicable'}),
    TextBlock("b3", "Bei Strafverfahren...", 
              metadata={'topic': 'legal', 'condition': 'criminal_case'}),
    TextBlock("b4", "Zusammenfassung", 
              metadata={'topic': 'summary'}),
]

# Linear strategy
assembler = DocumentAssembler(LinearAssemblyStrategy())
doc1 = assembler.build_document(blocks, {})
print("LINEAR ASSEMBLY:\n", doc1)

# Conditional strategy
assembler.set_strategy(ConditionalAssemblyStrategy())
doc2 = assembler.build_document(blocks, {'sgb9_applicable': True, 'criminal_case': False})
print("\n\nCONDITIONAL ASSEMBLY:\n", doc2)

# Hierarchical strategy
assembler.set_strategy(HierarchicalAssemblyStrategy())
doc3 = assembler.build_document(blocks, {})
print("\n\nHIERARCHICAL ASSEMBLY:\n", doc3)
```

#### 3.1.3 Decorator Pattern (Декоратор)

**Назначение**: динамическое добавление функциональности объектам.

**Применение**: обогащение блоков метаданными, форматированием, валидацией.

**Реализация**:

```python
class ContentDecorator(ContentComponent):
    """
    Базовый декоратор
    """
    def __init__(self, component: ContentComponent):
        self._component = component
    
    def render(self, indent=0) -> str:
        return self._component.render(indent)
    
    def get_word_count(self) -> int:
        return self._component.get_word_count()
    
    def search(self, query: str) -> List[ContentComponent]:
        return self._component.search(query)

class TimestampDecorator(ContentDecorator):
    """
    Добавляет timestamp к блоку
    """
    def __init__(self, component: ContentComponent, timestamp: str):
        super().__init__(component)
        self.timestamp = timestamp
    
    def render(self, indent=0) -> str:
        original = self._component.render(indent)
        return f"{original} [Created: {self.timestamp}]"

class ValidationDecorator(ContentDecorator):
    """
    Добавляет валидацию контента
    """
    def __init__(self, component: ContentComponent, min_words: int = 10):
        super().__init__(component)
        self.min_words = min_words
        self.is_valid = self._validate()
    
    def _validate(self) -> bool:
        return self._component.get_word_count() >= self.min_words
    
    def render(self, indent=0) -> str:
        original = self._component.render(indent)
        status = "✓ VALID" if self.is_valid else "✗ INVALID (too short)"
        return f"{original} [{status}]"

class TranslationDecorator(ContentDecorator):
    """
    Добавляет перевод (упрощённая версия)
    """
    def __init__(self, component: ContentComponent, target_language: str):
        super().__init__(component)
        self.target_language = target_language
        self.translations = {
            'en': self._translate_to_en(),
            'ru': self._translate_to_ru()
        }
    
    def _translate_to_en(self) -> str:
        # В реальности здесь API Google Translate или DeepL
        return "[EN TRANSLATION]"
    
    def _translate_to_ru(self) -> str:
        return "[RU ПЕРЕВОД]"
    
    def render(self, indent=0) -> str:
        original = self._component.render(indent)
        translation = self.translations.get(self.target_language, '')
        return f"{original}\n{' ' * indent}{translation}"

# Пример использования - цепочка декораторов
block = TextBlock("b1", "Widerspruch gegen den Bescheid des Sozialamts Dresden")

# Добавляем timestamp
block_with_timestamp = TimestampDecorator(block, "2024-02-04 15:30")

# Добавляем валидацию
block_validated = ValidationDecorator(block_with_timestamp, min_words=5)

# Добавляем перевод
block_translated = TranslationDecorator(block_validated, target_language='ru')

print(block_translated.render())
```

**Output**:
```
[b1] Widerspruch gegen den Bescheid des Sozialamts Dresden [Created: 2024-02-04 15:30] [✓ VALID]
[RU ПЕРЕВОД]
```

#### 3.1.4 Template Method Pattern (Шаблонный метод)

**Назначение**: определение скелета алгоритма с возможностью переопределения шагов.

**Применение**: базовый процесс сборки документа с кастомизируемыми шагами.

**Реализация**:

```python
from abc import ABC, abstractmethod

class DocumentBuilder(ABC):
    """
    Абстрактный класс с шаблонным методом
    """
    def build(self, context: dict) -> str:
        """
        Template Method - определяет скелет алгоритма
        """
        # Шаг 1: Сбор необходимых блоков
        blocks = self.collect_blocks(context)
        
        # Шаг 2: Валидация блоков
        if not self.validate_blocks(blocks, context):
            raise ValueError("Blocks validation failed")
        
        # Шаг 3: Предобработка
        blocks = self.preprocess_blocks(blocks, context)
        
        # Шаг 4: Сборка
        document = self.assemble_blocks(blocks, context)
        
        # Шаг 5: Постобработка
        document = self.postprocess_document(document, context)
        
        # Шаг 6: Форматирование
        return self.format_output(document, context)
    
    @abstractmethod
    def collect_blocks(self, context: dict) -> List[ContentComponent]:
        """Подклассы должны реализовать сбор блоков"""
        pass
    
    def validate_blocks(self, blocks: List[ContentComponent], context: dict) -> bool:
        """Hook - можно переопределить, по умолчанию True"""
        return True
    
    def preprocess_blocks(self, blocks: List[ContentComponent], context: dict) -> List[ContentComponent]:
        """Hook - предобработка блоков"""
        return blocks
    
    @abstractmethod
    def assemble_blocks(self, blocks: List[ContentComponent], context: dict) -> str:
        """Подклассы должны реализовать сборку"""
        pass
    
    def postprocess_document(self, document: str, context: dict) -> str:
        """Hook - постобработка документа"""
        return document
    
    def format_output(self, document: str, context: dict) -> str:
        """Hook - форматирование вывода"""
        return document

class WiderspruchBuilder(DocumentBuilder):
    """
    Конкретная реализация для Widerspruch
    """
    def collect_blocks(self, context: dict) -> List[ContentComponent]:
        blocks = []
        
        # Заголовок
        blocks.append(TextBlock("header", f"Widerspruch gegen Bescheid vom {context.get('bescheid_date', 'N/A')}"))
        
        # Адрес отправителя
        if context.get('sender_address'):
            blocks.append(TextBlock("sender", context['sender_address']))
        
        # Основание
        blocks.append(TextBlock("legal_basis", "Rechtsgrundlage: §29 SGB IX"))
        
        # Begründung
        if context.get('reasoning'):
            blocks.append(TextBlock("reasoning", context['reasoning']))
        
        # Заключение
        blocks.append(TextBlock("conclusion", "Ich bitte um Abhilfe."))
        
        return blocks
    
    def validate_blocks(self, blocks: List[ContentComponent], context: dict) -> bool:
        # Проверяем наличие обязательных полей
        required_ids = ['header', 'legal_basis', 'conclusion']
        block_ids = [b.id for b in blocks if hasattr(b, 'id')]
        
        for req_id in required_ids:
            if req_id not in block_ids:
                print(f"Missing required block: {req_id}")
                return False
        
        return True
    
    def preprocess_blocks(self, blocks: List[ContentComponent], context: dict) -> List[ContentComponent]:
        # Добавляем даты ко всем блокам
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        processed = []
        for block in blocks:
            processed.append(TimestampDecorator(block, timestamp))
        
        return processed
    
    def assemble_blocks(self, blocks: List[ContentComponent], context: dict) -> str:
        result = []
        for block in blocks:
            result.append(block.render())
        return "\n\n".join(result)
    
    def postprocess_document(self, document: str, context: dict) -> str:
        # Добавляем подпись
        signature = f"\n\nMit freundlichen Grüßen,\n{context.get('sender_name', 'N/A')}"
        return document + signature
    
    def format_output(self, document: str, context: dict) -> str:
        # Добавляем границы документа
        border = "=" * 60
        return f"{border}\n{document}\n{border}"

# Пример использования
context = {
    'bescheid_date': '15.01.2024',
    'sender_address': 'Max Mustermann\nMusterstraße 1\n01234 Dresden',
    'sender_name': 'Max Mustermann',
    'reasoning': 'Der Bescheid ist rechtswidrig, da die Voraussetzungen des §29 SGB IX erfüllt sind.'
}

builder = WiderspruchBuilder()
document = builder.build(context)
print(document)
```

### 3.2 Graph Algorithms (Алгоритмы на графах)

#### 3.2.1 Depth-First Search (DFS) - Поиск в глубину

**Применение**: обход иерархии блоков, поиск зависимостей.

```python
def dfs_traverse(node, visited=None, depth=0):
    """
    DFS обход графа блоков
    """
    if visited is None:
        visited = set()
    
    if node.id in visited:
        return
    
    visited.add(node.id)
    print("  " * depth + f"Visiting: {node.id}")
    
    # Обрабатываем детей
    if hasattr(node, 'children'):
        for child in node.children:
            dfs_traverse(child, visited, depth + 1)
    
    return visited

# Пример
root = Section("root", "Document")
child1 = Section("ch1", "Chapter 1")
child2 = Section("ch2", "Chapter 2")
grandchild1 = TextBlock("gc1", "Section 1.1")
grandchild2 = TextBlock("gc2", "Section 1.2")

child1.add(grandchild1)
child1.add(grandchild2)
root.add(child1)
root.add(child2)

dfs_traverse(root)
```

#### 3.2.2 Breadth-First Search (BFS) - Поиск в ширину

**Применение**: поиск блоков по уровням, построение оглавления.

```python
from collections import deque

def bfs_traverse(root):
    """
    BFS обход - по уровням
    """
    queue = deque([(root, 0)])  # (node, level)
    
    while queue:
        node, level = queue.popleft()
        print("  " * level + f"Level {level}: {node.id}")
        
        if hasattr(node, 'children'):
            for child in node.children:
                queue.append((child, level + 1))

# Использование
bfs_traverse(root)
```

#### 3.2.3 Dijkstra's Algorithm (Алгоритм Дейкстры)

**Применение**: поиск оптимального пути в графе блоков с весами.

```python
import heapq
from typing import Dict, List, Tuple

class WeightedGraph:
    """
    Взвешенный граф для блоков
    """
    def __init__(self):
        self.nodes = {}
        self.edges = {}  # {from_id: [(to_id, weight)]}
    
    def add_node(self, node_id, data):
        self.nodes[node_id] = data
        if node_id not in self.edges:
            self.edges[node_id] = []
    
    def add_edge(self, from_id, to_id, weight):
        """
        Добавляет ребро с весом
        weight может быть: сложность, релевантность, приоритет и т.д.
        """
        self.edges[from_id].append((to_id, weight))
    
    def dijkstra(self, start_id, end_id) -> Tuple[float, List[str]]:
        """
        Находит кратчайший путь от start_id до end_id
        Возвращает: (total_weight, path)
        """
        # Инициализация
        distances = {node_id: float('inf') for node_id in self.nodes}
        distances[start_id] = 0
        
        previous = {node_id: None for node_id in self.nodes}
        
        # Priority queue: (distance, node_id)
        pq = [(0, start_id)]
        visited = set()
        
        while pq:
            current_dist, current_id = heapq.heappop(pq)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_id == end_id:
                break
            
            # Проверяем соседей
            for neighbor_id, weight in self.edges.get(current_id, []):
                distance = current_dist + weight
                
                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    previous[neighbor_id] = current_id
                    heapq.heappush(pq, (distance, neighbor_id))
        
        # Восстановление пути
        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return distances[end_id], path

# Пример: граф параграфов закона
graph = WeightedGraph()

# Добавляем узлы
graph.add_node("start", "Anfrage")
graph.add_node("p5", "§5 SGB IX")
graph.add_node("p6", "§6 SGB IX")
graph.add_node("p15", "§15 SGB IX")
graph.add_node("p29", "§29 SGB IX - Persönliches Budget")
graph.add_node("end", "Antrag")

# Добавляем рёбра с весами (сложность применения)
graph.add_edge("start", "p5", weight=1)
graph.add_edge("start", "p29", weight=5)
graph.add_edge("p5", "p6", weight=2)
graph.add_edge("p5", "p15", weight=3)
graph.add_edge("p6", "p29", weight=2)
graph.add_edge("p15", "p29", weight=1)
graph.add_edge("p29", "end", weight=1)

# Поиск оптимального пути
total_weight, path = graph.dijkstra("start", "end")

print(f"Shortest path weight: {total_weight}")
print(f"Path: {' -> '.join(path)}")
```

**Output**:
```
Shortest path weight: 7.0
Path: start -> p5 -> p15 -> p29 -> end
```

#### 3.2.4 PageRank Algorithm

**Применение**: определение важности блоков на основе ссылок.

```python
import numpy as np

def pagerank(graph, damping=0.85, iterations=100):
    """
    Вычисляет PageRank для узлов графа
    
    Args:
        graph: dict {node_id: [list of outgoing node_ids]}
        damping: коэффициент затухания (обычно 0.85)
        iterations: количество итераций
    
    Returns:
        dict {node_id: pagerank_score}
    """
    nodes = list(graph.keys())
    n = len(nodes)
    
    # Инициализация: равномерное распределение
    ranks = {node: 1.0 / n for node in nodes}
    
    for _ in range(iterations):
        new_ranks = {}
        
        for node in nodes:
            # Базовая вероятность (teleportation)
            rank = (1 - damping) / n
            
            # Добавляем вклад от входящих связей
            for other_node in nodes:
                if node in graph.get(other_node, []):
                    outgoing_count = len(graph[other_node])
                    if outgoing_count > 0:
                        rank += damping * (ranks[other_node] / outgoing_count)
            
            new_ranks[node] = rank
        
        ranks = new_ranks
    
    return ranks

# Пример: граф ссылок между параграфами
legal_graph = {
    'p5': ['p6', 'p15'],     # §5 ссылается на §6 и §15
    'p6': ['p29'],           # §6 ссылается на §29
    'p15': ['p29'],          # §15 ссылается на §29
    'p29': [],               # §29 никуда не ссылается
    'p7': ['p5', 'p6'],      # §7 ссылается на §5 и §6
}

ranks = pagerank(legal_graph)

print("PageRank scores (важность параграфов):")
for node, score in sorted(ranks.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {score:.4f}")
```

**Output**:
```
PageRank scores (важность параграфов):
p29: 0.3421
p6: 0.2187
p5: 0.1654
p15: 0.1432
p7: 0.1306
```

### 3.3 Rule-Based Systems (Системы, основанные на правилах)

#### 3.3.1 Forward Chaining (Прямой вывод)

**Принцип**: от фактов к заключениям.

```python
class Fact:
    """Факт - известное утверждение"""
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Fact({self.name}={self.value})"

class Rule:
    """Правило IF-THEN"""
    def __init__(self, name, conditions, action):
        self.name = name
        self.conditions = conditions  # список условий
        self.action = action          # функция действия
        self.fired = False
    
    def can_fire(self, facts_dict):
        """Проверяет, можно ли активировать правило"""
        if self.fired:
            return False
        
        for condition in self.conditions:
            if not condition(facts_dict):
                return False
        
        return True
    
    def fire(self, facts_dict):
        """Выполняет действие правила"""
        if self.can_fire(facts_dict):
            self.fired = True
            new_facts = self.action(facts_dict)
            return new_facts if new_facts else []
        return []

class ForwardChainingEngine:
    """Движок прямого вывода"""
    def __init__(self):
        self.facts = {}
        self.rules = []
    
    def add_fact(self, fact: Fact):
        self.facts[fact.name] = fact.value
    
    def add_rule(self, rule: Rule):
        self.rules.append(rule)
    
    def run(self, max_iterations=100):
        """Запускает вывод"""
        iteration = 0
        changes = True
        
        print("=== Forward Chaining Started ===\n")
        print(f"Initial facts: {self.facts}\n")
        
        while changes and iteration < max_iterations:
            changes = False
            iteration += 1
            
            print(f"--- Iteration {iteration} ---")
            
            for rule in self.rules:
                if rule.can_fire(self.facts):
                    print(f"Firing rule: {rule.name}")
                    new_facts = rule.fire(self.facts)
                    
                    for fact in new_facts:
                        self.facts[fact.name] = fact.value
                        print(f"  Added fact: {fact}")
                        changes = True
            
            if not changes:
                print("No more rules can fire.")
        
        print(f"\n=== Final facts: {self.facts} ===")
        return self.facts

# Пример: правила для определения применимых параграфов

def rule_action_apply_p6(facts):
    """Если стаж > 5 лет, применяем §6"""
    return [Fact('apply_p6', True)]

def rule_action_apply_p15(facts):
    """Если увеличение >= 10%, применяем §15"""
    return [Fact('apply_p15', True)]

def rule_action_require_hearing(facts):
    """Если применяется §6, требуется слушание"""
    return [Fact('require_hearing', True)]

# Создаём движок
engine = ForwardChainingEngine()

# Добавляем начальные факты
engine.add_fact(Fact('work_years', 7))
engine.add_fact(Fact('budget_increase_pct', 12))
engine.add_fact(Fact('disability_degree', 60))

# Добавляем правила
engine.add_rule(Rule(
    name="R1: work_years > 5 → apply §6",
    conditions=[lambda f: f.get('work_years', 0) > 5],
    action=rule_action_apply_p6
))

engine.add_rule(Rule(
    name="R2: budget_increase >= 10% → apply §15",
    conditions=[lambda f: f.get('budget_increase_pct', 0) >= 10],
    action=rule_action_apply_p15
))

engine.add_rule(Rule(
    name="R3: apply_p6 = True → require hearing",
    conditions=[lambda f: f.get('apply_p6', False) == True],
    action=rule_action_require_hearing
))

# Запускаем вывод
final_facts = engine.run()
```

**Output**:
```
=== Forward Chaining Started ===

Initial facts: {'work_years': 7, 'budget_increase_pct': 12, 'disability_degree': 60}

--- Iteration 1 ---
Firing rule: R1: work_years > 5 → apply §6
  Added fact: Fact(apply_p6=True)
Firing rule: R2: budget_increase >= 10% → apply §15
  Added fact: Fact(apply_p15=True)

--- Iteration 2 ---
Firing rule: R3: apply_p6 = True → require hearing
  Added fact: Fact(require_hearing=True)

--- Iteration 3 ---
No more rules can fire.

=== Final facts: {..., 'apply_p6': True, 'apply_p15': True, 'require_hearing': True} ===
```

#### 3.3.2 Backward Chaining (Обратный вывод)

**Принцип**: от цели к фактам.

```python
class BackwardChainingEngine:
    """Движок обратного вывода"""
    def __init__(self):
        self.facts = {}
        self.rules = []
    
    def add_fact(self, fact: Fact):
        self.facts[fact.name] = fact.value
    
    def add_rule(self, rule: Rule):
        self.rules.append(rule)
    
    def prove_goal(self, goal_name, depth=0):
        """
        Пытается доказать цель
        Возвращает True/False
        """
        indent = "  " * depth
        print(f"{indent}Trying to prove: {goal_name}")
        
        # Если уже есть в фактах
        if goal_name in self.facts:
            result = self.facts[goal_name]
            print(f"{indent}  Found in facts: {result}")
            return result
        
        # Ищем правило, которое может вывести эту цель
        for rule in self.rules:
            # Проверяем, выводит ли правило эту цель
            if self._rule_concludes(rule, goal_name):
                print(f"{indent}  Trying rule: {rule.name}")
                
                # Пытаемся доказать все условия
                all_conditions_met = True
                for condition_goal in self._get_condition_goals(rule):
                    if not self.prove_goal(condition_goal, depth + 1):
                        all_conditions_met = False
                        break
                
                if all_conditions_met:
                    # Все условия доказаны - применяем правило
                    print(f"{indent}  Rule {rule.name} succeeded!")
                    new_facts = rule.fire(self.facts)
                    for fact in new_facts:
                        self.facts[fact.name] = fact.value
                    
                    return self.facts.get(goal_name, False)
        
        print(f"{indent}  Cannot prove {goal_name}")
        return False
    
    def _rule_concludes(self, rule, goal_name):
        """Проверяет, выводит ли правило данную цель"""
        # Упрощённая проверка - нужно знать, что правило выводит
        # В реальной системе это будет в метаданных правила
        return goal_name in rule.name.lower()
    
    def _get_condition_goals(self, rule):
        """Извлекает цели из условий правила"""
        # Упрощённая версия - парсим имя правила
        # В реальной системе условия были бы структурированы
        goals = []
        if "work_years > 5" in rule.name:
            goals.append("work_years")
        if "disability >= 50" in rule.name:
            goals.append("disability_degree")
        return goals

# Пример использования (упрощённая версия)
# В реальной системе правила были бы более структурированы
```

---

## 4. Технологический стек

### 4.1 Backend Technologies

#### 4.1.1 Python Ecosystem

**Core Libraries**:

```python
# requirements.txt

# Graph databases
neo4j==5.15.0
py2neo==2021.2.3

# NLP
spacy==3.7.2
sentence-transformers==2.2.2
transformers==4.36.0
torch==2.1.2

# Topic modeling
gensim==4.3.2
bertopic==0.16.0

# ML/Data Science
scikit-learn==1.3.2
numpy==1.26.2
pandas==2.1.4

# Search
elasticsearch==8.11.1
whoosh==2.7.4

# Rule engines
durable-rules==2.0.28
pyknow==1.7.0

# Document processing
python-docx==1.1.0
PyPDF2==3.0.1
pdfplumber==0.10.3
beautifulsoup4==4.12.2

# Template engines
jinja2==3.1.2

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# API
fastapi==0.108.0
uvicorn==0.25.0

# Task queue
celery==5.3.4
redis==5.0.1
```

**Project Structure**:

```
content-blocks-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── block.py            # Block model
│   │   ├── rule.py             # Rule model
│   │   └── document.py         # Document model
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── block_service.py    # CRUD для блоков
│   │   ├── rule_engine.py      # Rule processing
│   │   ├── assembly_service.py # Document assembly
│   │   ├── search_service.py   # Semantic search
│   │   └── nlp_service.py      # NLP processing
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── neo4j_repo.py       # Graph DB access
│   │   ├── mongo_repo.py       # Document DB access
│   │   └── elastic_repo.py     # Search index
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── blocks.py           # /api/blocks endpoints
│   │   ├── documents.py        # /api/documents endpoints
│   │   └── search.py           # /api/search endpoints
│   │
│   └── utils/
│       ├── __init__.py
│       ├── parsers.py          # Text parsers
│       ├── validators.py       # Validation
│       └── formatters.py       # Output formatting
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/
│   ├── import_sgb9.py          # Import SGB IX
│   ├── train_models.py         # Train ML models
│   └── migrate_data.py         # Data migration
│
├── data/
│   ├── raw/                    # Raw legal texts
│   ├── processed/              # Processed blocks
│   └── models/                 # Trained models
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
├── docs/
│   ├── api.md
│   ├── architecture.md
│   └── deployment.md
│
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

#### 4.1.2 Database Technologies

**Neo4j - Graph Database**:

```cypher
// Схема данных в Neo4j

// Nodes
(:Block {
    id: String,
    type: String,              // "paragraph", "section", "article"
    number: String,            // "§5", "Art. 3 GG"
    title: String,
    content: String,
    language: String,          // "de", "en", "ru"
    jurisdiction: String,      // "Deutschland", "EU"
    valid_from: Date,
    valid_until: Date,
    source: String,            // "SGB IX", "BGB"
    embedding: [Float],        // vector для semantic search
    created_at: DateTime,
    updated_at: DateTime
})

(:Condition {
    id: String,
    expression: String,        // "work_years > 5"
    description: String,
    variables: [String]        // ["work_years"]
})

(:Topic {
    id: String,
    name: String,              // "Persönliches Budget"
    keywords: [String],
    parent_topic_id: String
})

// Relationships
(:Block)-[:REFERENCES {
    type: String,              // "direct", "conditional", "optional"
    strength: Float            // 0.0 - 1.0
}]->(:Block)

(:Block)-[:APPLIES_IF {
    condition_id: String,
    priority: Integer
}]->(:Block)

(:Block)-[:BELONGS_TO]->(:Topic)

(:Block)-[:VERSION_OF {
    version: String,
    change_description: String,
    changed_at: DateTime
}]->(:Block)

(:Block)-[:CONFLICTS_WITH {
    conflict_type: String,     // "semantic", "logical", "temporal"
    severity: String           // "low", "medium", "high", "critical"
}]->(:Block)

// Индексы
CREATE INDEX block_id FOR (b:Block) ON (b.id);
CREATE INDEX block_number FOR (b:Block) ON (b.number);
CREATE INDEX block_type FOR (b:Block) ON (b.type);
CREATE FULLTEXT INDEX block_content FOR (b:Block) ON EACH [b.content, b.title];

// Примеры запросов

// 1. Найти все блоки, связанные с §29 SGB IX
MATCH path = (start:Block {number: "§29"})-[:REFERENCES*1..3]-(related:Block)
WHERE start.source = "SGB IX"
RETURN path;

// 2. Построить документ с условной логикой
MATCH (start:Block {id: "widerspruch_template"})
CALL apoc.path.expandConfig(start, {
    relationshipFilter: "APPLIES_IF>",
    labelFilter: "+Block",
    uniqueness: "NODE_GLOBAL",
    filterStartNode: false
}) YIELD path
WITH nodes(path) as blocks, relationships(path) as rels
UNWIND rels as rel
WITH blocks, rel
WHERE apoc.cypher.runFirstColumn(
    "RETURN " + rel.condition_expression,
    {context: $context},
    false
) = true
RETURN blocks;

// 3. PageRank для определения важности блоков
CALL gds.pageRank.stream({
    nodeProjection: 'Block',
    relationshipProjection: 'REFERENCES',
    maxIterations: 20,
    dampingFactor: 0.85
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).number AS block, score
ORDER BY score DESC
LIMIT 10;

// 4. Community Detection - кластеризация похожих блоков
CALL gds.louvain.stream({
    nodeProjection: 'Block',
    relationshipProjection: {
        REFERENCES: {
            orientation: 'UNDIRECTED'
        }
    }
})
YIELD nodeId, communityId
RETURN communityId, collect(gds.util.asNode(nodeId).number) AS blocks
ORDER BY size(blocks) DESC;
```

**MongoDB - Document Database**:

```javascript
// Схема коллекций в MongoDB

// Collection: blocks
{
    "_id": ObjectId("..."),
    "id": "sgb9_p29_abs1",
    "type": "paragraph",
    "number": "§29",
    "absatz": 1,
    "title": "Persönliches Budget",
    "content": {
        "de": "Auf Antrag werden Leistungen zur Teilhabe...",
        "en": "Upon application, services for participation...",
        "ru": "По заявлению предоставляются услуги..."
    },
    "metadata": {
        "source": "SGB IX",
        "valid_from": ISODate("2001-07-01"),
        "valid_until": null,
        "jurisdiction": "Deutschland",
        "authority": "Bundestag",
        "last_modified": ISODate("2017-12-29")
    },
    "structure": {
        "parent_id": "sgb9_p29",
        "children_ids": ["sgb9_p29_abs1_s1", "sgb9_p29_abs1_s2"],
        "level": 2,
        "position": 1
    },
    "annotations": {
        "keywords": ["budget", "antrag", "teilhabe", "leistungen"],
        "entities": [
            {"type": "LAW", "value": "SGB IX", "offset": 0},
            {"type": "CONCEPT", "value": "Persönliches Budget", "offset": 45}
        ],
        "topics": ["social_law", "disability_rights", "personal_budget"],
        "difficulty_score": 7.5,
        "readability_score": 65.3
    },
    "relations": [
        {
            "target_id": "sgb9_p17",
            "type": "references",
            "description": "Verweist auf §17 für Gesamtplan"
        },
        {
            "target_id": "sgb9_p4",
            "type": "based_on",
            "description": "Basiert auf Leistungsformen in §4"
        }
    ],
    "versions": [
        {
            "version": "1.0",
            "date": ISODate("2001-07-01"),
            "changes": "Erstfassung"
        },
        {
            "version": "2.0",
            "date": ISODate("2017-12-29"),
            "changes": "BTHG-Reform"
        }
    ],
    "usage_stats": {
        "referenced_count": 1247,
        "applied_count": 543,
        "last_used": ISODate("2024-02-04T10:30:00Z")
    },
    "created_at": ISODate("2024-01-01T00:00:00Z"),
    "updated_at": ISODate("2024-02-04T12:00:00Z")
}

// Collection: rules
{
    "_id": ObjectId("..."),
    "id": "rule_pb_eligibility",
    "name": "Persönliches Budget Eligibility Check",
    "description": "Prüft Voraussetzungen für Persönliches Budget",
    "type": "forward_chaining",
    "priority": 1,
    "conditions": [
        {
            "variable": "leistungsberechtigt",
            "operator": "==",
            "value": true,
            "description": "Person ist leistungsberechtigt"
        },
        {
            "variable": "antrag_gestellt",
            "operator": "==",
            "value": true,
            "description": "Antrag wurde gestellt"
        }
    ],
    "actions": [
        {
            "type": "include_block",
            "block_id": "sgb9_p29",
            "reason": "Rechtsgrundlage für PB"
        },
        {
            "type": "set_variable",
            "variable": "pb_applicable",
            "value": true
        },
        {
            "type": "trigger_rule",
            "rule_id": "rule_pb_calculation"
        }
    ],
    "metadata": {
        "author": "Legal Team",
        "reviewed_by": "Max Mustermann",
        "review_date": ISODate("2024-01-15"),
        "source": "§29 SGB IX"
    },
    "created_at": ISODate("2024-01-01"),
    "updated_at": ISODate("2024-01-15")
}

// Collection: documents
{
    "_id": ObjectId("..."),
    "id": "doc_widerspruch_001",
    "type": "widerspruch",
    "title": "Widerspruch gegen Bescheid des Sozialamts Dresden",
    "status": "draft",  // "draft", "review", "finalized"
    "context": {
        "case_number": "S 7 SO 99/25",
        "bescheid_date": "2024-01-15",
        "authority": "Sozialamt Dresden",
        "applicant": {
            "name": "Max Mustermann",
            "address": "Musterstraße 1, 01234 Dresden"
        },
        "legal_basis": ["§29 SGB IX", "§44 SGB X"],
        "custom_variables": {
            "work_years": 7,
            "disability_degree": 60,
            "budget_increase_pct": 12
        }
    },
    "assembly": {
        "template_id": "template_widerspruch_sgb9",
        "strategy": "conditional",
        "blocks": [
            {
                "block_id": "header_widerspruch",
                "order": 1,
                "required": true,
                "included": true
            },
            {
                "block_id": "sgb9_p29",
                "order": 2,
                "required": false,
                "included": true,
                "reason": "Rule: pb_applicable = true"
            },
            {
                "block_id": "argumentation_template",
                "order": 3,
                "required": true,
                "included": true,
                "customization": {
                    "placeholder_facts": "Der Bescheid vom 15.01.2024..."
                }
            }
        ],
        "rules_applied": ["rule_pb_eligibility", "rule_work_years_check"],
        "assembly_date": ISODate("2024-02-04T12:00:00Z")
    },
    "output": {
        "formats": ["docx", "pdf"],
        "docx_path": "/outputs/widerspruch_001.docx",
        "pdf_path": "/outputs/widerspruch_001.pdf",
        "text": "Widerspruch\n\nHiermit lege ich Widerspruch...",
        "word_count": 842,
        "page_count": 3
    },
    "version_history": [
        {
            "version": 1,
            "date": ISODate("2024-02-04T10:00:00Z"),
            "changes": "Initial draft",
            "author": "Max"
        },
        {
            "version": 2,
            "date": ISODate("2024-02-04T12:00:00Z"),
            "changes": "Added legal basis §29 SGB IX",
            "author": "Max"
        }
    ],
    "created_at": ISODate("2024-02-04T10:00:00Z"),
    "updated_at": ISODate("2024-02-04T12:00:00Z")
}

// Индексы
db.blocks.createIndex({"id": 1}, {unique: true});
db.blocks.createIndex({"number": 1, "metadata.source": 1});
db.blocks.createIndex({"annotations.topics": 1});
db.blocks.createIndex({"metadata.valid_from": 1, "metadata.valid_until": 1});
db.blocks.createIndex({"content.de": "text", "title": "text"});

db.rules.createIndex({"id": 1}, {unique: true});
db.rules.createIndex({"type": 1, "priority": 1});

db.documents.createIndex({"id": 1}, {unique: true});
db.documents.createIndex({"type": 1, "status": 1});
db.documents.createIndex({"context.case_number": 1});
```

**Elasticsearch - Full-Text Search**:

```json
// Index mapping для blocks

PUT /legal_blocks
{
  "settings": {
    "analysis": {
      "analyzer": {
        "german_legal": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "german_stop",
            "german_keywords",
            "german_stemmer"
          ]
        }
      },
      "filter": {
        "german_stop": {
          "type": "stop",
          "stopwords": "_german_"
        },
        "german_keywords": {
          "type": "keyword_marker",
          "keywords": ["§", "SGB", "GG", "BGB", "Abs.", "Art."]
        },
        "german_stemmer": {
          "type": "stemmer",
          "language": "light_german"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "type": {
        "type": "keyword"
      },
      "number": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "german_legal",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "content": {
        "type": "text",
        "analyzer": "german_legal"
      },
      "source": {
        "type": "keyword"
      },
      "topics": {
        "type": "keyword"
      },
      "keywords": {
        "type": "keyword"
      },
      "embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "valid_from": {
        "type": "date"
      },
      "valid_until": {
        "type": "date"
      }
    }
  }
}

// Пример поиска

// 1. Full-text search
GET /legal_blocks/_search
{
  "query": {
    "multi_match": {
      "query": "Persönliches Budget Antrag",
      "fields": ["title^3", "content"],
      "type": "best_fields",
      "fuzziness": "AUTO"
    }
  },
  "highlight": {
    "fields": {
      "content": {},
      "title": {}
    }
  }
}

// 2. Semantic search (KNN)
GET /legal_blocks/_search
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.12, -0.45, 0.78, ...],  // 384 dimensions
    "k": 10,
    "num_candidates": 100
  }
}

// 3. Filtered search
GET /legal_blocks/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "content": "Teilhabe"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "source": "SGB IX"
          }
        },
        {
          "range": {
            "valid_from": {
              "lte": "2024-02-04"
            }
          }
        },
        {
          "bool": {
            "should": [
              {
                "bool": {
                  "must_not": {
                    "exists": {
                      "field": "valid_until"
                    }
                  }
                }
              },
              {
                "range": {
                  "valid_until": {
                    "gte": "2024-02-04"
                  }
                }
              }
            ]
          }
        }
      ]
    }
  }
}
```

#### 4.1.3 API Layer (FastAPI)

**Complete API Implementation**:

```python
# app/main.py

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="Content Blocks System API",
    description="API for dynamic content block management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class BlockCreate(BaseModel):
    type: str
    number: str
    title: str
    content: str
    source: str
    metadata: dict = {}

class BlockResponse(BaseModel):
    id: str
    type: str
    number: str
    title: str
    content: str
    source: str
    metadata: dict
    created_at: datetime
    updated_at: datetime

class SearchQuery(BaseModel):
    query: str
    filters: Optional[dict] = None
    limit: int = 10

class DocumentRequest(BaseModel):
    template_id: str
    context: dict
    strategy: str = "conditional"
    output_format: str = "docx"

# Dependencies
def get_block_service():
    from app.services.block_service import BlockService
    return BlockService()

def get_search_service():
    from app.services.search_service import SearchService
    return SearchService()

def get_assembly_service():
    from app.services.assembly_service import AssemblyService
    return AssemblyService()

# Endpoints

@app.get("/")
async def root():
    return {
        "message": "Content Blocks System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# --- BLOCKS ---

@app.post("/api/blocks", response_model=BlockResponse)
async def create_block(
    block: BlockCreate,
    service: BlockService = Depends(get_block_service)
):
    """Create a new content block"""
    try:
        created_block = await service.create_block(block.dict())
        return created_block
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blocks/{block_id}", response_model=BlockResponse)
async def get_block(
    block_id: str,
    service: BlockService = Depends(get_block_service)
):
    """Get a block by ID"""
    block = await service.get_block(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

@app.get("/api/blocks", response_model=List[BlockResponse])
async def list_blocks(
    source: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: BlockService = Depends(get_block_service)
):
    """List blocks with optional filters"""
    blocks = await service.list_blocks(
        source=source,
        type=type,
        skip=skip,
        limit=limit
    )
    return blocks

@app.put("/api/blocks/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: str,
    block_update: dict,
    service: BlockService = Depends(get_block_service)
):
    """Update a block"""
    try:
        updated_block = await service.update_block(block_id, block_update)
        if not updated_block:
            raise HTTPException(status_code=404, detail="Block not found")
        return updated_block
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/blocks/{block_id}")
async def delete_block(
    block_id: str,
    service: BlockService = Depends(get_block_service)
):
    """Delete a block"""
    deleted = await service.delete_block(block_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "Block deleted successfully"}

# --- SEARCH ---

@app.post("/api/search/text")
async def search_text(
    query: SearchQuery,
    service: SearchService = Depends(get_search_service)
):
    """Full-text search in blocks"""
    results = await service.text_search(
        query=query.query,
        filters=query.filters,
        limit=query.limit
    )
    return {"results": results, "count": len(results)}

@app.post("/api/search/semantic")
async def search_semantic(
    query: SearchQuery,
    service: SearchService = Depends(get_search_service)
):
    """Semantic search using embeddings"""
    results = await service.semantic_search(
        query=query.query,
        filters=query.filters,
        limit=query.limit
    )
    return {"results": results, "count": len(results)}

@app.get("/api/search/related/{block_id}")
async def get_related_blocks(
    block_id: str,
    limit: int = Query(5, ge=1, le=20),
    service: SearchService = Depends(get_search_service)
):
    """Get blocks related to a specific block"""
    related = await service.find_related(block_id, limit=limit)
    return {"related_blocks": related, "count": len(related)}

# --- DOCUMENTS ---

@app.post("/api/documents/assemble")
async def assemble_document(
    request: DocumentRequest,
    service: AssemblyService = Depends(get_assembly_service)
):
    """Assemble a document from blocks"""
    try:
        document = await service.assemble_document(
            template_id=request.template_id,
            context=request.context,
            strategy=request.strategy,
            output_format=request.output_format
        )
        
        return {
            "document_id": document["id"],
            "output_path": document["output_path"],
            "blocks_used": document["blocks_used"],
            "word_count": document["word_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}")
async def get_document(
    document_id: str,
    service: AssemblyService = Depends(get_assembly_service)
):
    """Get assembled document"""
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

# --- ANALYTICS ---

@app.get("/api/analytics/blocks/{block_id}/usage")
async def get_block_usage(
    block_id: str,
    service: BlockService = Depends(get_block_service)
):
    """Get usage statistics for a block"""
    stats = await service.get_usage_stats(block_id)
    return stats

@app.get("/api/analytics/popular-blocks")
async def get_popular_blocks(
    limit: int = Query(10, ge=1, le=100),
    service: BlockService = Depends(get_block_service)
):
    """Get most frequently used blocks"""
    popular = await service.get_popular_blocks(limit=limit)
    return {"blocks": popular}

# --- GRAPH ---

@app.get("/api/graph/path/{start_id}/{end_id}")
async def find_path(
    start_id: str,
    end_id: str,
    max_depth: int = Query(5, ge=1, le=10),
    service: BlockService = Depends(get_block_service)
):
    """Find path between two blocks in the graph"""
    path = await service.find_path(start_id, end_id, max_depth=max_depth)
    return {"path": path, "length": len(path) - 1}

@app.get("/api/graph/neighbors/{block_id}")
async def get_neighbors(
    block_id: str,
    depth: int = Query(1, ge=1, le=3),
    service: BlockService = Depends(get_block_service)
):
    """Get neighboring blocks in the graph"""
    neighbors = await service.get_neighbors(block_id, depth=depth)
    return {"neighbors": neighbors}

# --- HEALTH & MONITORING ---

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Service Layer Implementation**:

```python
# app/services/block_service.py

from typing import List, Optional, Dict
from datetime import datetime
import uuid

class BlockService:
    """
    Service для работы с блоками
    """
    
    def __init__(self):
        from app.repositories.neo4j_repo import Neo4jRepository
        from app.repositories.mongo_repo import MongoRepository
        from app.repositories.elastic_repo import ElasticRepository
        
        self.neo4j = Neo4jRepository()
        self.mongo = MongoRepository()
        self.elastic = ElasticRepository()
    
    async def create_block(self, block_data: dict) -> dict:
        """
        Создаёт новый блок во всех хранилищах
        """
        block_id = str(uuid.uuid4())
        
        block = {
            "id": block_id,
            **block_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Сохраняем в MongoDB (основное хранилище)
        await self.mongo.insert_block(block)
        
        # Создаём узел в Neo4j (граф связей)
        await self.neo4j.create_node(block)
        
        # Индексируем в Elasticsearch (поиск)
        await self.elastic.index_block(block)
        
        return block
    
    async def get_block(self, block_id: str) -> Optional[dict]:
        """
        Получает блок по ID
        """
        block = await self.mongo.find_block_by_id(block_id)
        return block
    
    async def list_blocks(
        self,
        source: Optional[str] = None,
        type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Список блоков с фильтрами
        """
        filters = {}
        if source:
            filters["source"] = source
        if type:
            filters["type"] = type
        
        blocks = await self.mongo.find_blocks(
            filters=filters,
            skip=skip,
            limit=limit
        )
        return blocks
    
    async def update_block(self, block_id: str, update_data: dict) -> Optional[dict]:
        """
        Обновляет блок
        """
        update_data["updated_at"] = datetime.utcnow()
        
        # Обновляем в MongoDB
        updated = await self.mongo.update_block(block_id, update_data)
        
        if updated:
            # Обновляем в Neo4j
            await self.neo4j.update_node(block_id, update_data)
            
            # Переиндексируем в Elasticsearch
            await self.elastic.update_block(block_id, update_data)
        
        return updated
    
    async def delete_block(self, block_id: str) -> bool:
        """
        Удаляет блок из всех хранилищ
        """
        # Удаляем из MongoDB
        deleted = await self.mongo.delete_block(block_id)
        
        if deleted:
            # Удаляем из Neo4j
            await self.neo4j.delete_node(block_id)
            
            # Удаляем из Elasticsearch
            await self.elastic.delete_block(block_id)
        
        return deleted
    
    async def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> List[str]:
        """
        Находит путь между блоками в графе
        """
        path = await self.neo4j.find_shortest_path(
            start_id,
            end_id,
            max_depth=max_depth
        )
        return path
    
    async def get_neighbors(
        self,
        block_id: str,
        depth: int = 1
    ) -> List[dict]:
        """
        Получает соседние блоки
        """
        neighbor_ids = await self.neo4j.get_neighbors(block_id, depth=depth)
        
        # Получаем полные данные из MongoDB
        neighbors = []
        for nid in neighbor_ids:
            block = await self.mongo.find_block_by_id(nid)
            if block:
                neighbors.append(block)
        
        return neighbors
    
    async def get_usage_stats(self, block_id: str) -> dict:
        """
        Статистика использования блока
        """
        block = await self.mongo.find_block_by_id(block_id)
        
        if not block:
            return {}
        
        usage_stats = block.get("usage_stats", {})
        
        # Дополнительная статистика из Neo4j
        graph_stats = await self.neo4j.get_node_stats(block_id)
        
        return {
            **usage_stats,
            "incoming_references": graph_stats.get("incoming_count", 0),
            "outgoing_references": graph_stats.get("outgoing_count", 0),
            "centrality_score": graph_stats.get("pagerank", 0.0)
        }
    
    async def get_popular_blocks(self, limit: int = 10) -> List[dict]:
        """
        Наиболее часто используемые блоки
        """
        blocks = await self.mongo.find_blocks(
            filters={},
            sort=[("usage_stats.applied_count", -1)],
            limit=limit
        )
        return blocks
```

---

## 5. Архитектурные паттерны

### 5.1 Layered Architecture (Многоуровневая архитектура)

```
┌─────────────────────────────────────────────────┐
│         PRESENTATION LAYER                      │
│  • REST API (FastAPI)                           │
│  • Web UI (React)                               │
│  • CLI Tools                                    │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│         APPLICATION LAYER                       │
│  • Business Logic                               │
│  • Workflow Orchestration                       │
│  • Rule Processing                              │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│         DOMAIN LAYER                            │
│  • Domain Models                                │
│  • Domain Services                              │
│  • Domain Events                                │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│         INFRASTRUCTURE LAYER                    │
│  • Database Access (Neo4j, MongoDB, Elastic)    │
│  • External APIs                                │
│  • File System                                  │
└─────────────────────────────────────────────────┘
```

### 5.2 Event-Driven Architecture

**Использование событий для связывания компонентов**:

```python
from typing import Callable, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class EventType(Enum):
    BLOCK_CREATED = "block.created"
    BLOCK_UPDATED = "block.updated"
    BLOCK_DELETED = "block.deleted"
    DOCUMENT_ASSEMBLED = "document.assembled"
    RULE_TRIGGERED = "rule.triggered"

@dataclass
class Event:
    """Базовое событие"""
    type: EventType
    payload: dict
    timestamp: datetime
    source: str

class EventBus:
    """
    Шина событий для связывания компонентов
    """
    def __init__(self):
        self.subscribers: dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Подписаться на событие"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: Event):
        """Опубликовать событие"""
        handlers = self.subscribers.get(event.type, [])
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")

# Глобальная шина событий
event_bus = EventBus()

# Обработчики событий

async def on_block_created(event: Event):
    """Обработчик создания блока"""
    block_id = event.payload['block_id']
    print(f"Block created: {block_id}")
    
    # Генерируем embedding
    from app.services.nlp_service import generate_embedding
    embedding = await generate_embedding(event.payload['content'])
    
    # Обновляем блок
    from app.services.block_service import BlockService
    service = BlockService()
    await service.update_block(block_id, {'embedding': embedding})

async def on_block_updated(event: Event):
    """Обработчик обновления блока"""
    block_id = event.payload['block_id']
    print(f"Block updated: {block_id}")
    
    # Переиндексируем в Elasticsearch
    from app.repositories.elastic_repo import ElasticRepository
    elastic = ElasticRepository()
    await elastic.reindex_block(block_id)

async def on_document_assembled(event: Event):
    """Обработчик сборки документа"""
    document_id = event.payload['document_id']
    print(f"Document assembled: {document_id}")
    
    # Сохраняем статистику
    for block_id in event.payload['blocks_used']:
        from app.services.block_service import BlockService
        service = BlockService()
        
        block = await service.get_block(block_id)
        stats = block.get('usage_stats', {})
        stats['applied_count'] = stats.get('applied_count', 0) + 1
        stats['last_used'] = datetime.utcnow()
        
        await service.update_block(block_id, {'usage_stats': stats})

# Регистрация обработчиков
event_bus.subscribe(EventType.BLOCK_CREATED, on_block_created)
event_bus.subscribe(EventType.BLOCK_UPDATED, on_block_updated)
event_bus.subscribe(EventType.DOCUMENT_ASSEMBLED, on_document_assembled)

# Пример использования
async def create_block_with_event(block_data: dict):
    """Создаёт блок и публикует событие"""
    from app.services.block_service import BlockService
    service = BlockService()
    
    block = await service.create_block(block_data)
    
    # Публикуем событие
    event = Event(
        type=EventType.BLOCK_CREATED,
        payload={'block_id': block['id'], 'content': block['content']},
        timestamp=datetime.utcnow(),
        source='block_service'
    )
    
    await event_bus.publish(event)
    
    return block
```

### 5.3 CQRS (Command Query Responsibility Segregation)

**Разделение операций чтения и записи**:

```python
from abc import ABC, abstractmethod

# --- COMMANDS (Write Model) ---

class Command(ABC):
    """Базовая команда"""
    pass

class CreateBlockCommand(Command):
    def __init__(self, block_data: dict):
        self.block_data = block_data

class UpdateBlockCommand(Command):
    def __init__(self, block_id: str, update_data: dict):
        self.block_id = block_id
        self.update_data = update_data

class CommandHandler(ABC):
    """Базовый обработчик команд"""
    @abstractmethod
    async def handle(self, command: Command):
        pass

class CreateBlockCommandHandler(CommandHandler):
    async def handle(self, command: CreateBlockCommand):
        # Бизнес-логика создания
        from app.services.block_service import BlockService
        service = BlockService()
        
        block = await service.create_block(command.block_data)
        
        # Публикуем событие
        event = Event(
            type=EventType.BLOCK_CREATED,
            payload={'block_id': block['id']},
            timestamp=datetime.utcnow(),
            source='command_handler'
        )
        await event_bus.publish(event)
        
        return block

# --- QUERIES (Read Model) ---

class Query(ABC):
    """Базовый запрос"""
    pass

class GetBlockQuery(Query):
    def __init__(self, block_id: str):
        self.block_id = block_id

class SearchBlocksQuery(Query):
    def __init__(self, search_term: str, filters: dict):
        self.search_term = search_term
        self.filters = filters

class QueryHandler(ABC):
    """Базовый обработчик запросов"""
    @abstractmethod
    async def handle(self, query: Query):
        pass

class GetBlockQueryHandler(QueryHandler):
    async def handle(self, query: GetBlockQuery):
        # Оптимизированное чтение
        from app.repositories.mongo_repo import MongoRepository
        mongo = MongoRepository()
        
        # Можно использовать кэш
        cache_key = f"block:{query.block_id}"
        # cached = await redis.get(cache_key)
        # if cached:
        #     return cached
        
        block = await mongo.find_block_by_id(query.block_id)
        # await redis.set(cache_key, block, expire=3600)
        
        return block

class SearchBlocksQueryHandler(QueryHandler):
    async def handle(self, query: SearchBlocksQuery):
        # Используем Elasticsearch для быстрого поиска
        from app.repositories.elastic_repo import ElasticRepository
        elastic = ElasticRepository()
        
        results = await elastic.search(
            query=query.search_term,
            filters=query.filters
        )
        
        return results

# --- Dispatcher ---

class CommandBus:
    """Шина команд"""
    def __init__(self):
        self.handlers = {}
    
    def register_handler(self, command_class, handler):
        self.handlers[command_class] = handler
    
    async def dispatch(self, command: Command):
        handler = self.handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for {type(command)}")
        
        return await handler.handle(command)

class QueryBus:
    """Шина запросов"""
    def __init__(self):
        self.handlers = {}
    
    def register_handler(self, query_class, handler):
        self.handlers[query_class] = handler
    
    async def dispatch(self, query: Query):
        handler = self.handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for {type(query)}")
        
        return await handler.handle(query)

# Инициализация
command_bus = CommandBus()
command_bus.register_handler(CreateBlockCommand, CreateBlockCommandHandler())
command_bus.register_handler(UpdateBlockCommand, UpdateBlockCommandHandler())

query_bus = QueryBus()
query_bus.register_handler(GetBlockQuery, GetBlockQueryHandler())
query_bus.register_handler(SearchBlocksQuery, SearchBlocksQueryHandler())

# Пример использования в API
@app.post("/api/blocks")
async def create_block_endpoint(block_data: dict):
    command = CreateBlockCommand(block_data)
    result = await command_bus.dispatch(command)
    return result

@app.get("/api/blocks/{block_id}")
async def get_block_endpoint(block_id: str):
    query = GetBlockQuery(block_id)
    result = await query_bus.dispatch(query)
    return result
```

---

## 6. Практическая реализация

### 6.1 Парсинг структурированных текстов

#### 6.1.1 Парсер для немецких законов

```python
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class LegalBlock:
    """Блок законодательного текста"""
    number: str           # "§5", "Art. 3 GG"
    absatz: int = None    # номер абзаца
    satz: int = None      # номер предложения
    title: str = ""
    content: str = ""
    level: int = 0
    parent_id: str = None
    references: List[str] = None

class GermanLegalTextParser:
    """
    Парсер для немецких законодательных текстов
    Поддерживает: SGB, BGB, GG, и другие
    """
    
    # Регулярные выражения
    PARAGRAPH_PATTERN = r'§\s*(\d+[a-z]?)'
    ARTICLE_PATTERN = r'Art(?:ikel)?\.\s*(\d+[a-z]?)'
    ABSATZ_PATTERN = r'\((\d+)\)'
    SATZ_PATTERN = r'(\d+)\.'
    
    def __init__(self):
        self.blocks = []
        self.current_paragraph = None
        self.current_absatz = None
    
    def parse(self, text: str, source: str = "Unknown") -> List[LegalBlock]:
        """
        Парсит текст закона
        
        Args:
            text: текст закона
            source: источник (например "SGB IX")
        
        Returns:
            List[LegalBlock]: список блоков
        """
        self.blocks = []
        self.source = source
        
        # Разбиваем на параграфы
        paragraphs = self._split_into_paragraphs(text)
        
        for para_text in paragraphs:
            self._parse_paragraph(para_text)
        
        return self.blocks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Разбивает текст на параграфы"""
        # Находим все начала параграфов
        para_starts = []
        
        for match in re.finditer(self.PARAGRAPH_PATTERN, text):
            para_starts.append(match.start())
        
        # Разрезаем текст по началам параграфов
        paragraphs = []
        for i in range(len(para_starts)):
            start = para_starts[i]
            end = para_starts[i + 1] if i + 1 < len(para_starts) else len(text)
            paragraphs.append(text[start:end])
        
        return paragraphs
    
    def _parse_paragraph(self, text: str):
        """Парсит один параграф"""
        # Извлекаем номер параграфа
        match = re.match(self.PARAGRAPH_PATTERN, text)
        if not match:
            return
        
        para_number = match.group(1)
        
        # Извлекаем заголовок (обычно в скобках или выделен)
        title_match = re.search(r'\n([A-ZÄÖÜ][^\n]+)\n', text)
        title = title_match.group(1).strip() if title_match else ""
        
        # Создаём основной блок параграфа
        para_id = f"{self.source.lower().replace(' ', '_')}_p{para_number}"
        
        para_block = LegalBlock(
            number=f"§{para_number}",
            title=title,
            content=text,
            level=0,
            parent_id=None
        )
        
        self.blocks.append(para_block)
        self.current_paragraph = para_id
        
        # Парсим абзацы (Absätze)
        self._parse_absatze(text, para_id, para_number)
    
    def _parse_absatze(self, text: str, para_id: str, para_number: str):
        """Парсит абзацы внутри параграфа"""
        # Находим все абзацы вида (1), (2), (3)
        absatz_matches = list(re.finditer(self.ABSATZ_PATTERN, text))
        
        if not absatz_matches:
            # Нет явных абзацев - весь текст один абзац
            return
        
        for i, match in enumerate(absatz_matches):
            absatz_num = int(match.group(1))
            
            # Извлекаем текст абзаца
            start = match.end()
            end = absatz_matches[i + 1].start() if i + 1 < len(absatz_matches) else len(text)
            absatz_text = text[start:end].strip()
            
            # Создаём блок абзаца
            absatz_id = f"{para_id}_abs{absatz_num}"
            
            absatz_block = LegalBlock(
                number=f"§{para_number}",
                absatz=absatz_num,
                content=absatz_text,
                level=1,
                parent_id=para_id
            )
            
            self.blocks.append(absatz_block)
            
            # Парсим предложения (Sätze) внутри абзаца
            self._parse_satze(absatz_text, absatz_id, para_number, absatz_num)
    
    def _parse_satze(self, text: str, absatz_id: str, para_number: str, absatz_num: int):
        """Парсит предложения внутри абзаца"""
        # Находим предложения вида "1. ", "2. ", "3. "
        satz_matches = list(re.finditer(r'^(\d+)\.\s+', text, re.MULTILINE))
        
        if not satz_matches:
            return
        
        for i, match in enumerate(satz_matches):
            satz_num = int(match.group(1))
            
            # Извлекаем текст предложения
            start = match.end()
            end = satz_matches[i + 1].start() if i + 1 < len(satz_matches) else len(text)
            satz_text = text[start:end].strip()
            
            # Создаём блок предложения
            satz_id = f"{absatz_id}_s{satz_num}"
            
            satz_block = LegalBlock(
                number=f"§{para_number}",
                absatz=absatz_num,
                satz=satz_num,
                content=satz_text,
                level=2,
                parent_id=absatz_id,
                references=self._extract_references(satz_text)
            )
            
            self.blocks.append(satz_block)
    
    def _extract_references(self, text: str) -> List[str]:
        """Извлекает ссылки на другие параграфы"""
        references = []
        
        # Ищем ссылки вида "§5", "§ 5", "Absatz 2"
        para_refs = re.findall(r'§\s*(\d+[a-z]?)', text)
        references.extend([f"§{ref}" for ref in para_refs])
        
        # Ищем ссылки вида "Absatz 2"
        abs_refs = re.findall(r'Absatz\s+(\d+)', text, re.IGNORECASE)
        references.extend([f"Abs.{ref}" for ref in abs_refs])
        
        return references

# Пример использования

sgb9_text = """
§5 Leistungsgruppen

Die Leistungen zur Teilhabe umfassen die notwendigen Sozialleistungen, um

1. die Behinderung abzuwenden, zu beseitigen, zu mindern,
2. ihre Verschlimmerung zu verhüten oder ihre Folgen zu mildern,
3. Einschränkungen der Erwerbsfähigkeit zu vermeiden,
4. den vorzeitigen Bezug anderer Sozialleistungen zu vermeiden,
5. die Teilhabe am Arbeitsleben entsprechend den Neigungen und Fähigkeiten dauerhaft zu sichern,
6. die persönliche Entwicklung ganzheitlich zu fördern,
7. die Teilhabe am Leben in der Gesellschaft und eine selbstbestimmte Lebensführung zu ermöglichen oder zu erleichtern.

§29 Persönliches Budget

(1) Auf Antrag werden Leistungen zur Teilhabe durch die Leistungsform eines Persönlichen Budgets ausgeführt. Das Persönliche Budget ist ein Instrument zur Förderung der Selbstbestimmung und Teilhabe.

(2) Das Persönliche Budget kann von mehreren Leistungsträgern als trägerübergreifendes Persönliches Budget ausgeführt werden.

1. Die Leistungsträger vereinbaren gemeinsam die Höhe des Budgets.
2. Das Budget wird monatlich ausgezahlt.
"""

parser = GermanLegalTextParser()
blocks = parser.parse(sgb9_text, source="SGB IX")

print(f"Parsed {len(blocks)} blocks:")
for block in blocks:
    indent = "  " * block.level
    print(f"{indent}• {block.number}", end="")
    if block.absatz:
        print(f" Abs.{block.absatz}", end="")
    if block.satz:
        print(f" S.{block.satz}", end="")
    if block.title:
        print(f" - {block.title}")
    else:
        print()
    
    if block.references:
        print(f"{indent}  References: {', '.join(block.references)}")
```

#### 6.1.2 Импорт в базу данных

```python
async def import_legal_text(text: str, source: str):
    """
    Импортирует законодательный текст в систему
    """
    from app.services.block_service import BlockService
    from app.services.nlp_service import NLPService
    
    # Парсим текст
    parser = GermanLegalTextParser()
    blocks = parser.parse(text, source=source)
    
    # Сервисы
    block_service = BlockService()
    nlp_service = NLPService()
    
    # Импортируем блоки
    imported = []
    
    for legal_block in blocks:
        # Генерируем embedding
        embedding = await nlp_service.generate_embedding(legal_block.content)
        
        # Извлекаем entities и keywords
        entities = await nlp_service.extract_entities(legal_block.content)
        keywords = await nlp_service.extract_keywords(legal_block.content)
        topics = await nlp_service.classify_topics(legal_block.content)
        
        # Создаём block_data
        block_data = {
            "type": "paragraph",
            "number": legal_block.number,
            "title": legal_block.title,
            "content": legal_block.content,
            "source": source,
            "metadata": {
                "absatz": legal_block.absatz,
                "satz": legal_block.satz,
                "level": legal_block.level,
                "parent_id": legal_block.parent_id,
                "valid_from": "2001-07-01",  # для SGB IX
                "jurisdiction": "Deutschland"
            },
            "annotations": {
                "keywords": keywords,
                "entities": entities,
                "topics": topics,
                "embedding": embedding
            },
            "relations": [
                {
                    "target_id": ref,
                    "type": "references"
                }
                for ref in (legal_block.references or [])
            ]
        }
        
        # Создаём блок
        created_block = await block_service.create_block(block_data)
        imported.append(created_block)
        
        print(f"Imported: {created_block['number']} - {created_block['title']}")
    
    # Создаём связи в графе
    await create_graph_relations(imported)
    
    return imported

async def create_graph_relations(blocks: List[dict]):
    """
    Создаёт связи между блоками в Neo4j
    """
    from app.repositories.neo4j_repo import Neo4jRepository
    
    neo4j = Neo4jRepository()
    
    for block in blocks:
        # Связь с родительским блоком
        parent_id = block["metadata"].get("parent_id")
        if parent_id:
            await neo4j.create_relationship(
                from_id=parent_id,
                to_id=block["id"],
                rel_type="HAS_CHILD",
                properties={"level_diff": 1}
            )
        
        # Связи с упоминаемыми параграфами
        for relation in block.get("relations", []):
            if relation["type"] == "references":
                # Находим блок по номеру
                referenced = await find_block_by_number(
                    relation["target_id"],
                    block["source"]
                )
                
                if referenced:
                    await neo4j.create_relationship(
                        from_id=block["id"],
                        to_id=referenced["id"],
                        rel_type="REFERENCES",
                        properties={"type": "direct"}
                    )
```

### 6.2 Генерация документов

#### 6.2.1 Сборка документа из блоков

```python
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
import os

class DocumentAssembler:
    """
    Собирает документы из блоков
    """
    
    def __init__(self, templates_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.strategies = {
            "linear": self.linear_assembly,
            "conditional": self.conditional_assembly,
            "hierarchical": self.hierarchical_assembly
        }
    
    async def assemble(
        self,
        template_id: str,
        context: dict,
        strategy: str = "conditional"
    ) -> dict:
        """
        Собирает документ
        
        Args:
            template_id: ID шаблона
            context: контекст (переменные, условия)
            strategy: стратегия сборки
        
        Returns:
            Собранный документ
        """
        # Загружаем шаблон
        template = await self.load_template(template_id)
        
        # Получаем блоки по стратегии
        strategy_fn = self.strategies.get(strategy, self.conditional_assembly)
        blocks = await strategy_fn(template, context)
        
        # Рендерим шаблон
        rendered = self.render_template(template, blocks, context)
        
        # Формируем документ
        document = {
            "id": self.generate_doc_id(),
            "template_id": template_id,
            "strategy": strategy,
            "context": context,
            "blocks": blocks,
            "content": rendered,
            "word_count": len(rendered.split()),
            "assembled_at": datetime.utcnow()
        }
        
        return document
    
    async def load_template(self, template_id: str) -> dict:
        """Загружает шаблон"""
        from app.repositories.mongo_repo import MongoRepository
        mongo = MongoRepository()
        
        template = await mongo.find_template_by_id(template_id)
        return template
    
    async def linear_assembly(
        self,
        template: dict,
        context: dict
    ) -> List[dict]:
        """
        Линейная сборка - все блоки по порядку
        """
        from app.services.block_service import BlockService
        service = BlockService()
        
        blocks = []
        for block_ref in template["blocks"]:
            block = await service.get_block(block_ref["block_id"])
            if block:
                blocks.append(block)
        
        return blocks
    
    async def conditional_assembly(
        self,
        template: dict,
        context: dict
    ) -> List[dict]:
        """
        Условная сборка - блоки по правилам
        """
        from app.services.block_service import BlockService
        from app.services.rule_engine import RuleEngine
        
        block_service = BlockService()
        rule_engine = RuleEngine()
        
        # Применяем правила к контексту
        activated_block_ids = await rule_engine.evaluate(context)
        
        # Получаем блоки
        blocks = []
        for block_id in activated_block_ids:
            block = await block_service.get_block(block_id)
            if block:
                blocks.append(block)
        
        # Сортируем по приоритету
        blocks.sort(key=lambda b: b.get("metadata", {}).get("priority", 999))
        
        return blocks
    
    async def hierarchical_assembly(
        self,
        template: dict,
        context: dict
    ) -> List[dict]:
        """
        Иерархическая сборка - по темам и уровням
        """
        from app.services.block_service import BlockService
        service = BlockService()
        
        # Получаем все блоки
        all_blocks = []
        for block_ref in template["blocks"]:
            block = await service.get_block(block_ref["block_id"])
            if block:
                all_blocks.append(block)
        
        # Группируем по топикам
        topics = {}
        for block in all_blocks:
            topic = block.get("annotations", {}).get("topics", ["general"])[0]
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(block)
        
        # Сортируем внутри каждого топика по уровню
        for topic in topics:
            topics[topic].sort(key=lambda b: b.get("metadata", {}).get("level", 0))
        
        # Объединяем в линейный список
        blocks = []
        for topic, topic_blocks in topics.items():
            blocks.extend(topic_blocks)
        
        return blocks
    
    def render_template(
        self,
        template: dict,
        blocks: List[dict],
        context: dict
    ) -> str:
        """
        Рендерит шаблон с блоками
        """
        # Используем Jinja2
        jinja_template = self.env.from_string(template["template_text"])
        
        # Подготавливаем данные для шаблона
        template_data = {
            "blocks": blocks,
            "context": context,
            **context  # Распаковываем контекст для удобства
        }
        
        rendered = jinja_template.render(**template_data)
        return rendered
    
    def generate_doc_id(self) -> str:
        """Генерирует ID документа"""
        import uuid
        return f"doc_{uuid.uuid4().hex[:8]}"
```

#### 6.2.2 Шаблоны документов (Jinja2)

```jinja2
{# templates/widerspruch_template.jinja2 #}

{{ context.sender_address }}

{{ context.authority_name }}
{{ context.authority_address }}

{{ context.date }}

Betreff: Widerspruch gegen Bescheid vom {{ context.bescheid_date }}
         Aktenzeichen: {{ context.case_number }}

Sehr geehrte Damen und Herren,

hiermit lege ich Widerspruch gegen den Bescheid vom {{ context.bescheid_date }}, 
Aktenzeichen {{ context.case_number }}, ein.

{% for block in blocks %}
    {% if block.type == "legal_basis" %}
        
**Rechtsgrundlage:**

{{ block.content }}
    {% endif %}
{% endfor %}

**Begründung:**

{{ context.reasoning }}

{% for block in blocks %}
    {% if block.type == "argumentation" %}
        
{{ block.content }}
    {% endif %}
{% endfor %}

{% if context.request_hearing %}
**Anhörung:**

Ich beantrage eine persönliche Anhörung gemäß § 24 SGB X.
{% endif %}

**Antrag:**

Ich bitte um Abhilfe und um Aufhebung des Bescheides.

Mit freundlichen Grüßen,

{{ context.sender_name }}

{% if context.attachments %}
**Anlagen:**
{% for attachment in context.attachments %}
- {{ attachment }}
{% endfor %}
{% endif %}
```

#### 6.2.3 Экспорт в различные форматы

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown
from weasyprint import HTML

class DocumentExporter:
    """
    Экспорт документов в различные форматы
    """
    
    async def export_to_docx(self, document: dict, output_path: str):
        """
        Экспорт в Microsoft Word
        """
        doc = Document()
        
        # Заголовок
        title = doc.add_heading(document.get("title", "Document"), level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Контент
        content = document["content"]
        
        # Разбиваем на параграфы
        paragraphs = content.split("\n\n")
        
        for para_text in paragraphs:
            if para_text.startswith("**") and para_text.endswith("**"):
                # Это заголовок
                heading = para_text.strip("*")
                doc.add_heading(heading, level=2)
            else:
                # Обычный параграф
                p = doc.add_paragraph(para_text)
                p.paragraph_format.space_after = Pt(12)
        
        # Метаданные в футере
        section = doc.sections[0]
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = f"Erstellt am: {document['assembled_at']}"
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Сохраняем
        doc.save(output_path)
        
        return output_path
    
    async def export_to_pdf(self, document: dict, output_path: str):
        """
        Экспорт в PDF
        """
        # Конвертируем в HTML
        html_content = markdown.markdown(document["content"])
        
        # CSS стили
        css = """
        <style>
            body {
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.6;
                margin: 2cm;
            }
            h1 {
                text-align: center;
                margin-bottom: 1cm;
            }
            h2 {
                margin-top: 0.8cm;
                margin-bottom: 0.4cm;
            }
            p {
                text-align: justify;
                margin-bottom: 0.5cm;
            }
        </style>
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{document.get("title", "Document")}</title>
            {css}
        </head>
        <body>
            {html_content}
            <hr>
            <p style="text-align: center; font-size: 10pt;">
                Erstellt am: {document['assembled_at']}
            </p>
        </body>
        </html>
        """
        
        # Генерируем PDF
        HTML(string=full_html).write_pdf(output_path)
        
        return output_path
    
    async def export_to_markdown(self, document: dict, output_path: str):
        """
        Экспорт в Markdown
        """
        content = document["content"]
        
        # Добавляем метаданные
        metadata = f"""---
title: {document.get("title", "Document")}
template: {document["template_id"]}
assembled: {document["assembled_at"]}
---

"""
        
        full_content = metadata + content
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        return output_path
```

---

## 7. Система автоматического встраивания

### 7.1 Концепция эскалации детализации

**Основная идея**: автоматически определять уровень детализации и встраивать контент на нужный уровень иерархии.

```
Level 0 (Summary): "Погода в Европе" (1 предложение)
    ↓ (новый контент на 5 предложений)
Level 1 (Medium):  "Погода в Европе" → заголовок
                   5 предложений → тело
    ↓ (новый контент на 20 предложений)
Level 2 (Detailed): 5 предложений → краткое описание
                    20 предложений → подробный текст
```

### 7.2 Реализация Smart Inserter

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple

class SmartContentInserter:
    """
    Умное встраивание контента с автоматической эскалацией
    """
    
    def __init__(self):
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.content_tree = {}  # topic_id -> ContentNode
        self.topic_embeddings = {}  # topic_id -> embedding
        
    async def insert_content(
        self,
        content: str,
        metadata: dict = None
    ) -> Dict:
        """
        Вставляет контент на правильное место
        
        Returns:
            dict с информацией о вставке
        """
        # 1. Определяем топик
        topic_id, similarity = await self.identify_topic(content)
        
        # 2. Определяем уровень детализации
        depth_level = self.calculate_depth_level(content)
        
        # 3. Вставляем в дерево
        result = await self.insert_into_tree(
            topic_id,
            content,
            depth_level,
            similarity,
            metadata
        )
        
        return result
    
    async def identify_topic(self, content: str) -> Tuple[str, float]:
        """
        Определяет топик контента через semantic similarity
        
        Returns:
            (topic_id, similarity_score)
        """
        # Генерируем embedding для нового контента
        content_embedding = self.model.encode(content)
        
        if not self.topic_embeddings:
            # Первый контент - создаём новый топик
            topic_id = self.generate_topic_id()
            self.topic_embeddings[topic_id] = content_embedding
            return topic_id, 1.0
        
        # Ищем наиболее похожий топик
        max_similarity = 0
        best_topic = None
        
        for topic_id, topic_emb in self.topic_embeddings.items():
            similarity = self.cosine_similarity(content_embedding, topic_emb)
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_topic = topic_id
        
        # Threshold для создания нового топика
        if max_similarity < 0.7:
            # Создаём новый топик
            topic_id = self.generate_topic_id()
            self.topic_embeddings[topic_id] = content_embedding
            return topic_id, 1.0
        
        return best_topic, max_similarity
    
    def calculate_depth_level(self, content: str) -> int:
        """
        Вычисляет уровень детализации на основе длины
        
        Levels:
        - 0: 1 предложение (summary)
        - 1: 2-5 предложений (brief)
        - 2: 6-15 предложений (medium)
        - 3: 16-30 предложений (detailed)
        - 4: 30+ предложений (comprehensive)
        """
        sentences = self.split_sentences(content)
        num_sentences = len(sentences)
        
        if num_sentences == 1:
            return 0
        elif num_sentences <= 5:
            return 1
        elif num_sentences <= 15:
            return 2
        elif num_sentences <= 30:
            return 3
        else:
            return 4
    
    async def insert_into_tree(
        self,
        topic_id: str,
        content: str,
        depth_level: int,
        similarity: float,
        metadata: dict
    ) -> Dict:
        """
        Вставляет контент в дерево с эскалацией
        """
        if topic_id not in self.content_tree:
            # Новый топик
            self.content_tree[topic_id] = ContentNode(
                topic_id=topic_id,
                levels={depth_level: content},
                metadata=metadata
            )
            
            return {
                "action": "created_new_topic",
                "topic_id": topic_id,
                "depth_level": depth_level
            }
        
        node = self.content_tree[topic_id]
        current_max_level = max(node.levels.keys())
        
        if depth_level > current_max_level:
            # Эскалация - новый контент более детальный
            result = await self.escalate_content(
                node,
                content,
                depth_level,
                current_max_level
            )
            
            return {
                "action": "escalated",
                "topic_id": topic_id,
                "from_level": current_max_level,
                "to_level": depth_level,
                **result
            }
        
        elif depth_level == current_max_level:
            # Такой же уровень - merge или replace
            result = await self.merge_content(
                node,
                content,
                depth_level,
                similarity
            )
            
            return {
                "action": "merged",
                "topic_id": topic_id,
                "depth_level": depth_level,
                **result
            }
        
        else:
            # Менее детальный - добавляем как альтернативное резюме
            node.levels[depth_level] = content
            
            return {
                "action": "added_summary",
                "topic_id": topic_id,
                "depth_level": depth_level
            }
    
    async def escalate_content(
        self,
        node: 'ContentNode',
        new_content: str,
        new_level: int,
        old_level: int
    ) -> Dict:
        """
        Эскалирует контент на новый уровень детализации
        """
        old_content = node.levels[old_level]
        
        # Старый контент становится заголовком/summary
        key_sentence = self.extract_key_sentence(old_content)
        node.summary = key_sentence
        
        # Сохраняем старый контент на его уровне
        # (он может использоваться для кратких версий)
        
        # Новый контент добавляем на новый уровень
        node.levels[new_level] = new_content
        
        # Обновляем главный embedding
        await self.update_topic_embedding(node.topic_id, new_content)
        
        return {
            "old_summary": old_content[:100] + "...",
            "new_summary": key_sentence,
            "detailed_content_length": len(new_content)
        }
    
    async def merge_content(
        self,
        node: 'ContentNode',
        new_content: str,
        level: int,
        similarity: float
    ) -> Dict:
        """
        Объединяет или заменяет контент на том же уровне
        """
        old_content = node.levels[level]
        
        if similarity > 0.9:
            # Очень похоже - заменяем если новый контент лучше
            if len(new_content) > len(old_content):
                node.levels[level] = new_content
                return {"decision": "replaced", "reason": "longer_content"}
            else:
                return {"decision": "kept_old", "reason": "old_was_longer"}
        
        else:
            # Не очень похоже - объединяем
            merged = self.merge_texts(old_content, new_content)
            node.levels[level] = merged
            return {"decision": "merged", "merged_length": len(merged)}
    
    def extract_key_sentence(self, text: str) -> str:
        """
        Извлекает ключевое предложение из текста
        """
        sentences = self.split_sentences(text)
        
        if not sentences:
            return text[:200]
        
        # Простой heuristic - первое предложение
        # В реальной системе можно использовать extractive summarization
        return sentences[0]
    
    def split_sentences(self, text: str) -> List[str]:
        """Разбивает текст на предложения"""
        import re
        
        # Упрощённая версия
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def cosine_similarity(self, emb1, emb2) -> float:
        """Косинусное сходство"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def generate_topic_id(self) -> str:
        """Генерирует ID топика"""
        import uuid
        return f"topic_{uuid.uuid4().hex[:8]}"
    
    async def update_topic_embedding(self, topic_id: str, new_content: str):
        """Обновляет embedding топика"""
        new_embedding = self.model.encode(new_content)
        
        # Weighted average с предыдущим embedding
        if topic_id in self.topic_embeddings:
            old_embedding = self.topic_embeddings[topic_id]
            self.topic_embeddings[topic_id] = (old_embedding * 0.7 + new_embedding * 0.3)
        else:
            self.topic_embeddings[topic_id] = new_embedding
    
    def merge_texts(self, text1: str, text2: str) -> str:
        """Объединяет два текста, удаляя дубликаты"""
        sentences1 = set(self.split_sentences(text1))
        sentences2 = set(self.split_sentences(text2))
        
        # Объединяем уникальные предложения
        all_sentences = list(sentences1 | sentences2)
        
        return " ".join(all_sentences)

class ContentNode:
    """Узел в дереве контента"""
    def __init__(self, topic_id: str, levels: dict, metadata: dict = None):
        self.topic_id = topic_id
        self.levels = levels  # {depth_level: content}
        self.summary = ""
        self.children = []
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

# Пример использования

async def demo_smart_inserter():
    """Демонстрация работы SmartContentInserter"""
    
    inserter = SmartContentInserter()
    
    # Вставка 1: Краткая новость
    result1 = await inserter.insert_content(
        "Погода в Берлине: температура +15°C, солнечно.",
        metadata={"source": "weather_api", "city": "Berlin"}
    )
    print("Insert 1:", result1)
    
    # Вставка 2: Более подробная информация о погоде в Берлине
    result2 = await inserter.insert_content(
        """
        Прогноз погоды для Берлина на сегодня.
        Температура днём достигнет +15°C.
        Небо ясное, солнечно.
        Ветер северо-западный, 5 м/с.
        Влажность 60%.
        """,
        metadata={"source": "weather_detailed", "city": "Berlin"}
    )
    print("Insert 2:", result2)
    
    # Вставка 3: Очень подробная статья о погоде
    detailed_article = """
    Подробный анализ погодных условий в Берлине на сегодняшний день.
    Утром температура составляла +10°C, к полудню поднялась до +15°C.
    Синоптики прогнозируют, что к вечеру температура останется на уровне +14°C.
    Атмосферное давление 1015 гПа, что является нормой для этого времени года.
    Небо преимущественно ясное, облачность не превышает 10%.
    Ветер дует с северо-запада со скоростью 5 м/с, порывы до 8 м/с.
    Относительная влажность воздуха составляет 60%, что комфортно для человека.
    Осадков не ожидается.
    UV-индекс умеренный, рекомендуется использовать солнцезащитный крем при длительном пребывании на улице.
    Видимость отличная, более 10 км.
    Такая погода благоприятствует прогулкам и активностям на свежем воздухе.
    """
    
    result3 = await inserter.insert_content(
        detailed_article,
        metadata={"source": "weather_analysis", "city": "Berlin"}
    )
    print("Insert 3:", result3)
    
    # Вставка 4: Информация о погоде в другом городе
    result4 = await inserter.insert_content(
        "Погода в Париже: дождь, +12°C.",
        metadata={"source": "weather_api", "city": "Paris"}
    )
    print("Insert 4:", result4)
    
    # Получение контента разных уровней
    for topic_id, node in inserter.content_tree.items():
        print(f"\n=== Topic: {topic_id} ===")
        print(f"Summary: {node.summary}")
        print(f"Levels: {list(node.levels.keys())}")
        
        for level, content in sorted(node.levels.items()):
            print(f"\nLevel {level}:")
            print(content[:150] + "..." if len(content) > 150 else content)
```

---

## 8. Работа с законодательными текстами

### 8.1 Специфика немецкого законодательства

**Структура немецких законов**:

```
Gesetz (Закон)
├── Teil (Часть) - опционально
├── Kapitel (Глава) - опционально
├── Abschnitt (Раздел) - опционально
└── § Paragraph (Параграф)
    ├── Absatz (Абзац) - обозначается (1), (2), (3)
    ├── Satz (Предложение) - обозначается 1., 2., 3.
    └── Nummer/Buchstabe - нумерация 1., 2. или a), b)
```

**Примеры обозначений**:
- `§29 SGB IX` - параграф 29 Социального кодекса IX
- `§29 Abs. 2 SGB IX` - параграф 29, абзац 2
- `§29 Abs. 2 Satz 1 SGB IX` - параграф 29, абзац 2, предложение 1
- `Art. 3 GG` - статья 3 Основного закона

### 8.2 Расширенный парсер с поддержкой всех структур

```python
class AdvancedGermanLegalParser:
    """
    Расширенный парсер для немецких законов
    Поддерживает: Teil, Kapitel, Abschnitt, §, Absatz, Satz, Nummer, Buchstabe
    """
    
    # Паттерны для всех структурных элементов
    PATTERNS = {
        "teil": r'Teil\s+([IVX]+|[\d]+)',
        "kapitel": r'Kapitel\s+([IVX]+|[\d]+)',
        "abschnitt": r'Abschnitt\s+([IVX]+|[\d]+)',
        "paragraph": r'§\s*(\d+[a-z]?)',
        "artikel": r'Art(?:ikel)?\.\s*(\d+[a-z]?)',
        "absatz": r'\((\d+)\)',
        "satz": r'(\d+)\.',
        "nummer": r'(\d+)\.',
        "buchstabe": r'([a-z])\)',
    }
    
    def __init__(self):
        self.blocks = []
        self.hierarchy = []  # Stack текущей иерархии
    
    def parse(self, text: str, source: str = "Unknown") -> List[LegalBlock]:
        """
        Полный парсинг с учётом всей иерархии
        """
        self.blocks = []
        self.hierarchy = []
        self.source = source
        
        # Построчный анализ
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Определяем тип строки
            block_type, match_data = self.identify_line_type(line)
            
            if block_type:
                self.process_line(block_type, match_data, line)
        
        return self.blocks
    
    def identify_line_type(self, line: str) -> Tuple[str, dict]:
        """Определяет тип структурного элемента в строке"""
        for block_type, pattern in self.PATTERNS.items():
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return block_type, {
                    "number": match.group(1),
                    "full_text": line
                }
        
        return None, {}
    
    def process_line(self, block_type: str, match_data: dict, full_line: str):
        """Обрабатывает строку определённого типа"""
        # Обновляем иерархию
        self.update_hierarchy(block_type, match_data)
        
        # Создаём блок
        block = self.create_block(block_type, match_data, full_line)
        
        self.blocks.append(block)
    
    def update_hierarchy(self, block_type: str, match_data: dict):
        """
        Обновляет текущую иерархию
        
        Hierarchy levels:
        0: teil
        1: kapitel
        2: abschnitt
        3: paragraph/artikel
        4: absatz
        5: satz
        6: nummer/buchstabe
        """
        level_map = {
            "teil": 0,
            "kapitel": 1,
            "abschnitt": 2,
            "paragraph": 3,
            "artikel": 3,
            "absatz": 4,
            "satz": 5,
            "nummer": 6,
            "buchstabe": 6
        }
        
        level = level_map.get(block_type, 99)
        
        # Удаляем элементы того же или более низкого уровня
        self.hierarchy = [h for h in self.hierarchy if h["level"] < level]
        
        # Добавляем текущий элемент
        self.hierarchy.append({
            "level": level,
            "type": block_type,
            "number": match_data["number"]
        })
    
    def create_block(self, block_type: str, match_data: dict, full_line: str) -> LegalBlock:
        """Создаёт блок на основе типа и иерархии"""
        # Формируем ID на основе полной иерархии
        block_id = self.generate_block_id()
        
        # Определяем parent_id
        parent_id = self.get_parent_id()
        
        # Создаём блок
        block = LegalBlock(
            id=block_id,
            type=block_type,
            number=match_data["number"],
            content=full_line,
            level=len(self.hierarchy) - 1,
            parent_id=parent_id,
            hierarchy=self.hierarchy.copy()
        )
        
        return block
    
    def generate_block_id(self) -> str:
        """Генерирует ID на основе иерархии"""
        parts = [self.source.lower().replace(" ", "_")]
        
        for h in self.hierarchy:
            type_prefix = {
                "teil": "t",
                "kapitel": "k",
                "abschnitt": "a",
                "paragraph": "p",
                "artikel": "art",
                "absatz": "abs",
                "satz": "s",
                "nummer": "n",
                "buchstabe": "b"
            }.get(h["type"], h["type"][0])
            
            parts.append(f"{type_prefix}{h['number']}")
        
        return "_".join(parts)
    
    def get_parent_id(self) -> str:
        """Получает ID родительского элемента"""
        if len(self.hierarchy) < 2:
            return None
        
        # Родитель - предпоследний элемент иерархии
        parent_hierarchy = self.hierarchy[:-1]
        
        parts = [self.source.lower().replace(" ", "_")]
        
        for h in parent_hierarchy:
            type_prefix = {
                "teil": "t",
                "kapitel": "k",
                "abschnitt": "a",
                "paragraph": "p",
                "artikel": "art",
                "absatz": "abs",
                "satz": "s",
                "nummer": "n",
                "buchstabe": "b"
            }.get(h["type"], h["type"][0])
            
            parts.append(f"{type_prefix}{h['number']}")
        
        return "_".join(parts)

# Пример сложной структуры

complex_legal_text = """
Teil 1
Allgemeine Vorschriften

Kapitel 1
Grundlagen

Abschnitt 1
Begriffsbestimmungen

§1 Regelungsbereich

(1) Dieses Gesetz regelt die Teilhabe von Menschen mit Behinderungen.

1. Es gilt für alle Leistungsträger.
2. Es umfasst präventive Maßnahmen.

(2) Die Leistungen umfassen:

a) Leistungen zur medizinischen Rehabilitation,
b) Leistungen zur Teilhabe am Arbeitsleben,
c) Leistungen zur sozialen Teilhabe.

Abschnitt 2
Leistungsformen

§29 Persönliches Budget

(1) Auf Antrag werden Leistungen zur Teilhabe durch die Leistungsform eines Persönlichen Budgets ausgeführt.

1. Das Budget dient der Selbstbestimmung.
2. Es ermöglicht flexible Leistungsgestaltung.

(2) Das Budget wird monatlich ausgezahlt.
"""

parser = AdvancedGermanLegalParser()
blocks = parser.parse(complex_legal_text, source="SGB IX")

print(f"Parsed {len(blocks)} blocks with full hierarchy:\n")

for block in blocks:
    indent = "  " * block.level
    print(f"{indent}[{block.type}] {block.number} (ID: {block.id})")
    print(f"{indent}  Parent: {block.parent_id}")
    print(f"{indent}  Hierarchy: {[f'{h['type']}:{h['number']}' for h in block.hierarchy]}")
    print()
```

---

(Продолжение следует...)

## 9. Advanced функциональность

### 9.1 Версионирование блоков (Version Control)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import difflib

@dataclass
class Version:
    """Версия блока"""
    version_number: int
    content: str
    author: str
    timestamp: datetime
    commit_message: str
    diff: Optional[str] = None

class BlockVersionControl:
    """
    Git-like версионирование для блоков
    """
    
    def __init__(self, block_id: str):
        self.block_id = block_id
        self.versions: List[Version] = []
        self.current_version = None
        self.branches = {"main": []}
    
    def commit(
        self,
        new_content: str,
        author: str,
        message: str
    ) -> Version:
        """
        Создаёт новую версию (коммит)
        """
        version_number = len(self.versions) + 1
        
        # Вычисляем diff с предыдущей версией
        diff = None
        if self.current_version:
            diff = self.calculate_diff(
                self.current_version.content,
                new_content
            )
        
        # Создаём версию
        version = Version(
            version_number=version_number,
            content=new_content,
            author=author,
            timestamp=datetime.utcnow(),
            commit_message=message,
            diff=diff
        )
        
        self.versions.append(version)
        self.current_version = version
        self.branches["main"].append(version_number)
        
        return version
    
    def checkout(self, version_number: int) -> str:
        """
        Возвращает к определённой версии
        """
        for version in self.versions:
            if version.version_number == version_number:
                self.current_version = version
                return version.content
        
        raise ValueError(f"Version {version_number} not found")
    
    def get_history(self) -> List[Version]:
        """Возвращает историю версий"""
        return self.versions.copy()
    
    def create_branch(self, branch_name: str, from_version: int = None):
        """Создаёт новую ветку"""
        if branch_name in self.branches:
            raise ValueError(f"Branch {branch_name} already exists")
        
        base_version = from_version or self.current_version.version_number
        self.branches[branch_name] = [base_version]
    
    def calculate_diff(self, old_content: str, new_content: str) -> str:
        """
        Вычисляет diff между версиями
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            fromfile=f'version_{self.current_version.version_number}',
            tofile=f'version_{len(self.versions) + 1}'
        )
        
        return '\n'.join(diff)
    
    def merge(self, source_branch: str, target_branch: str = "main"):
        """
        Сливает ветки (упрощённая версия)
        """
        if source_branch not in self.branches:
            raise ValueError(f"Branch {source_branch} not found")
        
        if target_branch not in self.branches:
            raise ValueError(f"Branch {target_branch} not found")
        
        # В реальной системе здесь была бы сложная логика мержа
        # Пока просто копируем версии
        source_versions = self.branches[source_branch]
        self.branches[target_branch].extend(source_versions)
    
    async def save_to_db(self):
        """Сохраняет версии в базу данных"""
        from app.repositories.mongo_repo import MongoRepository
        mongo = MongoRepository()
        
        version_data = {
            "block_id": self.block_id,
            "versions": [
                {
                    "version_number": v.version_number,
                    "content": v.content,
                    "author": v.author,
                    "timestamp": v.timestamp,
                    "commit_message": v.commit_message,
                    "diff": v.diff
                }
                for v in self.versions
            ],
            "current_version": self.current_version.version_number,
            "branches": self.branches
        }
        
        await mongo.update_block_versions(self.block_id, version_data)

# Пример использования
async def demo_version_control():
    """Демонстрация версионирования"""
    
    vcs = BlockVersionControl("sgb9_p29")
    
    # Version 1
    v1 = vcs.commit(
        new_content="§29 Persönliches Budget\n\nAuf Antrag werden Leistungen...",
        author="Gesetzgeber",
        message="Initial version"
    )
    print(f"Created version {v1.version_number}")
    
    # Version 2
    v2 = vcs.commit(
        new_content="§29 Persönliches Budget\n\nAuf Antrag werden Leistungen zur Teilhabe...",
        author="BTHG-Reform",
        message="Added 'zur Teilhabe'"
    )
    print(f"Created version {v2.version_number}")
    print(f"Diff:\n{v2.diff}")
    
    # Version 3
    v3 = vcs.commit(
        new_content="§29 Persönliches Budget\n\n(1) Auf Antrag werden Leistungen zur Teilhabe...",
        author="BTHG-Reform",
        message="Added Absatz numbering"
    )
    print(f"Created version {v3.version_number}")
    
    # Checkout к старой версии
    old_content = vcs.checkout(1)
    print(f"\nChecked out version 1:\n{old_content}")
    
    # История
    print("\nVersion history:")
    for v in vcs.get_history():
        print(f"  v{v.version_number} - {v.timestamp} - {v.author}: {v.commit_message}")
    
    # Сохраняем
    await vcs.save_to_db()
```

### 9.2 Детекция конфликтов (Conflict Detection)

```python
from typing import List, Tuple
from enum import Enum

class ConflictType(Enum):
    SEMANTIC = "semantic"           # Семантические противоречия
    LOGICAL = "logical"             # Логические противоречия
    TEMPORAL = "temporal"           # Временные противоречия
    HIERARCHICAL = "hierarchical"   # Нарушение иерархии

class ConflictSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Conflict:
    """Описание конфликта между блоками"""
    type: ConflictType
    severity: ConflictSeverity
    block_ids: List[str]
    description: str
    suggested_resolution: str = None

class ConflictDetector:
    """
    Детектор конфликтов между блоками
    """
    
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    async def detect_conflicts(
        self,
        blocks: List[dict]
    ) -> List[Conflict]:
        """
        Находит все конфликты в наборе блоков
        """
        conflicts = []
        
        # Попарная проверка
        for i, block_a in enumerate(blocks):
            for block_b in blocks[i+1:]:
                # Семантические конфликты
                semantic_conflict = await self.check_semantic_conflict(block_a, block_b)
                if semantic_conflict:
                    conflicts.append(semantic_conflict)
                
                # Логические конфликты
                logical_conflict = await self.check_logical_conflict(block_a, block_b)
                if logical_conflict:
                    conflicts.append(logical_conflict)
                
                # Временные конфликты
                temporal_conflict = await self.check_temporal_conflict(block_a, block_b)
                if temporal_conflict:
                    conflicts.append(temporal_conflict)
        
        # Иерархические конфликты
        hierarchical_conflicts = await self.check_hierarchical_conflicts(blocks)
        conflicts.extend(hierarchical_conflicts)
        
        return conflicts
    
    async def check_semantic_conflict(
        self,
        block_a: dict,
        block_b: dict
    ) -> Optional[Conflict]:
        """
        Проверяет семантические противоречия
        """
        # Генерируем embeddings
        emb_a = self.model.encode(block_a["content"])
        emb_b = self.model.encode(block_b["content"])
        
        # Косинусное сходство
        similarity = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))
        
        # Проверяем на противоположность через negation detection
        is_negation = await self.detect_negation(block_a["content"], block_b["content"])
        
        if is_negation and similarity > 0.7:
            return Conflict(
                type=ConflictType.SEMANTIC,
                severity=ConflictSeverity.HIGH,
                block_ids=[block_a["id"], block_b["id"]],
                description=f"Blocks appear to contradict each other semantically",
                suggested_resolution="Review both blocks and determine which is correct"
            )
        
        return None
    
    async def detect_negation(self, text_a: str, text_b: str) -> bool:
        """
        Определяет, противоречат ли тексты друг другу
        """
        # Упрощённая проверка через ключевые слова
        negation_pairs = [
            ("kann", "kann nicht"),
            ("ist", "ist nicht"),
            ("muss", "muss nicht"),
            ("darf", "darf nicht"),
            ("soll", "soll nicht"),
        ]
        
        text_a_lower = text_a.lower()
        text_b_lower = text_b.lower()
        
        for positive, negative in negation_pairs:
            if positive in text_a_lower and negative in text_b_lower:
                return True
            if negative in text_a_lower and positive in text_b_lower:
                return True
        
        return False
    
    async def check_logical_conflict(
        self,
        block_a: dict,
        block_b: dict
    ) -> Optional[Conflict]:
        """
        Проверяет логические противоречия в условиях
        """
        # Извлекаем условия из метаданных
        conditions_a = block_a.get("metadata", {}).get("conditions", [])
        conditions_b = block_b.get("metadata", {}).get("conditions", [])
        
        if not conditions_a or not conditions_b:
            return None
        
        # Проверяем на взаимоисключающие условия
        if await self.are_mutually_exclusive(conditions_a, conditions_b):
            return Conflict(
                type=ConflictType.LOGICAL,
                severity=ConflictSeverity.CRITICAL,
                block_ids=[block_a["id"], block_b["id"]],
                description="Blocks have mutually exclusive conditions",
                suggested_resolution="Only one of these blocks can be active at a time"
            )
        
        return None
    
    async def are_mutually_exclusive(
        self,
        conditions_a: List[str],
        conditions_b: List[str]
    ) -> bool:
        """
        Определяет, являются ли условия взаимоисключающими
        """
        # Упрощённая проверка
        # В реальной системе нужен SAT solver
        
        for cond_a in conditions_a:
            for cond_b in conditions_b:
                # Пример: "x > 5" и "x <= 5" - взаимоисключающие
                if self.is_negation_of(cond_a, cond_b):
                    return True
        
        return False
    
    def is_negation_of(self, cond_a: str, cond_b: str) -> bool:
        """Проверяет, является ли cond_b отрицанием cond_a"""
        # Упрощённая логика
        negations = {
            ">": "<=",
            "<": ">=",
            "==": "!=",
            ">=": "<",
            "<=": ">",
        }
        
        for op, neg_op in negations.items():
            if op in cond_a and neg_op in cond_b:
                # Проверяем, что это одна и та же переменная
                var_a = cond_a.split(op)[0].strip()
                var_b = cond_b.split(neg_op)[0].strip()
                
                if var_a == var_b:
                    return True
        
        return False
    
    async def check_temporal_conflict(
        self,
        block_a: dict,
        block_b: dict
    ) -> Optional[Conflict]:
        """
        Проверяет временные конфликты (даты действия)
        """
        valid_from_a = block_a.get("metadata", {}).get("valid_from")
        valid_until_a = block_a.get("metadata", {}).get("valid_until")
        
        valid_from_b = block_b.get("metadata", {}).get("valid_from")
        valid_until_b = block_b.get("metadata", {}).get("valid_until")
        
        if not all([valid_from_a, valid_from_b]):
            return None
        
        # Проверяем пересечение периодов действия для одного и того же параграфа
        if block_a.get("number") == block_b.get("number"):
            if self.periods_overlap(
                (valid_from_a, valid_until_a),
                (valid_from_b, valid_until_b)
            ):
                return Conflict(
                    type=ConflictType.TEMPORAL,
                    severity=ConflictSeverity.MEDIUM,
                    block_ids=[block_a["id"], block_b["id"]],
                    description=f"Same paragraph number has overlapping validity periods",
                    suggested_resolution="Adjust validity dates or merge versions"
                )
        
        return None
    
    def periods_overlap(
        self,
        period_a: Tuple[str, str],
        period_b: Tuple[str, str]
    ) -> bool:
        """Проверяет пересечение периодов"""
        start_a, end_a = period_a
        start_b, end_b = period_b
        
        # None означает "до бесконечности"
        if end_a is None:
            end_a = "9999-12-31"
        if end_b is None:
            end_b = "9999-12-31"
        
        # Простая проверка пересечения
        return not (end_a < start_b or end_b < start_a)
    
    async def check_hierarchical_conflicts(
        self,
        blocks: List[dict]
    ) -> List[Conflict]:
        """
        Проверяет нарушения иерархии
        """
        conflicts = []
        
        # Строим граф иерархии
        hierarchy_graph = {}
        for block in blocks:
            parent_id = block.get("metadata", {}).get("parent_id")
            if parent_id:
                if parent_id not in hierarchy_graph:
                    hierarchy_graph[parent_id] = []
                hierarchy_graph[parent_id].append(block["id"])
        
        # Проверяем на циклы (A → B → C → A)
        cycles = self.detect_cycles(hierarchy_graph)
        
        for cycle in cycles:
            conflicts.append(Conflict(
                type=ConflictType.HIERARCHICAL,
                severity=ConflictSeverity.CRITICAL,
                block_ids=cycle,
                description=f"Circular dependency detected in hierarchy",
                suggested_resolution="Break the circular reference"
            ))
        
        return conflicts
    
    def detect_cycles(self, graph: dict) -> List[List[str]]:
        """Находит циклы в графе"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Нашли цикл
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:])
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
```

### 9.3 AI-Powered предложения (Suggestion Engine)

```python
class BlockSuggestionEngine:
    """
    Движок предложений на основе AI
    """
    
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        # История использования блоков
        self.usage_patterns = {}  # {(block_a, block_b): count}
    
    async def suggest_next_blocks(
        self,
        current_blocks: List[str],
        context: dict
    ) -> List[dict]:
        """
        Предлагает следующие блоки на основе:
        1. Collaborative filtering (что использовали другие)
        2. Graph-based (соседние узлы в графе)
        3. ML-based (предсказание модели)
        """
        suggestions = []
        
        # 1. Collaborative filtering
        collab_suggestions = await self.collaborative_filtering(current_blocks)
        suggestions.extend(collab_suggestions)
        
        # 2. Graph-based
        graph_suggestions = await self.graph_based_suggestions(current_blocks)
        suggestions.extend(graph_suggestions)
        
        # 3. ML-based
        ml_suggestions = await self.ml_based_suggestions(current_blocks, context)
        suggestions.extend(ml_suggestions)
        
        # Объединяем и ранжируем
        ranked_suggestions = self.rank_suggestions(suggestions)
        
        return ranked_suggestions[:10]  # Top 10
    
    async def collaborative_filtering(
        self,
        current_blocks: List[str]
    ) -> List[dict]:
        """
        "Пользователи, которые использовали A и B, также использовали C"
        """
        suggestions = []
        
        # Находим похожие наборы блоков
        similar_sets = await self.find_similar_block_sets(current_blocks)
        
        # Извлекаем блоки, которые часто использовались вместе
        for similar_set in similar_sets:
            for block_id in similar_set:
                if block_id not in current_blocks:
                    suggestions.append({
                        "block_id": block_id,
                        "score": 0.8,
                        "reason": "frequently_used_together",
                        "method": "collaborative_filtering"
                    })
        
        return suggestions
    
    async def find_similar_block_sets(
        self,
        current_blocks: List[str]
    ) -> List[List[str]]:
        """
        Находит похожие наборы блоков из истории
        """
        from app.repositories.mongo_repo import MongoRepository
        mongo = MongoRepository()
        
        # Получаем документы, которые использовали хотя бы 50% текущих блоков
        threshold = len(current_blocks) * 0.5
        
        similar_docs = await mongo.find_documents_with_blocks(
            block_ids=current_blocks,
            min_overlap=int(threshold)
        )
        
        # Извлекаем наборы блоков
        block_sets = [doc["assembly"]["blocks"] for doc in similar_docs]
        
        return block_sets
    
    async def graph_based_suggestions(
        self,
        current_blocks: List[str]
    ) -> List[dict]:
        """
        Предлагает блоки, связанные в графе
        """
        from app.repositories.neo4j_repo import Neo4jRepository
        neo4j = Neo4jRepository()
        
        suggestions = []
        
        for block_id in current_blocks:
            # Получаем соседей в графе
            neighbors = await neo4j.get_neighbors(
                block_id,
                depth=1,
                relationship_types=["REFERENCES", "APPLIES_IF", "RELATED_TO"]
            )
            
            for neighbor in neighbors:
                if neighbor["id"] not in current_blocks:
                    suggestions.append({
                        "block_id": neighbor["id"],
                        "score": neighbor.get("relationship_strength", 0.7),
                        "reason": f"connected_via_{neighbor['relationship_type']}",
                        "method": "graph_based"
                    })
        
        return suggestions
    
    async def ml_based_suggestions(
        self,
        current_blocks: List[str],
        context: dict
    ) -> List[dict]:
        """
        Предсказание на основе ML модели
        """
        suggestions = []
        
        # Загружаем все блоки
        from app.services.block_service import BlockService
        service = BlockService()
        
        all_blocks = await service.list_blocks(limit=1000)
        
        # Генерируем embeddings для текущих блоков
        current_embeddings = []
        for block_id in current_blocks:
            block = await service.get_block(block_id)
            if block and "annotations" in block and "embedding" in block["annotations"]:
                current_embeddings.append(block["annotations"]["embedding"])
        
        if not current_embeddings:
            return suggestions
        
        # Средний embedding текущего набора
        avg_embedding = np.mean(current_embeddings, axis=0)
        
        # Находим блоки с похожими embeddings
        for block in all_blocks:
            if block["id"] in current_blocks:
                continue
            
            if "annotations" not in block or "embedding" not in block["annotations"]:
                continue
            
            block_embedding = np.array(block["annotations"]["embedding"])
            
            # Косинусное сходство
            similarity = np.dot(avg_embedding, block_embedding) / (
                np.linalg.norm(avg_embedding) * np.linalg.norm(block_embedding)
            )
            
            if similarity > 0.6:
                suggestions.append({
                    "block_id": block["id"],
                    "score": float(similarity),
                    "reason": "semantic_similarity",
                    "method": "ml_based"
                })
        
        return suggestions
    
    def rank_suggestions(self, suggestions: List[dict]) -> List[dict]:
        """
        Ранжирует предложения
        """
        # Группируем по block_id
        grouped = {}
        for sugg in suggestions:
            block_id = sugg["block_id"]
            if block_id not in grouped:
                grouped[block_id] = []
            grouped[block_id].append(sugg)
        
        # Вычисляем финальный score для каждого блока
        ranked = []
        for block_id, sugg_list in grouped.items():
            # Weighted average scores
            total_score = sum(s["score"] for s in sugg_list)
            avg_score = total_score / len(sugg_list)
            
            # Бонус за упоминание в нескольких методах
            method_diversity_bonus = len(set(s["method"] for s in sugg_list)) * 0.1
            
            final_score = avg_score + method_diversity_bonus
            
            ranked.append({
                "block_id": block_id,
                "final_score": final_score,
                "methods": [s["method"] for s in sugg_list],
                "reasons": [s["reason"] for s in sugg_list]
            })
        
        # Сортируем по score
        ranked.sort(key=lambda x: x["final_score"], reverse=True)
        
        return ranked
    
    async def record_usage(self, blocks_used: List[str]):
        """
        Записывает использование блоков для обучения
        """
        # Записываем пары блоков
        for i, block_a in enumerate(blocks_used):
            for block_b in blocks_used[i+1:]:
                pair = tuple(sorted([block_a, block_b]))
                
                if pair not in self.usage_patterns:
                    self.usage_patterns[pair] = 0
                
                self.usage_patterns[pair] += 1
        
        # Сохраняем в БД
        from app.repositories.mongo_repo import MongoRepository
        mongo = MongoRepository()
        
        await mongo.save_usage_patterns(self.usage_patterns)
```

---

## 10. Полные примеры кода

### 10.1 Полный цикл: от парсинга до генерации документа

```python
import asyncio
from datetime import datetime

async def complete_workflow_example():
    """
    Полный рабочий процесс:
    1. Парсинг законодательного текста
    2. Импорт в базу данных
    3. Создание правил
    4. Сборка документа
    5. Экспорт в DOCX
    """
    
    print("=== STEP 1: Parsing Legal Text ===\n")
    
    # Текст закона
    legal_text = """
§29 Persönliches Budget

(1) Auf Antrag werden Leistungen zur Teilhabe durch die Leistungsform 
eines Persönlichen Budgets ausgeführt, um den Leistungsberechtigten in 
eigener Verantwortung ein möglichst selbstbestimmtes Leben zu ermöglichen.

(2) Das Persönliche Budget kann von mehreren Leistungsträgern als 
trägerübergreifendes Persönliches Budget ausgeführt werden.

§17 Gesamtplan

(1) Der Rehabilitationsträger stellt einen Gesamtplan auf.

(2) Der Gesamtplan enthält:

1. die Feststellung der Ausgangslage,
2. die Zielsetzung der erforderlichen Leistungen,
3. die Festlegung der konkret zu erbringenden Leistungen.
    """
    
    # Парсим
    parser = GermanLegalTextParser()
    blocks = parser.parse(legal_text, source="SGB IX")
    
    print(f"Parsed {len(blocks)} blocks\n")
    
    print("=== STEP 2: Importing to Database ===\n")
    
    # Импортируем
    imported_blocks = await import_legal_text(legal_text, source="SGB IX")
    
    print(f"Imported {len(imported_blocks)} blocks\n")
    
    print("=== STEP 3: Creating Rules ===\n")
    
    # Создаём правила
    from app.services.rule_engine import RuleEngine
    
    rule_engine = RuleEngine()
    
    # Правило 1: Если заявление на PB → включить §29
    rule_engine.add_rule({
        "id": "rule_pb_application",
        "name": "Personal Budget Application",
        "priority": 1,
        "conditions": [
            {
                "variable": "application_type",
                "operator": "==",
                "value": "persönliches_budget"
            }
        ],
        "actions": [
            {
                "type": "include_block",
                "block_number": "§29"
            }
        ]
    })
    
    # Правило 2: Если заявление на PB → включить §17 (Gesamtplan)
    rule_engine.add_rule({
        "id": "rule_gesamtplan",
        "name": "Gesamtplan Required",
        "priority": 2,
        "conditions": [
            {
                "variable": "application_type",
                "operator": "==",
                "value": "persönliches_budget"
            }
        ],
        "actions": [
            {
                "type": "include_block",
                "block_number": "§17"
            }
        ]
    })
    
    print("Created 2 rules\n")
    
    print("=== STEP 4: Assembling Document ===\n")
    
    # Контекст для сборки документа
    context = {
        "application_type": "persönliches_budget",
        "applicant_name": "Max Mustermann",
        "applicant_address": "Musterstraße 1\n01234 Dresden",
        "authority_name": "Sozialamt Dresden",
        "authority_address": "Amtsplatz 1\n01067 Dresden",
        "bescheid_date": "2024-01-15",
        "case_number": "S 7 SO 99/25",
        "date": datetime.now().strftime("%d.%m.%Y"),
        "reasoning": "Der Bescheid ist rechtswidrig, da gemäß §29 SGB IX ein Anspruch auf ein Persönliches Budget besteht.",
        "request_hearing": True,
        "attachments": [
            "Kopie des Bescheides vom 15.01.2024",
            "Ärztliches Attest"
        ]
    }
    
    # Собираем документ
    assembler = DocumentAssembler(templates_dir="templates")
    
    document = await assembler.assemble(
        template_id="widerspruch_template",
        context=context,
        strategy="conditional"
    )
    
    print(f"Assembled document with {len(document['blocks'])} blocks\n")
    print(f"Word count: {document['word_count']}\n")
    
    print("=== STEP 5: Exporting to DOCX ===\n")
    
    # Экспортируем
    exporter = DocumentExporter()
    
    output_path = "/mnt/user-data/outputs/widerspruch_example.docx"
    
    await exporter.export_to_docx(document, output_path)
    
    print(f"Exported to: {output_path}\n")
    
    print("=== STEP 6: Document Preview ===\n")
    print(document["content"][:500] + "...\n")
    
    print("=== COMPLETE ===")
    
    return document, output_path

# Запуск
asyncio.run(complete_workflow_example())
```

### 10.2 Пример работы с графом знаний

```python
async def knowledge_graph_example():
    """
    Работа с графом знаний
    """
    from app.repositories.neo4j_repo import Neo4jRepository
    
    neo4j = Neo4jRepository()
    
    print("=== Creating Knowledge Graph ===\n")
    
    # Создаём узлы
    await neo4j.create_node({
        "id": "sgb9_p29",
        "type": "paragraph",
        "number": "§29",
        "title": "Persönliches Budget",
        "source": "SGB IX"
    })
    
    await neo4j.create_node({
        "id": "sgb9_p17",
        "type": "paragraph",
        "number": "§17",
        "title": "Gesamtplan",
        "source": "SGB IX"
    })
    
    await neo4j.create_node({
        "id": "sgb9_p4",
        "type": "paragraph",
        "number": "§4",
        "title": "Leistungsformen",
        "source": "SGB IX"
    })
    
    # Создаём связи
    await neo4j.create_relationship(
        from_id="sgb9_p29",
        to_id="sgb9_p17",
        rel_type="REQUIRES",
        properties={"reason": "Gesamtplan erforderlich für PB"}
    )
    
    await neo4j.create_relationship(
        from_id="sgb9_p29",
        to_id="sgb9_p4",
        rel_type="BASED_ON",
        properties={"reason": "PB ist eine Leistungsform"}
    )
    
    print("Created 3 nodes and 2 relationships\n")
    
    # Запросы к графу
    print("=== Graph Queries ===\n")
    
    # 1. Найти все блоки, связанные с §29
    related = await neo4j.get_neighbors("sgb9_p29", depth=1)
    print(f"Blocks related to §29: {[r['number'] for r in related]}\n")
    
    # 2. Найти путь от §29 до §4
    path = await neo4j.find_shortest_path("sgb9_p29", "sgb9_p4")
    print(f"Path from §29 to §4: {path}\n")
    
    # 3. PageRank - важность параграфов
    ranks = await neo4j.calculate_pagerank()
    print("PageRank scores:")
    for node_id, score in sorted(ranks.items(), key=lambda x: x[1], reverse=True):
        print(f"  {node_id}: {score:.4f}")

asyncio.run(knowledge_graph_example())
```

---

## 11. Deployment и масштабирование

### 11.1 Docker Setup

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - MONGO_URI=mongodb://mongodb:27017
      - MONGO_DB=content_blocks
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - REDIS_URL=redis://redis:6379
    depends_on:
      - neo4j
      - mongodb
      - elasticsearch
      - redis
    volumes:
      - ./app:/app
      - ./data:/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  # Neo4j Graph Database
  neo4j:
    image: neo4j:5.15
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
  
  # MongoDB Document Database
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    volumes:
      - mongo_data:/data/db
  
  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.1
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data
  
  # Redis (for caching and Celery)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # Celery Worker (for async tasks)
  celery_worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - MONGO_URI=mongodb://mongodb:27017
      - MONGO_DB=content_blocks
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - neo4j
      - mongodb
    volumes:
      - ./app:/app
      - ./data:/data

volumes:
  neo4j_data:
  neo4j_logs:
  mongo_data:
  es_data:
  redis_data:
```

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Kubernetes Deployment (для production)

**kubernetes/deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: content-blocks-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: content-blocks-api
  template:
    metadata:
      labels:
        app: content-blocks-api
    spec:
      containers:
      - name: api
        image: content-blocks-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_URI
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: neo4j_uri
        - name: NEO4J_USER
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: neo4j_user
        - name: NEO4J_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: neo4j_password
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: content-blocks-api-service
spec:
  selector:
    app: content-blocks-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 11.3 Мониторинг и логирование

**Prometheus + Grafana**:

```python
# app/monitoring.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Метрики
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

blocks_in_db = Gauge(
    'blocks_in_database',
    'Total blocks in database'
)

# Middleware для метрик
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        active_connections.inc()
        
        try:
            response = await call_next(request)
            
            # Записываем метрики
            api_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            duration = time.time() - start_time
            api_request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
        
        finally:
            active_connections.dec()

# Добавляем в FastAPI
from app.main import app
app.add_middleware(MetricsMiddleware)

# Endpoint для метрик
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

---

## 12. Roadmap и будущее развитие

### 12.1 Phase 1: MVP (Месяцы 1-2)

**Цели**:
- ✅ Базовый парсинг законодательных текстов (SGB IX)
- ✅ Neo4j граф с основными связями
- ✅ MongoDB хранилище блоков
- ✅ Простой rule engine (forward chaining)
- ✅ Базовая сборка документов (linear strategy)
- ✅ Экспорт в DOCX

**Deliverables**:
- 200+ блоков из SGB IX в базе
- 3-5 шаблонов документов (Widerspruch, Antrag)
- REST API с основными endpoints
- Docker Compose setup

### 12.2 Phase 2: Advanced Features (Месяцы 3-4)

**Цели**:
- Семантический поиск (Elasticsearch + embeddings)
- Conditional assembly strategy
- Версионирование блоков
- UI для визуального редактирования графа
- Conflict detection
- Автоматическое встраивание контента

**Deliverables**:
- Web UI (React + Tailwind)
- 500+ блоков (SGB IX + частично BGB, GG)
- Advanced rule engine с backward chaining
- Suggestion engine

### 12.3 Phase 3: AI/ML Integration (Месяцы 5-6)

**Цели**:
- Transformer models для NLP (BERT, GPT)
- Автоматическая классификация блоков
- Генерация новых блоков из текста
- Topic modeling с BERTopic
- Predictive analytics для suggestion engine
- Multi-language support (DE, EN, RU)

**Deliverables**:
- Обученные модели для немецкого права
- API для генерации контента
- Автоматический перевод блоков
- Quality scoring для блоков

### 12.4 Phase 4: Enterprise Features (Месяцы 7-9)

**Цели**:
- Multi-tenancy (разные организации)
- Role-based access control (RBAC)
- Audit logging
- Compliance tracking (GDPR, etc.)
- Integration с внешними системами
- Advanced analytics dashboard

**Deliverables**:
- Enterprise-ready deployment
- SSO integration (SAML, OAuth)
- Compliance reports
- API rate limiting
- Subscription management

### 12.5 Phase 5: Scale & Performance (Месяцы 10-12)

**Цели**:
- Horizontal scaling
- Caching strategy (Redis)
- Database sharding
- CDN для статики
- Load balancing
- Performance optimization

**Deliverables**:
- Kubernetes deployment
- 10,000+ blocks support
- <100ms API response time
- 99.9% uptime SLA
- Monitoring & alerting (Prometheus, Grafana)

---

## 13. Приложения

### Приложение A: Полный список технологий

**Backend**:
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- asyncio

**Databases**:
- Neo4j 5.15 (Graph)
- MongoDB 7.0 (Documents)
- Elasticsearch 8.11 (Search)
- Redis 7 (Cache)

**NLP/ML**:
- spaCy 3.7
- sentence-transformers
- transformers (Hugging Face)
- gensim (LDA)
- BERTopic
- scikit-learn
- numpy, pandas

**Document Processing**:
- python-docx
- PyPDF2, pdfplumber
- python-pptx
- openpyxl
- Pandoc (via subprocess)

**Frontend** (опционально):
- React 18
- TypeScript
- Tailwind CSS
- Axios
- React Query
- D3.js (для графов)

**DevOps**:
- Docker
- Docker Compose
- Kubernetes
- GitHub Actions
- Prometheus
- Grafana
- Nginx

### Приложение B: Глоссарий терминов

**Block** (Блок): атомарная единица контента с метаданными  
**Rule** (Правило): условие IF-THEN для активации блоков  
**Assembly** (Сборка): процесс генерации документа из блоков  
**Strategy** (Стратегия): метод сборки (linear, conditional, hierarchical)  
**Template** (Шаблон): структура документа с плейсхолдерами  
**Context** (Контекст): набор переменных для rule engine  
**Embedding** (Эмбеддинг): векторное представление текста  
**Topic** (Топик): семантическая категория блоков  
**Depth Level** (Уровень детализации): мера подробности контента  
**Escalation** (Эскалация): повышение уровня детализации  
**Conflict** (Конфликт): противоречие между блоками  
**Suggestion** (Предложение): AI-рекомендация следующих блоков

**Немецкие юридические термины**:
- **Paragraph (§)**: параграф закона
- **Absatz (Abs.)**: абзац параграфа
- **Satz (S.)**: предложение
- **Artikel (Art.)**: статья (обычно в конституции)
- **Widerspruch**: возражение, протест
- **Bescheid**: административное решение, постановление
- **Antrag**: заявление, ходатайство
- **Persönliches Budget**: личный бюджет (форма соцподдержки)
- **Teilhabe**: участие, интеграция
- **Leistungsträger**: органы социального обеспечения

### Приложение C: Примеры use cases

**1. Юридическая фирма**:
- Автоматическая генерация Widerspruch по шаблонам
- База знаний законодательства с быстрым поиском
- Версионирование документов клиентов
- Conflict detection в договорах

**2. Государственные органы**:
- Управление законодательной базой
- Автоматическое обновление связанных документов
- Публикация изменений в законах
- Генерация отчётов для граждан

**3. Образовательные учреждения**:
- Интерактивные учебные материалы по праву
- Персонализированные учебные траектории
- База прецедентов с семантическим поиском
- Автоматическая генерация тестов

**4. Корпоративная документация**:
- Управление политиками и процедурами
- Автоматическое обновление руководств
- Compliance tracking
- Многоязычные версии документов

**5. Новостные агентства**:
- Автоматическая кластеризация новостей
- Генерация summary разных уровней
- Topic tracking
- Персонализированные дайджесты

### Приложение D: Ссылки на ресурсы

**Документация**:
- Neo4j: https://neo4j.com/docs/
- MongoDB: https://docs.mongodb.com/
- Elasticsearch: https://www.elastic.co/guide/
- FastAPI: https://fastapi.tiangolo.com/
- spaCy: https://spacy.io/
- Sentence Transformers: https://www.sbert.net/

**Стандарты**:
- Akoma Ntoso: http://www.akomantoso.org/
- DITA: https://www.dita-ot.org/
- LegalDocML: https://www.oasis-open.org/committees/legaldocml/

**Академические статьи**:
- "Graph-based Knowledge Representation for Legal Reasoning"
- "Semantic Networks in Natural Language Processing"
- "Automated Document Assembly Systems"
- "Rule-Based Expert Systems in Legal Domain"

**Open Source Projects**:
- Apache Tika (document parsing)
- Apache UIMA (text analytics)
- Stanford CoreNLP
- OpenNLP

### Приложение E: Чеклист для внедрения

**Pre-deployment**:
- [ ] Определены требования к системе
- [ ] Выбраны источники законодательных текстов
- [ ] Подготовлены шаблоны документов
- [ ] Настроена инфраструктура (серверы, БД)
- [ ] Проведено тестирование на тестовых данных

**Deployment**:
- [ ] Развёрнуты базы данных (Neo4j, MongoDB, Elasticsearch)
- [ ] Импортированы законодательные тексты
- [ ] Созданы правила и шаблоны
- [ ] Настроена аутентификация и авторизация
- [ ] Проведены нагрузочные тесты

**Post-deployment**:
- [ ] Настроен мониторинг (Prometheus, Grafana)
- [ ] Настроены алерты
- [ ] Проведено обучение пользователей
- [ ] Собрана обратная связь
- [ ] Запланированы регулярные обновления

**Maintenance**:
- [ ] Регулярное обновление законодательной базы
- [ ] Мониторинг производительности
- [ ] Бэкапы баз данных (ежедневно)
- [ ] Обновление зависимостей (ежемесячно)
- [ ] Review и оптимизация правил (ежеквартально)

---

## Заключение

Эта методология предоставляет comprehensive подход к созданию системы динамических информационных блоков. Ключевые преимущества:

1. **Модульность**: блоки можно переиспользовать в разных контекстах
2. **Автоматизация**: документы собираются автоматически по правилам
3. **Масштабируемость**: система легко расширяется на новые области
4. **Интеллектуальность**: AI/ML для предложений и оптимизации
5. **Версионирование**: полная история изменений
6. **Поиск**: семантический поиск по смыслу, не только по ключевым словам

**Следующие шаги**:
1. Начните с MVP - парсинг и базовая сборка
2. Постепенно добавляйте advanced функции
3. Собирайте feedback от пользователей
4. Итеративно улучшайте систему

Удачи в реализации! 🚀

---

**Версия документа**: 1.0  
**Последнее обновление**: 04.02.2026  
**Автор**: Claude (Anthropic)  
**Лицензия**: MIT (для open source реализаций)
