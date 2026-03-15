import customtkinter as ctk
import os
import sys
from src.logger.manager import DecisionManager
from src.logger.models import Decision
from datetime import datetime

# Configuración RS Standard
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

RS_DARK = "#1A1F2E"
RS_SIDEBAR = "#131722"
RS_ORANGE = "#FF7A3D"
RS_CARD = "#242B3D"
RS_TEXT = "#E2E8F0"

class RSEngineeringLoggerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RS Engineering Decision Logger - GUI")
        self.geometry("1100x700")
        self.configure(fg_color=RS_DARK)

        self.manager = DecisionManager()

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

        self.show_welcome_screen()

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_main_container()
        welcome_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        welcome_frame.pack(expand=True)
        
        ctk.CTkLabel(welcome_frame, text="RS ENGINEERING\nDECISION LOGGER", 
                    font=ctk.CTkFont(size=32, weight="bold"), text_color=RS_ORANGE).pack(pady=10)
        
        ctk.CTkLabel(welcome_frame, text="Selecciona una decisión técnica del historial\no registra una nueva decisión para continuar.", 
                    font=ctk.CTkFont(size=16), text_color="gray").pack(pady=20)

    def load_decisions(self, query=None):
        for btn in self.decision_buttons:
            btn.destroy()
        self.decision_buttons = []

        decisions = self.manager.search_decisions(query) if query else self.manager.list_decisions()
        decisions.sort(key=lambda x: x.date, reverse=True)

        for d in decisions:
            btn = ctk.CTkButton(self.scrollable_frame, text=f"{d.date}\n{d.title[:25]}...", 
                                anchor="w", fg_color=RS_CARD, hover_color="#2D364A",
                                command=lambda d_id=d.id: self.show_decision_details(d_id),
                                font=ctk.CTkFont(size=12), corner_radius=8, height=60)
            btn.pack(fill="x", pady=5, padx=5)
            self.decision_buttons.append(btn)

    def filter_decisions(self, event):
        query = self.search_entry.get()
        self.load_decisions(query)

    def show_decision_details(self, d_id):
        self.clear_main_container()
        
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40, pady=40)

        d = self.manager.get_decision(d_id)

        # Header
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        date_label = ctk.CTkLabel(header_frame, text=d.date, text_color=RS_ORANGE, font=ctk.CTkFont(family="Consolas"))
        date_label.pack(anchor="w")
        
        title_label = ctk.CTkLabel(header_frame, text=d.title, font=ctk.CTkFont(size=32, weight="bold"), text_color=RS_TEXT, wraplength=700, justify="left")
        title_label.pack(anchor="w")

        # Impact Badge
        impact_colors = {"Critical": "#FF4B4B", "Medium": "#FF7A3D", "Low": "#3D9CFF"}
        badge_color = impact_colors.get(d.impact, RS_ORANGE)
        badge = ctk.CTkLabel(header_frame, text=f" IMPACTO: {d.impact.upper()} ", fg_color=badge_color, text_color=RS_SIDEBAR, font=ctk.CTkFont(size=10, weight="bold"), corner_radius=5)
        badge.pack(anchor="w", pady=5)

        # Grid de Contexto y Solución
        grid_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=20)
        grid_frame.grid_columnconfigure((0,1), weight=1)

        self.create_detail_card(grid_frame, "Contexto y Problema", d.context, 0, 0, "#FF7A3D")
        self.create_detail_card(grid_frame, "Solución Aplicada", d.chosen_option, 0, 1, "#4CAF50")

        # Justificación
        rationale_card = ctk.CTkFrame(content_frame, fg_color=RS_CARD, corner_radius=15, border_width=1, border_color="#333")
        rationale_card.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(rationale_card, text="Justificación Técnica", font=ctk.CTkFont(weight="bold", size=16), text_color=RS_ORANGE).pack(anchor="w", padx=20, pady=(15,5))
        
        text_box = ctk.CTkTextbox(rationale_card, fg_color="transparent", text_color="#BBB", font=ctk.CTkFont(size=14))
        text_box.pack(fill="both", expand=True, padx=20, pady=(0,15))
        text_box.insert("0.0", d.rationale)
        text_box.configure(state="disabled")

    def create_detail_card(self, parent, title, content, row, col, accent):
        frame = ctk.CTkFrame(parent, fg_color=RS_CARD, corner_radius=15, border_width=1, border_color="#333")
        frame.grid(row=row, column=col, padx=10, sticky="nsew")
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold"), text_color=accent).pack(anchor="w", padx=15, pady=(10,5))
        
        label = ctk.CTkLabel(frame, text=content, wraplength=350, justify="left", text_color="#BBB")
        label.pack(anchor="w", padx=15, pady=(0,15))

    def show_registration_form(self):
        self.clear_main_container()
        
        scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(scroll_frame, text="Registro de Decisión Técnica", font=ctk.CTkFont(size=24, weight="bold"), text_color=RS_ORANGE).pack(anchor="w", pady=(0,20))

        # Campos
        self.entry_title = self.create_form_input(scroll_frame, "Título de la Decisión", "Ej: Migración a PostgreSQL para escalabilidad")
        
        impact_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        impact_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(impact_frame, text="Nivel de Impacto", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.impact_var = ctk.StringVar(value="Medium")
        self.impact_menu = ctk.CTkOptionMenu(impact_frame, values=["Low", "Medium", "Critical"], variable=self.impact_var, 
                                            fg_color=RS_CARD, button_color=RS_ORANGE, button_hover_color="#E66E37")
        self.impact_menu.pack(fill="x", pady=(5,0))

        self.text_context = self.create_form_text_input(scroll_frame, "Contexto y Problema", "¿Qué está pasando? ¿Por qué necesitamos tomar esta decisión?")
        self.text_solution = self.create_form_text_input(scroll_frame, "Solución Aplicada", "¿Qué opción se eligió y cómo se implementó?")
        self.text_rationale = self.create_form_text_input(scroll_frame, "Justificación Técnica", "¿Por qué esta es la mejor opción técnica? Pros y contras.")

        # Botones de Acción
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)
        
        ctk.CTkButton(btn_frame, text="Guardar Decisión", command=self.save_decision, 
                     fg_color=RS_ORANGE, text_color=RS_SIDEBAR, font=ctk.CTkFont(weight="bold", size=14), height=45).pack(side="left", expand=True, padx=(0,10), fill="x")
        
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.show_welcome_screen, 
                     fg_color=RS_CARD, text_color="gray", font=ctk.CTkFont(weight="bold"), height=45).pack(side="left", expand=True, fill="x")

    def create_form_input(self, parent, label, placeholder):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=label, text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color=RS_CARD, border_color="#333", height=40, corner_radius=8)
        entry.pack(fill="x", pady=(5,0))
        return entry

    def create_form_text_input(self, parent, label, placeholder):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=label, text_color="gray", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        text = ctk.CTkTextbox(frame, fg_color=RS_CARD, border_color="#333", height=120, corner_radius=8, font=ctk.CTkFont(size=13))
        text.pack(fill="x", pady=(5,0))
        # Nota: CustomTkinter Textbox no tiene placeholder nativo, podríamos implementarlo pero lo dejamos limpio por ahora
        return text

    def save_decision(self):
        title = self.entry_title.get().strip()
        if not title:
            # Podríamos añadir un mensaje de error visual aquí
            return

        data = {
            "title": title,
            "impact": self.impact_var.get(),
            "context": self.text_context.get("0.0", "end").strip(),
            "chosen_option": self.text_solution.get("0.0", "end").strip(),
            "rationale": self.text_rationale.get("0.0", "end").strip(),
            "status": "Accepted"
        }
        
        new_decision = self.manager.add_decision(data)
        self.load_decisions()
        self.show_decision_details(new_decision.id)

if __name__ == "__main__":
    app = RSEngineeringLoggerGUI()
    app.mainloop()
