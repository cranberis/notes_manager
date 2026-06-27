from __future__ import annotations

import json
import logging
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import TypedDict

from logger import setup_logging


FILE_PATH: Path = Path('data/notes.json')
logger = logging.getLogger(__name__)


class NoteDict(TypedDict):
    id: int
    text: str
    tags: list[str]
    created_at: str


class Note:

    def __init__(self, id: int, text: str,
                 tags: list[str], created_at: str) -> None:
        self.id = id
        self.text = text
        self.tags = tags
        self.created_at = created_at

    def __str__(self) -> str:
        return f"Note #{self.id}: {self.text[:50]}... [tags: {', '.join(self.tags)}]"


class NotesStorage:

    def __init__(self) -> None:
        self._storage: list[Note] = []
        self._load_from_file()

    def _load_from_file(self) -> None:
        """Для считывания заметок из .json-файла в self._storage при запуске кода"""
        FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                for note_dict in json.load(f):
                    note = Note(
                        note_dict["id"],
                        note_dict["text"],
                        note_dict["tags"],
                        note_dict["created_at"]
                    )
                    self._storage.append(note)
                logger.debug(f"Загружено {len(self._storage)} заметок из файла")
        except FileNotFoundError:
            logger.info(f"При первом запуске кода файла {FILE_PATH} - не существует")
        except JSONDecodeError:
            logger.info(f"При первом запуске файл {FILE_PATH} - пустой")

    def _save_to_file(self) -> None:
        """Для записи заметки в файл `.json`"""
        notes_list = []
        for note in self._storage:
            note_dict: NoteDict = {
                "id": note.id,
                "text": note.text,
                "tags": note.tags,
                "created_at": note.created_at
            }
            notes_list.append(note_dict)
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(notes_list, f, ensure_ascii=False, indent=2)
            logger.debug(f"Сохранено {len(notes_list)} заметок в файл")

    def add_note(self, text: str, tags: list[str]) -> Note:
        """Метод для добавления новых заметок."""
        note_id = max((note.id for note in self._storage), default=0) + 1
        note_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_note = Note(note_id, text, tags, note_date)
        self._storage.append(current_note)
        self._save_to_file()
        logger.info(f"Создана заметка: {current_note}")
        return current_note

    def get_all_notes(self) -> list[Note]:
        """Получить все сохранённые заметки."""
        logger.debug("Вызван метод `get_all_notes()`")
        return self._storage

    def find_by_tag(self, tag: str) -> list[Note]:
        """Найти заметки по указанному тегу."""
        result = [note for note in self._storage if tag in note.tags]
        logger.info(f"Вызван метод `find_by_tag()`, для заметки с тегом #{tag}")
        return result

    def delete_note(self, note_id: int) -> bool:
        """Метод для удаления заметок по ID."""
        for note in self._storage:
            if note_id == note.id:
                self._storage.remove(note)
                self._save_to_file()
                logger.info("Вызван метод `delete_note()`"
                            f" - удалена заметка с номером {note_id}: {note}")
                break
        else:
            logger.warning("Вызван метод `delete_note()`"
                        f" - заметки с номером {note_id} - не существует")
            return False
        return True


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    notes_storage = NotesStorage()
    print(notes_storage.add_note("Первое тестовое сообщение", ["первое"]))
    print(notes_storage.add_note("Второе тестовое сообщение", ["второе"]))
    print(*notes_storage.get_all_notes())
    print(*notes_storage.find_by_tag("первое"))
    print(*notes_storage.find_by_tag("второе"))
    print(notes_storage.delete_note(3))
    print(notes_storage.delete_note(2))