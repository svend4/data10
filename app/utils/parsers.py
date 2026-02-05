"""
Parsers for legal texts (SGB IX, BGB, etc.)
"""

import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import Block, BlockMetadata, BlockRelationships


class SGBParser:
    """Парсер для SGB (Sozialgesetzbuch) текстов"""

    # Regex patterns
    PARAGRAPH_PATTERN = r'§\s*(\d+)\s+([^\n]+)'  # §5 Title
    ABSATZ_PATTERN = r'\((\d+)\)\s+'  # (1), (2), etc.

    def __init__(self, law_name: str = "SGB IX"):
        self.law_name = law_name

    def parse_text(self, text: str) -> List[Block]:
        """
        Парсинг текста закона на блоки

        :param text: Текст закона
        :return: Список блоков
        """
        blocks = []

        # Разделить на параграфы
        paragraphs = self._split_into_paragraphs(text)

        for para_num, para_title, para_content in paragraphs:
            block = self._create_paragraph_block(para_num, para_title, para_content)
            blocks.append(block)

            # Парсинг абзацев внутри параграфа
            absatz_blocks = self._parse_absatze(para_num, para_content)
            blocks.extend(absatz_blocks)

        return blocks

    def _split_into_paragraphs(self, text: str) -> List[tuple]:
        """
        Разделить текст на параграфы

        :param text: Текст закона
        :return: Список (номер, заголовок, содержимое)
        """
        paragraphs = []

        # Найти все параграфы
        matches = list(re.finditer(self.PARAGRAPH_PATTERN, text))

        for i, match in enumerate(matches):
            para_num = match.group(1)
            para_title = match.group(2).strip()

            # Содержимое от текущего параграфа до следующего
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            para_content = text[start:end].strip()

            paragraphs.append((para_num, para_title, para_content))

        return paragraphs

    def _create_paragraph_block(
        self,
        para_num: str,
        para_title: str,
        para_content: str
    ) -> Block:
        """
        Создать блок параграфа

        :param para_num: Номер параграфа
        :param para_title: Заголовок параграфа
        :param para_content: Содержимое параграфа
        :return: Block
        """
        block_id = f"{self.law_name.lower().replace(' ', '_')}_para{para_num}"

        # Извлечь ключевые термины для тегов
        tags = self._extract_tags(para_title + " " + para_content)

        metadata = BlockMetadata(
            law=self.law_name,
            paragraph=para_num,
            language="de",
            tags=tags
        )

        # Определить дочерние блоки (абзацы)
        absatz_ids = self._find_absatz_ids(para_num, para_content)

        relationships = BlockRelationships(
            children=absatz_ids
        )

        return Block(
            id=block_id,
            type="paragraph",
            title=f"§{para_num} {para_title}",
            content=para_content,
            source=self.law_name,
            level=1,
            metadata=metadata,
            relationships=relationships
        )

    def _parse_absatze(self, para_num: str, para_content: str) -> List[Block]:
        """
        Парсинг абзацев внутри параграфа

        :param para_num: Номер параграфа
        :param para_content: Содержимое параграфа
        :return: Список блоков абзацев
        """
        blocks = []
        matches = list(re.finditer(self.ABSATZ_PATTERN, para_content))

        if not matches:
            return blocks

        for i, match in enumerate(matches):
            absatz_num = match.group(1)

            # Содержимое от текущего абзаца до следующего
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(para_content)
            absatz_content = para_content[start:end].strip()

            block = self._create_absatz_block(
                para_num,
                absatz_num,
                absatz_content
            )
            blocks.append(block)

        return blocks

    def _create_absatz_block(
        self,
        para_num: str,
        absatz_num: str,
        absatz_content: str
    ) -> Block:
        """
        Создать блок абзаца

        :param para_num: Номер параграфа
        :param absatz_num: Номер абзаца
        :param absatz_content: Содержимое абзаца
        :return: Block
        """
        block_id = f"{self.law_name.lower().replace(' ', '_')}_para{para_num}_abs{absatz_num}"
        parent_id = f"{self.law_name.lower().replace(' ', '_')}_para{para_num}"

        metadata = BlockMetadata(
            law=self.law_name,
            paragraph=para_num,
            absatz=int(absatz_num),
            language="de",
            tags=self._extract_tags(absatz_content)
        )

        relationships = BlockRelationships(
            parent=parent_id
        )

        return Block(
            id=block_id,
            type="absatz",
            title=f"§{para_num} Abs. {absatz_num}",
            content=absatz_content,
            source=self.law_name,
            level=2,
            metadata=metadata,
            relationships=relationships
        )

    def _find_absatz_ids(self, para_num: str, para_content: str) -> List[str]:
        """Найти ID всех абзацев в параграфе"""
        matches = re.findall(self.ABSATZ_PATTERN, para_content)
        return [
            f"{self.law_name.lower().replace(' ', '_')}_para{para_num}_abs{abs_num}"
            for abs_num in matches
        ]

    def _extract_tags(self, text: str) -> List[str]:
        """
        Извлечь ключевые термины из текста для тегов

        :param text: Текст
        :return: Список тегов
        """
        # Простой подход: ключевые термины для SGB IX
        keywords = [
            "teilhabe", "rehabilitation", "leistung", "budget",
            "persönliches budget", "antrag", "bescheid", "widerspruch",
            "behinderung", "pflegebedürftigkeit", "arbeitsleben"
        ]

        tags = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                tags.append(keyword)

        return tags[:5]  # Ограничить 5 тегами


class DocumentParser:
    """Общий парсер для разных типов документов"""

    @staticmethod
    def detect_law_type(text: str) -> Optional[str]:
        """
        Определить тип закона по тексту

        :param text: Текст
        :return: Тип закона или None
        """
        if "SGB IX" in text or "Sozialgesetzbuch" in text:
            return "SGB IX"
        elif "BGB" in text or "Bürgerliches Gesetzbuch" in text:
            return "BGB"
        elif "GG" in text or "Grundgesetz" in text:
            return "GG"
        return None

    @staticmethod
    def parse_file(file_path: str) -> List[Block]:
        """
        Парсинг файла с законодательным текстом

        :param file_path: Путь к файлу
        :return: Список блоков
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Определить тип закона
        law_type = DocumentParser.detect_law_type(text)

        if law_type in ["SGB IX", "SGB I", "SGB II"]:  # Все SGB используют один парсер
            parser = SGBParser(law_type)
            return parser.parse_text(text)

        # TODO: добавить парсеры для BGB, GG
        raise ValueError(f"Unsupported law type: {law_type}")


# Convenience function
def parse_sgb_file(file_path: str, law_name: str = "SGB IX") -> List[Block]:
    """
    Удобная функция для парсинга SGB файла

    :param file_path: Путь к файлу
    :param law_name: Название закона
    :return: Список блоков
    """
    parser = SGBParser(law_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return parser.parse_text(text)
