import customtkinter as ctk
import os
import sys
import webbrowser
import tempfile
from tkinter import messagebox
from src.logger.manager import DecisionManager
from src.logger.models import Decision
from src.git_integration.git_manager import GitManager  # HF-3
from datetime import datetime

# Configuración RS Standard
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

RS_DARK = "#1A1F2E"
RS_SIDEBAR = "#131722"
RS_ORANGE = "#FF7A3D"
RS_CARD = "#242B3D"
RS_TEXT = "#E2E8F0"
RS_SUCCESS = "#4CAF50"
RS_ERROR = "#FF4B4B"
RS_BLUE = "#3D9CFF"


class RSEngineeringLoggerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RS Engineering Decision Logger - GUI")
        self.geometry("1100x700")
        self.configure(fg_color=RS_DARK)

        self.manager = DecisionManager()
        self.git_manager = GitManager()  # HF-3

        # PU-10: Confirmación de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._has_unsaved = False
        self.active_decision_id = None  # UI-3: tracking selected card

        # Layout: Sidebar y Main Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=RS_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="RS EDL", font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.new_btn = ctk.CTkButton(self.sidebar_frame, text="+ Nueva Decisión", command=self.show_registration_form,
                                    fg_color=RS_ORANGE, text_color=RS_SIDEBAR, font=ctk.CTkFont(weight="bold"), corner_radius=10)
        self.new_btn.grid(row=1, column=0, padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Buscar...", fg_color=RS_CARD, border_color="#333", corner_radius=10)
        self.search_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_decisions)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Historial", label_text_color="gray", fg_color="transparent")
        self.scrollable_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        self.decision_buttons = []
        self.load_decisions()

        # --- MAIN CONTENT CONTAINER ---
        self.main_container = ctk.CTkFrame(self, fg_color=RS_DARK, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # --- TOAST CONTAINER (overlay) ---
        self._toast_label = None

        self.show_dashboard()  # PU-6

    # ──────────────────────────────────────────────
    # PU-4: Toast Notification System
    # ──────────────────────────────────────────────

    def show_toast(self, message: str, toast_type: str = "success", duration: int = 3000):
        """Shows an auto-dismissing toast notification at the top of main content."""
        if self._toast_label:
            self._toast_label.destroy()

        colors = {
            "success": RS_SUCCESS,
            "error": RS_ERROR,
            "info": RS_BLUE,
        }
        icons = {
            "success": "✅",
            "error": "⚠️",
            "info": "ℹ️",
        }
        bg = colors.get(toast_type, RS_ORANGE)
        icon = icons.get(toast_type, "")

        self._toast_label = ctk.CTkLabel(
            self, text=f"  {icon}  {message}  ", fg_color=bg,
            text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8, height=36
        )
        self._toast_label.place(relx=0.65, rely=0.02, anchor="n")
        self.after(duration, self._dismiss_toast)

    def _dismiss_toast(self):
        if self._toast_label:
            self._toast_label.destroy()
            self._toast_label = None

    # ──────────────────────────────────────────────
    # PU-10: Close Confirmation
    # ──────────────────────────────────────────────

    def _on_close(self):
        """Asks for confirmation before closing if there are unsaved changes."""
        if self._has_unsaved:
            result = messagebox.askyesnocancel(
                "Cerrar aplicación",
                "Tienes cambios sin guardar.\n¿Deseas salir sin guardar?"
            )
            if result is None:  # Cancel
                return
            if result:  # Yes — exit
                self.destroy()
        else:
            self.destroy()

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ──────────────────────────────────────────────
    # PU-6: Dashboard
    # ──────────────────────────────────────────────

    def show_dashboard(self):
        """Shows a dashboard with decision metrics instead of plain welcome."""
        self.clear_main_container()
        self._has_unsaved = False

        dashboard_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        dashboard_frame.pack(expand=True, fill="both", padx=50, pady=40)

        # Title
        ctk.CTkLabel(dashboard_frame, text="RS ENGINEERING\nDECISION LOGGER",
                    font=ctk.CTkFont(size=32, weight="bold"), text_color=RS_ORANGE).pack(pady=(20, 5))

        ctk.CTkLabel(dashboard_frame, text="Panel de Control",
                    font=ctk.CTkFont(size=16), text_color="gray").pack(pady=(0, 30))

        # Stats
        stats = self.manager.get_stats()

        # Metrics cards row
        metrics_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=10)
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_metric_card(metrics_frame, "Total Decisiones", str(stats["total"]), RS_ORANGE, 0)
        self._create_metric_card(metrics_frame, "Críticas", str(stats["by_impact"].get("Critical", 0)), RS_ERROR, 1)
        self._create_metric_card(metrics_frame, "Media", str(stats["by_impact"].get("Medium", 0)), "#FF7A3D", 2)
        self._create_metric_card(metrics_frame, "Baja", str(stats["by_impact"].get("Low", 0)), RS_BLUE, 3)

        # Status row
        status_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=20)
        status_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_metric_card(status_frame, "Propuestas", str(stats["by_status"].get("Proposed", 0)), "#9B59B6", 0)
        self._create_metric_card(status_frame, "Aceptadas", str(stats["by_status"].get("Accepted", 0)), RS_SUCCESS, 1)
        self._create_metric_card(status_frame, "Deprecadas", str(stats["by_status"].get("Deprecated", 0)), "#95A5A6", 2)
        self._create_metric_card(status_frame, "Sustituidas", str(stats["by_status"].get("Superseded", 0)), "#E67E22", 3)

        # UI-1: Chart section
        self._draw_chart(dashboard_frame, stats)

        # Help text
        ctk.CTkLabel(dashboard_frame,
                    text="Selecciona una decisión del historial o pulsa  + Nueva Decisión  para comenzar.",
                    font=ctk.CTkFont(size=14), text_color="gray").pack(pady=20)

        # Enterprise Tools (Opción B & C)
        tools_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        tools_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(tools_frame, text="🌐 Ver Red de Dependencias", command=self.show_network_graph,
                     fg_color=RS_CARD, hover_color="#2D364A", font=ctk.CTkFont(weight="bold")).pack(side="left", expand=True, padx=5, fill="x")
                     
        ctk.CTkButton(tools_frame, text="📄 Exportar Wiki MkDocs", command=self._generate_wiki_clicked,
                     fg_color=RS_CARD, hover_color="#2D364A", font=ctk.CTkFont(weight="bold")).pack(side="left", expand=True, padx=5, fill="x")

    def _create_metric_card(self, parent, label: str, value: str, accent: str, col: int):
        card = ctk.CTkFrame(parent, fg_color=RS_CARD, corner_radius=15, border_width=1, border_color="#333")
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")

        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=36, weight="bold"),
                    text_color=accent).pack(padx=15, pady=(15, 0))
        ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11),
                    text_color="gray").pack(padx=15, pady=(0, 15))

    def _draw_chart(self, parent, stats):
        """Draws a simple native bar chart for impacts on dashboard."""
        frame = ctk.CTkFrame(parent, fg_color=RS_CARD, corner_radius=15, border_width=1, border_color="#333")
        frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame, text="Distribución de Impacto", font=ctk.CTkFont(weight="bold"), text_color=RS_ORANGE).pack(anchor="w", padx=20, pady=(15, 5))
        
        canvas = ctk.CTkCanvas(frame, bg=RS_CARD, highlightthickness=0, height=180)
        canvas.pack(fill="x", padx=20, pady=(0, 15))
        
        by_impact = stats["by_impact"]
        max_val = max(by_impact.values()) if any(by_impact.values()) else 1
        
        colors = {"Critical": RS_ERROR, "Medium": "#FF7A3D", "Low": RS_BLUE}
        labels = ["Critical", "Medium", "Low"]
        
        x_start = 60
        y_bottom = 140
        bar_width = 50
        gap = 100
        
        for i, label in enumerate(labels):
            val = by_impact.get(label, 0)
            h = (val / max_val) * 110 if max_val > 0 else 0
            
            x1 = x_start + i * (bar_width + gap)
            y1 = y_bottom - h
            x2 = x1 + bar_width
            y2 = y_bottom
            
            color = colors.get(label, RS_ORANGE)
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color, width=0)
            canvas.create_text(x1 + bar_width/2, y_bottom + 15, text=label, fill="gray", font=("Consolas", 10))
            canvas.create_text(x1 + bar_width/2, y1 - 12, text=str(val), fill="white", font=("Consolas", 12, "bold"))
    # ──────────────────────────────────────────────

    # ──────────────────────────────────────────────
    # Sidebar: Decision List
    # ──────────────────────────────────────────────

    def load_decisions(self, query=None):
        for btn in self.decision_buttons:
            btn.destroy()
        self.decision_buttons = []
        self._sidebar_buttons = {}  # Map d_id to btn widget

        decisions = self.manager.search_decisions(query) if query else self.manager.list_decisions()
        decisions.sort(key=lambda x: x.date, reverse=True)

        for d in decisions:
            # HF-5: Conditional truncation
            display_title = d.title[:25] + "..." if len(d.title) > 25 else d.title
            
            is_active = getattr(self, "active_decision_id", None) == d.id
            color = "#2D364A" if is_active else RS_CARD
            hover = "#3A455C" if is_active else "#2D364A"
            
            btn = ctk.CTkButton(self.scrollable_frame, text=f"{d.date}\n{display_title}",
                                anchor="w", fg_color=color, hover_color=hover,
                                command=lambda d_id=d.id: self.show_decision_details(d_id),
                                font=ctk.CTkFont(size=12), corner_radius=8, height=60)
            btn.pack(fill="x", pady=5, padx=5)
            self.decision_buttons.append(btn)
            self._sidebar_buttons[d.id] = btn

    def filter_decisions(self, event):
        query = self.search_entry.get()
        self.load_decisions(query)

    # ──────────────────────────────────────────────
    # Decision Detail View (PU-3: Edit/Delete, PU-5: Export)
    # ──────────────────────────────────────────────

    def show_decision_details(self, d_id):
        self.clear_main_container()
        self._has_unsaved = False
        
        self.active_decision_id = d_id
        # Update sidebar highlight
        for b_id, b in getattr(self, "_sidebar_buttons", {}).items():
            if b_id == d_id:
                b.configure(fg_color="#2D364A", hover_color="#3A455C")
            else:
                b.configure(fg_color=RS_CARD, hover_color="#2D364A")

        scroll_wrapper = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll_wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        d = self.manager.get_decision(d_id)

        # HF-1: Guard against None
        if not d:
            ctk.CTkLabel(scroll_wrapper, text="⚠️ Decisión no encontrada",
                        font=ctk.CTkFont(size=20, weight="bold"), text_color=RS_ERROR).pack(expand=True, pady=40)
            return

        # Header
        header_frame = ctk.CTkFrame(scroll_wrapper, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        date_label = ctk.CTkLabel(header_frame, text=d.date, text_color=RS_ORANGE, font=ctk.CTkFont(family="Consolas"))
        date_label.pack(anchor="w")

        # MO-1: Show dependencies in Details
        if getattr(d, "depends_on", ""):
             deps = d.depends_on.split(",")
             deps_text = ", ".join([f"ADR-{int(x.strip()):03d}" for x in deps if x.strip().isdigit()])
             if deps_text:
                  ctk.CTkLabel(header_frame, text=f"🔗 Depende de: {deps_text}", text_color=RS_BLUE, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(2, 0))

        title_label = ctk.CTkLabel(header_frame, text=d.title, font=ctk.CTkFont(size=28, weight="bold"), text_color=RS_TEXT, wraplength=700, justify="left")
        title_label.pack(anchor="w")

        # Impact & Status badges in a row
        badge_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        badge_row.pack(anchor="w", pady=5)

        impact_colors = {"Critical": RS_ERROR, "Medium": RS_ORANGE, "Low": RS_BLUE}
        badge_color = impact_colors.get(d.impact, RS_ORANGE)
        ctk.CTkLabel(badge_row, text=f" IMPACTO: {d.impact.upper()} ", fg_color=badge_color,
                    text_color="#FFFFFF", font=ctk.CTkFont(size=10, weight="bold"), corner_radius=5).pack(side="left", padx=(0, 8))

        status_colors = {"Proposed": "#9B59B6", "Accepted": RS_SUCCESS, "Deprecated": "#95A5A6", "Superseded": "#E67E22"}
        status_color = status_colors.get(d.status, RS_ORANGE)
        ctk.CTkLabel(badge_row, text=f" STATUS: {d.status.upper()} ", fg_color=status_color,
                    text_color="#FFFFFF", font=ctk.CTkFont(size=10, weight="bold"), corner_radius=5).pack(side="left", padx=(0, 8))

        if d.commit_hash and d.commit_hash not in ("Unknown", "No commits yet"):
            ctk.CTkLabel(badge_row, text=f" GIT: {d.commit_hash[:7]} ", fg_color="#555",
                        text_color="#FFFFFF", font=ctk.CTkFont(size=10, family="Consolas"), corner_radius=5).pack(side="left")

        # PU-3 + PU-5: Action buttons
        action_frame = ctk.CTkFrame(scroll_wrapper, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(action_frame, text="✏️ Editar", command=lambda: self.show_edit_form(d_id),
                      fg_color=RS_CARD, hover_color="#2D364A", text_color=RS_TEXT,
                      font=ctk.CTkFont(weight="bold"), corner_radius=8, width=120, height=35).pack(side="left", padx=(0, 8))

        ctk.CTkButton(action_frame, text="🗑️ Eliminar", command=lambda: self._confirm_delete(d_id),
                      fg_color="#3A1A1A", hover_color=RS_ERROR, text_color=RS_ERROR,
                      font=ctk.CTkFont(weight="bold"), corner_radius=8, width=120, height=35).pack(side="left", padx=(0, 8))

        ctk.CTkButton(action_frame, text="📄 Exportar HTML", command=lambda: self._export_html(d),
                      fg_color=RS_CARD, hover_color="#2D364A", text_color=RS_BLUE,
                      font=ctk.CTkFont(weight="bold"), corner_radius=8, width=150, height=35).pack(side="left")

        # Grid de Contexto y Solución
        grid_frame = ctk.CTkFrame(scroll_wrapper, fg_color="transparent")
        grid_frame.pack(fill="x", pady=10)
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        self._create_detail_card(grid_frame, "Contexto y Problema", d.context, 0, 0, RS_ORANGE)
        self._create_detail_card(grid_frame, "Solución Aplicada", d.chosen_option, 0, 1, RS_SUCCESS)

        # Justificación
        rationale_card = ctk.CTkFrame(scroll_wrapper, fg_color=RS_CARD, corner_radius=15, border_width=1, border_color="#333")
        rationale_card.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(rationale_card, text="Justificación Técnica", font=ctk.CTkFont(weight="bold", size=16), text_color=RS_ORANGE).pack(anchor="w", padx=20, pady=(15, 5))

        text_box = ctk.CTkTextbox(rationale_card, fg_color="transparent", text_color="#BBB", font=ctk.CTkFont(size=14), height=150)
        text_box.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        text_box.insert("0.0", d.rationale)
        text_box.configure(state="disabled")

    def _create_detail_card(self, parent, title, content, row, col, accent):
        frame = ctk.CTkFrame(parent, fg_color=RS_CARD, corner_radius=15, border_width=1, border_color="#333")
        frame.grid(row=row, column=col, padx=8, sticky="nsew")

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold"), text_color=accent).pack(anchor="w", padx=15, pady=(10, 5))

        label = ctk.CTkLabel(frame, text=content or "(vacío)", wraplength=350, justify="left", text_color="#BBB")
        label.pack(anchor="w", padx=15, pady=(0, 15))

    # ──────────────────────────────────────────────
    # PU-3: Delete Confirmation
    # ──────────────────────────────────────────────

    def _confirm_delete(self, d_id):
        result = messagebox.askyesno(
            "Eliminar Decisión",
            "¿Estás seguro de que deseas eliminar esta decisión?\nEsta acción no se puede deshacer."
        )
        if result:
            success = self.manager.delete_decision(d_id)
            if success:
                self.show_toast("Decisión eliminada correctamente", "success")
                self.load_decisions()
                self.show_dashboard()
            else:
                self.show_toast("Error al eliminar la decisión", "error")

    # ──────────────────────────────────────────────
    # PU-5: Export to HTML
    # ──────────────────────────────────────────────

    def _export_html(self, d: Decision):
        """Generates a professional standalone HTML report and opens it in the browser."""
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADR #{d.id:04d} - {d.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: {RS_DARK}; color: {RS_TEXT}; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 3px solid {RS_ORANGE}; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2em; color: {RS_ORANGE}; margin-bottom: 8px; }}
        .header .meta {{ color: #888; font-family: Consolas, monospace; font-size: 0.9em; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 0.75em; font-weight: bold; margin-right: 8px; color: white; text-transform: uppercase; }}
        .badge-impact {{ background: {'#FF4B4B' if d.impact == 'Critical' else '#FF7A3D' if d.impact == 'Medium' else '#3D9CFF'}; }}
        .badge-status {{ background: {'#9B59B6' if d.status == 'Proposed' else '#4CAF50' if d.status == 'Accepted' else '#95A5A6' if d.status == 'Deprecated' else '#E67E22'}; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
        .card {{ background: {RS_CARD}; border: 1px solid #333; border-radius: 15px; padding: 20px; }}
        .card h3 {{ font-size: 1em; margin-bottom: 10px; }}
        .card p {{ color: #BBB; line-height: 1.6; white-space: pre-wrap; }}
        .card-accent-orange h3 {{ color: {RS_ORANGE}; }}
        .card-accent-green h3 {{ color: #4CAF50; }}
        .full-card {{ grid-column: 1 / -1; }}
        .footer {{ text-align: center; margin-top: 40px; color: #555; font-size: 0.85em; border-top: 1px solid #333; padding-top: 20px; }}
        .footer span {{ color: {RS_ORANGE}; }}
        @media print {{ body {{ background: white; color: #222; }} .card {{ background: #f5f5f5; border-color: #ddd; }} .card p {{ color: #333; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="meta">{d.date} &bull; ADR #{d.id:04d}{f' &bull; Commit: {d.commit_hash[:7]}' if d.commit_hash and d.commit_hash not in ('Unknown', 'No commits yet') else ''}</div>
            <h1>{d.title}</h1>
            <div style="margin-top: 10px;">
                <span class="badge badge-impact">Impacto: {d.impact}</span>
                <span class="badge badge-status">Status: {d.status}</span>
            </div>
        </div>
        <div class="grid">
            <div class="card card-accent-orange">
                <h3>🔍 Contexto y Problema</h3>
                <p>{d.context}</p>
            </div>
            <div class="card card-accent-green">
                <h3>✅ Solución Aplicada</h3>
                <p>{d.chosen_option}</p>
            </div>
            <div class="card full-card card-accent-orange">
                <h3>🧠 Justificación Técnica</h3>
                <p>{d.rationale}</p>
            </div>
        </div>
        <div class="footer">
            Generado por <span>RS Engineering Decision Logger</span> &mdash; Robert Salinas &copy; {datetime.now().year}
        </div>
    </div>
</body>
</html>"""
        # Save to temp file and open
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html)
            temp_path = f.name

        webbrowser.open(f"file:///{temp_path}")
        self.show_toast(f"Exportado: ADR #{d.id:04d}", "success")

    # ──────────────────────────────────────────────
    # Registration Form (PU-2: Status, HF-2: Validation, HF-3: Git)
    # ──────────────────────────────────────────────

    def show_registration_form(self):
        self.clear_main_container()
        self._has_unsaved = True

        scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(scroll_frame, text="Registro de Decisión Técnica", font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE).pack(anchor="w", pady=(0, 20))

        # Campos
        self.entry_title = self._create_form_input(scroll_frame, "Título de la Decisión", "Ej: Migración a PostgreSQL para escalabilidad")

        # Row: Impact + Status
        row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=10)
        row_frame.grid_columnconfigure((0, 1), weight=1)

        # Impact
        impact_container = ctk.CTkFrame(row_frame, fg_color="transparent")
        impact_container.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(impact_container, text="Nivel de Impacto", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.impact_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(impact_container, values=["Low", "Medium", "Critical"], variable=self.impact_var,
                         fg_color=RS_CARD, button_color=RS_ORANGE, button_hover_color="#E66E37").pack(fill="x", pady=(5, 0))

        # PU-2: Status selector
        status_container = ctk.CTkFrame(row_frame, fg_color="transparent")
        status_container.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(status_container, text="Estado", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.status_var = ctk.StringVar(value="Accepted")
        ctk.CTkOptionMenu(status_container, values=["Proposed", "Accepted", "Deprecated", "Superseded"], variable=self.status_var,
                         fg_color=RS_CARD, button_color=RS_ORANGE, button_hover_color="#E66E37").pack(fill="x", pady=(5, 0))

        self.text_context = self._create_form_text_input(scroll_frame, "Contexto y Problema", "¿Qué está pasando? ¿Por qué necesitamos tomar esta decisión?")
        self.text_solution = self._create_form_text_input(scroll_frame, "Solución Aplicada", "¿Qué opción se eligió y cómo se implementó?")
        self.text_rationale = self._create_form_text_input(scroll_frame, "Justificación Técnica", "¿Por qué esta es la mejor opción técnica? Pros y contras.")

        # MO-1: Dependency Input
        self.entry_depends = self._create_form_input(scroll_frame, "Depende de (IDs separadas por coma)", "Ej: 1, 3")

        # Botones de Acción
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)

        ctk.CTkButton(btn_frame, text="Guardar Decisión", command=self.save_decision,
                     fg_color=RS_ORANGE, text_color=RS_SIDEBAR, font=ctk.CTkFont(weight="bold", size=14), height=45).pack(side="left", expand=True, padx=(0, 10), fill="x")

        ctk.CTkButton(btn_frame, text="Cancelar", command=self._cancel_form,
                     fg_color=RS_CARD, text_color="gray", font=ctk.CTkFont(weight="bold"), height=45).pack(side="left", expand=True, fill="x")

    # ──────────────────────────────────────────────
    # PU-3: Edit Form
    # ──────────────────────────────────────────────

    def show_edit_form(self, d_id):
        d = self.manager.get_decision(d_id)
        if not d:
            self.show_toast("Decisión no encontrada", "error")
            return

        self.clear_main_container()
        self._has_unsaved = True

        scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(scroll_frame, text=f"Editar Decisión #{d.id:04d}", font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE).pack(anchor="w", pady=(0, 20))

        self.entry_title = self._create_form_input(scroll_frame, "Título de la Decisión", "")
        self.entry_title.insert(0, d.title)

        # Row: Impact + Status
        row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=10)
        row_frame.grid_columnconfigure((0, 1), weight=1)

        impact_container = ctk.CTkFrame(row_frame, fg_color="transparent")
        impact_container.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(impact_container, text="Nivel de Impacto", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.impact_var = ctk.StringVar(value=d.impact)
        ctk.CTkOptionMenu(impact_container, values=["Low", "Medium", "Critical"], variable=self.impact_var,
                         fg_color=RS_CARD, button_color=RS_ORANGE, button_hover_color="#E66E37").pack(fill="x", pady=(5, 0))

        status_container = ctk.CTkFrame(row_frame, fg_color="transparent")
        status_container.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(status_container, text="Estado", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.status_var = ctk.StringVar(value=d.status)
        ctk.CTkOptionMenu(status_container, values=["Proposed", "Accepted", "Deprecated", "Superseded"], variable=self.status_var,
                         fg_color=RS_CARD, button_color=RS_ORANGE, button_hover_color="#E66E37").pack(fill="x", pady=(5, 0))

        self.text_context = self._create_form_text_input(scroll_frame, "Contexto y Problema", "")
        self.text_context.insert("0.0", d.context)

        self.text_solution = self._create_form_text_input(scroll_frame, "Solución Aplicada", "")
        self.text_solution.insert("0.0", d.chosen_option)

        self.text_rationale = self._create_form_text_input(scroll_frame, "Justificación Técnica", "")
        self.text_rationale.insert("0.0", d.rationale)

        # MO-1: Dependency Input
        self.entry_depends = self._create_form_input(scroll_frame, "Depende de (IDs separadas por coma)", "")
        self.entry_depends.insert(0, getattr(d, "depends_on", "") or "")

        # Botones
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)

        ctk.CTkButton(btn_frame, text="Guardar Cambios", command=lambda: self._update_decision(d_id),
                     fg_color=RS_ORANGE, text_color=RS_SIDEBAR, font=ctk.CTkFont(weight="bold", size=14), height=45).pack(side="left", expand=True, padx=(0, 10), fill="x")

        ctk.CTkButton(btn_frame, text="Cancelar", command=lambda: self.show_decision_details(d_id),
                     fg_color=RS_CARD, text_color="gray", font=ctk.CTkFont(weight="bold"), height=45).pack(side="left", expand=True, fill="x")

    def _update_decision(self, d_id):
        title = self.entry_title.get().strip()
        context = self.text_context.get("0.0", "end").strip()
        solution = self.text_solution.get("0.0", "end").strip()
        rationale = self.text_rationale.get("0.0", "end").strip()

        if not title or not context or not solution or not rationale:
            self.show_toast("Todos los campos son obligatorios", "error")
            return

        depends_on = getattr(self, "entry_depends", None)
        depends_val = depends_on.get().strip() if depends_on else ""

        data = {
            "title": title,
            "impact": self.impact_var.get(),
            "status": self.status_var.get(),
            "context": context,
            "chosen_option": solution,
            "rationale": rationale,
            "depends_on": depends_val,
        }

        updated = self.manager.update_decision(d_id, data)
        if updated:
            self._has_unsaved = False
            self.show_toast("Decisión actualizada correctamente", "success")
            self.load_decisions()
            self.show_decision_details(d_id)
        else:
            self.show_toast("Error al actualizar la decisión", "error")

    # ──────────────────────────────────────────────
    # Form Helpers
    # ──────────────────────────────────────────────

    def _create_form_input(self, parent, label, placeholder):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=label, text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color=RS_CARD, border_color="#333", height=40, corner_radius=8)
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def _create_form_text_input(self, parent, label, placeholder):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=label, text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        text = ctk.CTkTextbox(frame, fg_color=RS_CARD, border_color="#333", height=120, corner_radius=8, font=ctk.CTkFont(size=13))
        text.pack(fill="x", pady=(5, 0))
        return text

    def _cancel_form(self):
        self._has_unsaved = False
        self.show_dashboard()

    # ──────────────────────────────────────────────
    # Save Decision (HF-2: Validation, HF-3: Git, PU-2: Status)
    # ──────────────────────────────────────────────

    def save_decision(self):
        title = self.entry_title.get().strip()
        context = self.text_context.get("0.0", "end").strip()
        solution = self.text_solution.get("0.0", "end").strip()
        rationale = self.text_rationale.get("0.0", "end").strip()

        # HF-2: Full field validation
        if not title or not context or not solution or not rationale:
            self.show_toast("Todos los campos son obligatorios", "error")
            return

        depends_on = getattr(self, "entry_depends", None)
        depends_val = depends_on.get().strip() if depends_on else ""

        data = {
            "title": title,
            "impact": self.impact_var.get(),
            "context": context,
            "chosen_option": solution,
            "rationale": rationale,
            "status": self.status_var.get(),  # PU-2
            "depends_on": depends_val,
            "commit_hash": self.git_manager.get_current_commit(),  # HF-3
        }

        new_decision = self.manager.add_decision(data)
        self._has_unsaved = False
        self.show_toast(f"Decisión #{new_decision.id:04d} registrada", "success")
        self.load_decisions()
        self.show_decision_details(new_decision.id)
    def _generate_wiki_clicked(self):
        try:
            res = self.manager.generate_mkdocs_config()
            self.show_toast("Wiki MkDocs exportada correctamente", "success")
        except Exception as e:
            self.show_toast(f"Error generando Wiki: {e}", "error")

    def show_network_graph(self):
        """Displays a circular node-link graph on Canvas for dependencies."""
        self.clear_main_container()
        self._has_unsaved = False
        
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(frame, text="Red de Dependencias de Arquitectura", font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE).pack(anchor="w", pady=(0, 20))
        
        canvas = ctk.CTkCanvas(frame, bg=RS_CARD, highlightthickness=0)
        canvas.pack(fill="both", expand=True, pady=10)
        canvas.update() # For dims
        
        relations = self.manager.get_dependency_relations()
        nodes = relations["nodes"]
        edges = relations["edges"]
        
        if not nodes:
             canvas.create_text(400, 250, text="No hay decisiones registradas", fill="gray", font=("Consolas", 14))
             return
             
        import math
        # Force a geometry sync
        w = canvas.winfo_width() or 800
        h = canvas.winfo_height() or 500
        if w < 100: w = 800
        if h < 100: h = 500
        
        center_x = w / 2
        center_y = h / 2
        radius = min(w, h) * 0.35
        
        n = len(nodes)
        node_pos = {}
        node_dims = 40
        
        for i, node in enumerate(nodes):
             angle = (2 * math.pi * i) / n
             x = center_x + radius * math.cos(angle)
             y = center_y + radius * math.sin(angle)
             node_pos[node["id"]] = (x, y)
             
        for edge in edges:
             frm = edge["from"]
             to = edge["to"]
             if frm in node_pos and to in node_pos:
                  x1, y1 = node_pos[frm]
                  x2, y2 = node_pos[to]
                  canvas.create_line(x1, y1, x2, y2, fill="gray", width=2, arrow="last", arrowshape=(10, 12, 5))
                  
        for node in nodes:
             x, y = node_pos[node["id"]]
             canvas.create_oval(x - node_dims, y - node_dims, x + node_dims, y + node_dims, fill="#1A1F2E", outline=RS_ORANGE, width=2)
             canvas.create_text(x, y, text=node["title"], fill="white", font=("Consolas", 8, "bold"), justify="center")
             
        ctk.CTkButton(frame, text="Volver al Panel", command=self.show_dashboard, fg_color=RS_CARD).pack(pady=10)



if __name__ == "__main__":
    app = RSEngineeringLoggerGUI()
    app.mainloop()
