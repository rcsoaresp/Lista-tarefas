"""
test_task_manager.py - Suíte de testes unitários para a aplicação de Lista de Tarefas.
Valida regras de negócio, persistência e casos de borda.
"""

import os
import tempfile
import unittest
from task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """Cria um arquivo temporário exclusivo para cada teste."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.manager = TaskManager(storage_file=self.temp_file.name)

    def tearDown(self):
        """Limpa o arquivo temporário após a execução do teste."""
        if os.path.exists(self.temp_file.name):
            try:
                os.remove(self.temp_file.name)
            except OSError:
                pass

    def test_add_task_success(self):
        """Valida que uma tarefa válida é criada com atributos padrão corretos."""
        task = self.manager.add_task("Estudar Python")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Estudar Python")
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.created_at)
        self.assertIsNone(task.completed_at)
        self.assertEqual(len(self.manager.tasks), 1)

    def test_add_multiple_tasks_increments_id(self):
        """Valida que múltiplas tarefas recebem IDs incrementais únicos."""
        t1 = self.manager.add_task("Tarefa 1")
        t2 = self.manager.add_task("Tarefa 2")
        t3 = self.manager.add_task("Tarefa 3")
        self.assertEqual(t1.id, 1)
        self.assertEqual(t2.id, 2)
        self.assertEqual(t3.id, 3)
        self.assertEqual(len(self.manager.tasks), 3)

    def test_add_task_trims_whitespace(self):
        """Valida que espaços extras no início e fim são removidos."""
        task = self.manager.add_task("   Comprar leite   ")
        self.assertEqual(task.title, "Comprar leite")

    def test_add_task_empty_or_whitespace_raises_value_error(self):
        """Valida que tentar adicionar tarefas vazias ou com espaços gera erro."""
        with self.assertRaises(ValueError):
            self.manager.add_task("")
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")
        with self.assertRaises(ValueError):
            self.manager.add_task(None)

    def test_toggle_task_status(self):
        """Valida a alternância de status de pendente para concluída e vice-versa."""
        task = self.manager.add_task("Fazer exercícios")
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

        # Alternar para concluída
        success = self.manager.toggle_task_status(task.id)
        self.assertTrue(success)
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)

        # Alternar de volta para pendente
        success = self.manager.toggle_task_status(task.id)
        self.assertTrue(success)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

    def test_toggle_nonexistent_task(self):
        """Valida que tentar alterar tarefa inexistente retorna False."""
        success = self.manager.toggle_task_status(9999)
        self.assertFalse(success)

    def test_set_task_status_explicit(self):
        """Valida a definição direta do status com set_task_status."""
        task = self.manager.add_task("Ler documentação")
        self.manager.set_task_status(task.id, True)
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)

        self.manager.set_task_status(task.id, False)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

    def test_remove_task_success(self):
        """Valida a exclusão de uma tarefa existente."""
        t1 = self.manager.add_task("Tarefa A")
        t2 = self.manager.add_task("Tarefa B")

        success = self.manager.remove_task(t1.id)
        self.assertTrue(success)
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertIsNone(self.manager.get_task(t1.id))
        self.assertIsNotNone(self.manager.get_task(t2.id))

    def test_remove_nonexistent_task(self):
        """Valida que tentar remover ID inexistente retorna False sem erros."""
        self.manager.add_task("Tarefa A")
        success = self.manager.remove_task(9999)
        self.assertFalse(success)
        self.assertEqual(len(self.manager.tasks), 1)

    def test_filter_tasks(self):
        """Valida a filtragem correta por todas, pendentes e concluídas."""
        t1 = self.manager.add_task("Tarefa 1")
        t2 = self.manager.add_task("Tarefa 2")
        t3 = self.manager.add_task("Tarefa 3")

        self.manager.toggle_task_status(t2.id)  # Marca Tarefa 2 como concluída

        all_tasks = self.manager.get_tasks("all")
        pending_tasks = self.manager.get_tasks("pending")
        completed_tasks = self.manager.get_tasks("completed")

        self.assertEqual(len(all_tasks), 3)
        self.assertEqual(len(pending_tasks), 2)
        self.assertEqual(len(completed_tasks), 1)
        self.assertIn(t1, pending_tasks)
        self.assertIn(t3, pending_tasks)
        self.assertIn(t2, completed_tasks)

    def test_get_summary_counts(self):
        """Valida os contadores de tarefas totais, pendentes e concluídas."""
        self.manager.add_task("T1")
        t2 = self.manager.add_task("T2")
        self.manager.add_task("T3")
        self.manager.toggle_task_status(t2.id)

        summary = self.manager.get_summary()
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["pending"], 2)
        self.assertEqual(summary["completed"], 1)

    def test_clear_completed(self):
        """Valida a remoção em lote de todas as tarefas concluídas."""
        t1 = self.manager.add_task("Pendente 1")
        t2 = self.manager.add_task("Concluída 1")
        t3 = self.manager.add_task("Concluída 2")
        self.manager.toggle_task_status(t2.id)
        self.manager.toggle_task_status(t3.id)

        removed = self.manager.clear_completed()
        self.assertEqual(removed, 2)
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0].id, t1.id)

    def test_persistence_save_and_load(self):
        """Valida que as tarefas são persistidas e restauradas fielmente em JSON."""
        t1 = self.manager.add_task("Reunião com equipe")
        t2 = self.manager.add_task("Enviar relatório mensal")
        self.manager.toggle_task_status(t1.id)

        # Cria nova instância apontando para o mesmo arquivo
        new_manager = TaskManager(storage_file=self.temp_file.name)
        self.assertEqual(len(new_manager.tasks), 2)

        loaded_t1 = new_manager.get_task(t1.id)
        loaded_t2 = new_manager.get_task(t2.id)

        self.assertIsNotNone(loaded_t1)
        self.assertEqual(loaded_t1.title, "Reunião com equipe")
        self.assertTrue(loaded_t1.completed)

        self.assertIsNotNone(loaded_t2)
        self.assertEqual(loaded_t2.title, "Enviar relatório mensal")
        self.assertFalse(loaded_t2.completed)

        # Adicionar nova tarefa deve continuar ID após os existentes
        t3 = new_manager.add_task("Nova tarefa após load")
        self.assertEqual(t3.id, 3)

    def test_persistence_corrupted_file(self):
        """Valida resiliência caso o arquivo JSON esteja corrompido."""
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write("{ json inválido ...")

        # Não deve lançar exceção fatal
        safe_manager = TaskManager(storage_file=self.temp_file.name)
        self.assertEqual(len(safe_manager.tasks), 0)


if __name__ == "__main__":
    unittest.main()
