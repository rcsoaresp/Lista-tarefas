"""
models.py - Modelos de dados para a aplicação de Lista de Tarefas.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Representa uma tarefa individual."""
    id: int
    title: str
    completed: bool = False
    created_at: str = ""
    completed_at: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    def to_dict(self) -> dict:
        """Converte a tarefa em dicionário serializável."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstrói uma instância de Task a partir de um dicionário."""
        return cls(
            id=data["id"],
            title=data["title"],
            completed=data.get("completed", False),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at", None),
        )
