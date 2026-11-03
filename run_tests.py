"""
run_tests.py - Script de execução e relatório didático de testes da solução.
Executa a suíte de testes com validações detalhadas dos requisitos da aplicação.
"""

import sys
import unittest

# Assegura suporte adequado a UTF-8 no console do Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from test_task_manager import TestTaskManager


def run():
    print("=" * 70)
    print("         SUÍTE DE TESTES E VALIDAÇÃO - TO-DO LIST")
    print("=" * 70)
    print("Requisitos a serem validados:")
    print(" [1] Adicionar tarefas (validação de entradas válidas, vazias e espaços)")
    print(" [2] Marcar/desmarcar tarefas como concluídas (timestamp e status)")
    print(" [3] Remover tarefas (existentes e inexistentes)")
    print(" [4] Filtros de exibição (todas, pendentes, concluídas)")
    print(" [5] Persistência em disco (formato JSON e integridade dos dados)")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTaskManager)
    runner = unittest.TextTestRunner(verbosity=2)

    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"Total de testes executados: {result.testsRun}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n [SUCESSO] Todos os casos de teste passaram com êxito!")
        print(" A solução atende a 100% dos requisitos funcionais e de qualidade.")
        print("=" * 70)
        return 0
    else:
        print("\n [FALHA] Alguns testes não passaram. Verifique o log acima.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run())
