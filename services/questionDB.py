from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import json
from typing import List, Optional

from models.Question import Question


class QuestionDB:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data: List[dict] = []
        self._load()

    def _load(self):
        if self.file_path.exists():
            with self.file_path.open("r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def _save(self):
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_questions(self, event_id: int) -> List[Question]:
        return [
            Question.from_dict(q)
            for q in self.data
            if q["event_id"] == event_id
        ]

    def get_question(self, question_id: str) -> Optional[Question]:
        for q in self.data:
            if q["id"] == question_id:
                return Question.from_dict(q)
        return None

    def remove_question(self, question_id: str):
        self.data = [q for q in self.data if q["id"] != question_id]
        self._save()

    def add_question(self, question: Question):
        self.data.append(question.to_dict())
        self._save()
