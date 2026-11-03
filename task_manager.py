"""
task_manager.py - Gerenciador de lógica de negócios e persistência para a Lista de Tarefas.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import Task


class TaskManager:
    """
    Controlador responsável pelo ciclo de vida das tarefas:
    - Adicionar tarefa
    - Alternar/marcar status de conclusão
    - Excluir tarefa
    - Filtrar tarefas (todas, pendentes, concluídas)
    - Persistência em arquivo JSON
    """

    def __init__(self, storage_file: Optional[str] = "tasks.json"):
        self.storage_file = storage_file
        self.tasks: List[Task] = []
        self._next_id = 1
        if self.storage_file and os.path.exists(self.storage_file):
            self.load_from_file()

    def add_task(self, title: str) -> Task:
        """Adiciona uma nova tarefa com título não-vazio."""
        clean_title = title.strip() if title else ""
        if not clean_title:
            raise ValueError("O título da tarefa não pode estar vazio.")

        task = Task(id=self._next_id, title=clean_title, completed=False)
        self._next_id += 1
        self.tasks.append(task)
        self.save_to_file()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Busca uma tarefa pelo seu identificador único."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def toggle_task_status(self, task_id: int) -> bool:
        """
        Alterna o status de concluído de uma tarefa existente.
        Retorna True se a tarefa foi encontrada e atualizada, False caso contrário.
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.completed = not task.completed
        if task.completed:
            task.completed_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        else:
            task.completed_at = None

        self.save_to_file()
        return True

    def set_task_status(self, task_id: int, completed: bool) -> bool:
        """Define explicitamente o status de conclusão de uma tarefa."""
        task = self.get_task(task_id)
        if not task:
            return False

        task.completed = completed
        if completed:
            task.completed_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        else:
            task.completed_at = None

        self.save_to_file()
        return True

    def remove_task(self, task_id: int) -> bool:
        """
        Remove uma tarefa com base no seu ID.
        Retorna True se removida, False se não encontrada.
        """
        task = self.get_task(task_id)
        if not task:
            return False

        self.tasks.remove(task)
        self.save_to_file()
        return True

    def get_tasks(self, filter_status: str = "all") -> List[Task]:
        """
        Retorna as tarefas de acordo com o filtro:
        - 'all': Todas as tarefas
        - 'pending': Apenas pendentes
        - 'completed': Apenas concluídas
        """
        if filter_status == "pending":
            return [t for t in self.tasks if not t.completed]
        elif filter_status == "completed":
            return [t for t in self.tasks if t.completed]
        return list(self.tasks)

    def get_summary(self) -> Dict[str, int]:
        """Retorna contadores de tarefas totais, pendentes e concluídas."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pending = total - completed
        return {
            "total": total,
            "pending": pending,
            "completed": completed
        }

    def clear_completed(self) -> int:
        """Remove todas as tarefas que já foram concluídas."""
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.completed]
        removed_count = initial_len - len(self.tasks)
        if removed_count > 0:
            self.save_to_file()
        return removed_count

    def save_to_file(self, filepath: Optional[str] = None) -> bool:
        """Persiste as tarefas em arquivo JSON."""
        target_path = filepath or self.storage_file
        if not target_path:
            return False
        try:
            data = {
                "next_id": self._next_id,
                "tasks": [t.to_dict() for t in self.tasks]
            }
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def load_from_file(self, filepath: Optional[str] = None) -> bool:
        """Carrega as tarefas de um arquivo JSON."""
        target_path = filepath or self.storage_file
        if not target_path or not os.path.exists(target_path):
            return False
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = [Task.from_dict(item) for item in data.get("tasks", [])]
            max_id = max([t.id for t in self.tasks], default=0)
            self._next_id = max(data.get("next_id", 1), max_id + 1)
            return True
        except (json.JSONDecodeError, KeyError, OSError, TypeError):
            return False
