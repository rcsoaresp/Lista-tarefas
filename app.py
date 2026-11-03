"""
app.py - Interface gráfica (GUI) em Tkinter para a Lista de Tarefas.
Design moderno, intuitivo, responsivo e com suporte a atalhos de teclado.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from typing import Optional
from task_manager import TaskManager


class TodoApp(tk.Tk):
    """Janela principal da aplicação Lista de Tarefas."""

    # Paleta de Cores Moderna (Estilo Tailwind / Clean Slate)
    BG_COLOR = "#F8FAFC"          # Slate 50
    HEADER_BG = "#1E293B"         # Slate 800
    HEADER_TEXT = "#FFFFFF"
    CARD_BG = "#FFFFFF"           # Branco
    CARD_BORDER = "#E2E8F0"       # Slate 200
    TEXT_MAIN = "#0F172A"         # Slate 900
    TEXT_MUTED = "#64748B"        # Slate 500
    PRIMARY = "#2563EB"           # Blue 600
    PRIMARY_HOVER = "#1D4ED8"     # Blue 700
    SUCCESS = "#16A34A"           # Green 600
    SUCCESS_BG = "#DCFCE7"        # Green 100
    PENDING_COLOR = "#D97706"     # Amber 600
    PENDING_BG = "#FEF3C7"        # Amber 100
    DANGER = "#EF4444"            # Red 500
    DANGER_HOVER = "#DC2626"      # Red 600

    def __init__(self, task_manager: Optional[TaskManager] = None):
        super().__init__()

        self.manager = task_manager if task_manager is not None else TaskManager()
        self.current_filter = "all"  # 'all', 'pending', 'completed'

        # Configurações da Janela
        self.title("Lista de Tarefas - To-Do List")
        self.geometry("620x720")
        self.minsize(540, 600)
        self.configure(bg=self.BG_COLOR)

        # Centralizar na tela
        self._center_window(620, 720)

        # Configurar Fontes
        self._setup_fonts()

        # Construir Interface
        self._build_header()
        self._build_input_section()
        self._build_filter_bar()
        self._build_task_list_area()
        self._build_footer()

        # Renderizar tarefas iniciais
        self.refresh_tasks()

    def _center_window(self, width: int, height: int):
        """Centraliza a janela na tela do usuário."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_fonts(self):
        """Define as fontes tipográficas da aplicação."""
        self.font_title = font.Font(family="Segoe UI", size=18, weight="bold")
        self.font_subtitle = font.Font(family="Segoe UI", size=10)
        self.font_body = font.Font(family="Segoe UI", size=11)
        self.font_body_completed = font.Font(family="Segoe UI", size=11, overstrike=1)
        self.font_sm = font.Font(family="Segoe UI", size=9)
        self.font_btn = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_badge = font.Font(family="Segoe UI", size=9, weight="bold")

    def _build_header(self):
        """Cria o cabeçalho estilizado da aplicação."""
        header_frame = tk.Frame(self, bg=self.HEADER_BG, padx=24, pady=18)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text=" Minhas Tarefas",
            font=self.font_title,
            fg=self.HEADER_TEXT,
            bg=self.HEADER_BG,
            anchor="w"
        )
        title_label.pack(fill=tk.X)

        subtitle_label = tk.Label(
            header_frame,
            text="Organize suas pendências diárias e acompanhe seu progresso",
            font=self.font_subtitle,
            fg="#94A3B8",
            bg=self.HEADER_BG,
            anchor="w"
        )
        subtitle_label.pack(fill=tk.X, pady=(2, 0))

    def _build_input_section(self):
        """Cria a barra de digitação para adicionar novas tarefas."""
        input_container = tk.Frame(self, bg=self.BG_COLOR, padx=20, pady=16)
        input_container.pack(fill=tk.X)

        input_box = tk.Frame(input_container, bg=self.CARD_BG, highlightbackground=self.CARD_BORDER,
                             highlightthickness=1, padx=4, pady=4)
        input_box.pack(fill=tk.X)

        self.entry_var = tk.StringVar()
        self.task_entry = tk.Entry(
            input_box,
            textvariable=self.entry_var,
            font=self.font_body,
            fg=self.TEXT_MAIN,
            bg=self.CARD_BG,
            relief="flat",
            bd=0
        )
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 8), ipady=6)
        self.task_entry.focus_set()

        # Adicionar via tecla Enter
        self.task_entry.bind("<Return>", lambda event: self.handle_add_task())

        # Placeholder visual
        self.placeholder_text = "O que você precisa realizar hoje?"
        self._setup_placeholder()

        # Botão Adicionar
        add_btn = tk.Button(
            input_box,
            text="➕ Adicionar",
            font=self.font_btn,
            bg=self.PRIMARY,
            fg="#FFFFFF",
            activebackground=self.PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.handle_add_task
        )
        add_btn.pack(side=tk.RIGHT)

    def _setup_placeholder(self):
        """Configura comportamento de texto de ajuda (placeholder)."""
        self.task_entry.insert(0, self.placeholder_text)
        self.task_entry.configure(fg=self.TEXT_MUTED)

        def on_focus_in(event):
            if self.task_entry.get() == self.placeholder_text:
                self.task_entry.delete(0, tk.END)
                self.task_entry.configure(fg=self.TEXT_MAIN)

        def on_focus_out(event):
            if not self.task_entry.get().strip():
                self.task_entry.delete(0, tk.END)
                self.task_entry.insert(0, self.placeholder_text)
                self.task_entry.configure(fg=self.TEXT_MUTED)

        self.task_entry.bind("<FocusIn>", on_focus_in)
        self.task_entry.bind("<FocusOut>", on_focus_out)

    def _build_filter_bar(self):
        """Cria as abas de filtragem (Todas, Pendentes, Concluídas)."""
        filter_container = tk.Frame(self, bg=self.BG_COLOR, padx=20, pady=4)
        filter_container.pack(fill=tk.X)

        self.btn_filter_all = tk.Button(
            filter_container, text="Todas (0)", font=self.font_sm,
            relief="flat", bd=0, padx=12, pady=4, cursor="hand2",
            command=lambda: self.set_filter("all")
        )
        self.btn_filter_all.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_filter_pending = tk.Button(
            filter_container, text="Pendentes (0)", font=self.font_sm,
            relief="flat", bd=0, padx=12, pady=4, cursor="hand2",
            command=lambda: self.set_filter("pending")
        )
        self.btn_filter_pending.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_filter_completed = tk.Button(
            filter_container, text="Concluídas (0)", font=self.font_sm,
            relief="flat", bd=0, padx=12, pady=4, cursor="hand2",
            command=lambda: self.set_filter("completed")
        )
        self.btn_filter_completed.pack(side=tk.LEFT)

    def _build_task_list_area(self):
        """Área rolável com a lista de cards de tarefas."""
        list_container = tk.Frame(self, bg=self.BG_COLOR, padx=20, pady=10)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(list_container, bg=self.BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.BG_COLOR)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)

        # Ajustar largura do frame interno ao redimensionar a janela
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Suporte ao scroll com a roda do mouse (Windows / Linux)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Permite rolar a lista com a roda do mouse."""
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_footer(self):
        """Cria o rodapé com resumo estatístico e ação de limpeza."""
        footer_frame = tk.Frame(self, bg="#FFFFFF", highlightbackground=self.CARD_BORDER,
                                highlightthickness=1, padx=20, pady=12)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.summary_label = tk.Label(
            footer_frame,
            text="",
            font=self.font_sm,
            fg=self.TEXT_MUTED,
            bg="#FFFFFF"
        )
        self.summary_label.pack(side=tk.LEFT)

        self.clear_btn = tk.Button(
            footer_frame,
            text="Limpar concluídas",
            font=self.font_sm,
            fg=self.TEXT_MUTED,
            bg="#FFFFFF",
            activeforeground=self.DANGER,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.handle_clear_completed
        )
        self.clear_btn.pack(side=tk.RIGHT)

    def handle_add_task(self):
        """Manipula a inclusão de uma nova atividade."""
        title = self.task_entry.get().strip()
        if not title or title == self.placeholder_text:
            messagebox.showwarning("Aviso", "Por favor, digite o nome de uma tarefa antes de adicionar.")
            self.task_entry.focus_set()
            return

        try:
            self.manager.add_task(title)
            # Limpa e foca novamente
            self.task_entry.delete(0, tk.END)
            self.task_entry.configure(fg=self.TEXT_MAIN)
            self.refresh_tasks()
        except ValueError as err:
            messagebox.showerror("Erro", str(err))

    def handle_toggle_task(self, task_id: int):
        """Alterna a conclusão de uma tarefa."""
        self.manager.toggle_task_status(task_id)
        self.refresh_tasks()

    def handle_remove_task(self, task_id: int):
        """Exclui uma tarefa com confirmação."""
        task = self.manager.get_task(task_id)
        if not task:
            return

        confirm = messagebox.askyesno(
            "Excluir Tarefa",
            f"Deseja realmente remover a tarefa:\n\n\"{task.title}\"?",
            parent=self
        )
        if confirm:
            self.manager.remove_task(task_id)
            self.refresh_tasks()

    def handle_clear_completed(self):
        """Limpa todas as tarefas já concluídas."""
        summary = self.manager.get_summary()
        if summary["completed"] == 0:
            messagebox.showinfo("Informação", "Não há tarefas concluídas para limpar.")
            return

        confirm = messagebox.askyesno(
            "Limpar Concluídas",
            f"Remover todas as {summary['completed']} tarefas concluídas?",
            parent=self
        )
        if confirm:
            self.manager.clear_completed()
            self.refresh_tasks()

    def set_filter(self, filter_name: str):
        """Altera o filtro ativo e recarrega os itens exibidos."""
        self.current_filter = filter_name
        self.refresh_tasks()

    def refresh_tasks(self):
        """Recarrega os componentes visuais de acordo com o estado do TaskManager."""
        # Limpar cards anteriores
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        summary = self.manager.get_summary()
        tasks = self.manager.get_tasks(self.current_filter)

        # Atualizar textos dos botões de filtro
        self._update_filter_buttons(summary)

        # Atualizar rodapé
        self.summary_label.config(
            text=f"Total: {summary['total']}  •  Pendentes: {summary['pending']}  •  Concluídas: {summary['completed']}"
        )

        if not tasks:
            self._render_empty_state()
            return

        # Renderizar cada tarefa como um Card moderno
        for task in tasks:
            self._render_task_card(task)

    def _update_filter_buttons(self, summary: dict):
        """Atualiza a aparência e as contagens dos botões de filtro."""
        filters = [
            (self.btn_filter_all, f"Todas ({summary['total']})", "all"),
            (self.btn_filter_pending, f"Pendentes ({summary['pending']})", "pending"),
            (self.btn_filter_completed, f"Concluídas ({summary['completed']})", "completed")
        ]

        for btn, label, name in filters:
            btn.config(text=label)
            if self.current_filter == name:
                btn.config(bg=self.PRIMARY, fg="#FFFFFF", activebackground=self.PRIMARY_HOVER, activeforeground="#FFFFFF")
            else:
                btn.config(bg="#E2E8F0", fg=self.TEXT_MAIN, activebackground="#CBD5E1", activeforeground=self.TEXT_MAIN)

    def _render_empty_state(self):
        """Exibe mensagem amigável quando não há tarefas na visualização."""
        empty_frame = tk.Frame(self.scrollable_frame, bg=self.BG_COLOR, pady=60)
        empty_frame.pack(fill=tk.BOTH, expand=True)

        if self.current_filter == "completed":
            msg = "Nenhuma tarefa concluída ainda.\nComplete suas atividades para vê-las aqui!"
            icon = "🎯"
        elif self.current_filter == "pending":
            msg = "Tudo em dia!\nVocê não possui nenhuma atividade pendente no momento."
            icon = "🎉"
        else:
            msg = "Sua lista de tarefas está vazia!\nAdicione sua primeira atividade no campo acima."
            icon = "📝"

        icon_label = tk.Label(empty_frame, text=icon, font=("Segoe UI", 36), bg=self.BG_COLOR)
        icon_label.pack()

        text_label = tk.Label(
            empty_frame,
            text=msg,
            font=self.font_body,
            fg=self.TEXT_MUTED,
            bg=self.BG_COLOR,
            justify="center"
        )
        text_label.pack(pady=10)

    def _render_task_card(self, task):
        """Constrói um card visual para uma tarefa."""
        card = tk.Frame(
            self.scrollable_frame,
            bg=self.CARD_BG,
            highlightbackground="#E2E8F0" if not task.completed else "#E5E7EB",
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card.pack(fill=tk.X, pady=4)

        # Botão de Checkbox / Conclusão
        check_symbol = "✔" if task.completed else "○"
        check_fg = self.SUCCESS if task.completed else self.TEXT_MUTED
        check_bg = self.SUCCESS_BG if task.completed else "#F1F5F9"

        check_btn = tk.Button(
            card,
            text=check_symbol,
            font=("Segoe UI", 12, "bold"),
            bg=check_bg,
            fg=check_fg,
            activebackground=self.SUCCESS_BG,
            activeforeground=self.SUCCESS,
            relief="flat",
            bd=0,
            width=2,
            height=1,
            cursor="hand2",
            command=lambda tid=task.id: self.handle_toggle_task(tid)
        )
        check_btn.pack(side=tk.LEFT, padx=(0, 12))

        # Informações da Tarefa (Centro)
        center_frame = tk.Frame(card, bg=self.CARD_BG)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Título da Tarefa (com tachado se concluída)
        title_font = self.font_body_completed if task.completed else self.font_body
        title_fg = self.TEXT_MUTED if task.completed else self.TEXT_MAIN

        title_label = tk.Label(
            center_frame,
            text=task.title,
            font=title_font,
            fg=title_fg,
            bg=self.CARD_BG,
            anchor="w",
            justify="left"
        )
        title_label.pack(fill=tk.X)

        # Metadados (Data de criação e conclusão)
        meta_parts = [f"Criada: {task.created_at}"]
        if task.completed and task.completed_at:
            meta_parts.append(f"Concluída: {task.completed_at}")

        meta_label = tk.Label(
            center_frame,
            text="  •  ".join(meta_parts),
            font=self.font_sm,
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG,
            anchor="w"
        )
        meta_label.pack(fill=tk.X, pady=(2, 0))

        # Tag de Status
        if task.completed:
            status_text = "Concluída"
            status_bg = self.SUCCESS_BG
            status_fg = self.SUCCESS
        else:
            status_text = "Pendente"
            status_bg = self.PENDING_BG
            status_fg = self.PENDING_COLOR

        status_badge = tk.Label(
            card,
            text=f" {status_text} ",
            font=self.font_badge,
            bg=status_bg,
            fg=status_fg,
            padx=6,
            pady=2
        )
        status_badge.pack(side=tk.LEFT, padx=10)

        # Botão Excluir
        delete_btn = tk.Button(
            card,
            text="🗑️",
            font=("Segoe UI", 11),
            bg=self.CARD_BG,
            fg=self.DANGER,
            activebackground="#FEE2E2",
            activeforeground=self.DANGER_HOVER,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda tid=task.id: self.handle_remove_task(tid)
        )
        delete_btn.pack(side=tk.RIGHT)
