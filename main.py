"""
main.py - Ponto de entrada para iniciar a aplicação Lista de Tarefas.
Execute este arquivo no terminal com: python main.py
"""

from app import TodoApp


def main():
    """Inicia a aplicação gráfica."""
    app = TodoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
