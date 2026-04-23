import os
import sys
import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox

# Añadir src al path si ejecutamos desde raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.search_engine import SearchEngine
from src.core.indexer import FileIndexer
from src.gui.document_viewer import DocumentViewer

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class CardExiaSmartSearch(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CardExia Doc-Manager - Búsqueda Predictiva Universal")
        self.geometry("1100x700")

        # Motores Core
        self.search_engine = SearchEngine('cardexia_index.db')
        self.indexer = FileIndexer(self.search_engine)
        
        self.debounce_timer = None
        
        self._build_ui()
        self._update_status()

    def _build_ui(self):
        # Header y Barra de búsqueda
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="CardExia Doc-Manager", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        self.index_btn = ctk.CTkButton(
            self.header_frame, 
            text="⚙️ Escanear Sistema", 
            command=self.request_index_permission,
            fg_color="#D35B5B", 
            hover_color="#A94949"
        )
        self.index_btn.pack(side="right")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_type)
        
        self.entry = ctk.CTkEntry(
            self, 
            placeholder_text="Empieza a escribir para buscar (ej: Factura, .pdf, Reporte)...",
            textvariable=self.search_var,
            font=ctk.CTkFont(size=18),
            height=50
        )
        self.entry.pack(fill="x", padx=20, pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Listo. Escribe para buscar.", text_color="gray")
        self.status_label.pack(anchor="w", padx=20)

        # Resultados (Lista Scrolleable)
        self.results_frame = ctk.CTkScrollableFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    def _update_status(self):
        count = self.search_engine.count_documents()
        if self.indexer.is_indexing:
            self.status_label.configure(
                text=f"Indexando en segundo plano... ({self.indexer.total_scanned} archivos escaneados. {count} en BD)"
            )
            self.after(1000, self._update_status)
        else:
            self.status_label.configure(text=f"Listo. {count} documentos indexados en total.")

    def request_index_permission(self):
        if self.indexer.is_indexing:
            messagebox.showinfo("Información", "La indexación ya está en curso.")
            return

        # Ventana de diálogo explícita para transparencia
        resp = messagebox.askyesno(
            "Permiso de Escaneo Requerido", 
            "Para que la Búsqueda Predictiva funcione, CardExia necesita rastrear tu sistema de archivos.\n\n"
            "Solo se leerán los nombres y rutas de los archivos para crear un índice local ultra rápido.\n\n"
            "¿Deseas seleccionar una carpeta o unidad para escanear?"
        )
        
        if resp:
            # Pedir directorio
            folder = filedialog.askdirectory(title="Selecciona la carpeta o unidad a indexar")
            if folder:
                self.indexer.start_indexing(folder, callback=self.on_index_complete)
                self.index_btn.configure(state="disabled", text="Indexando...")
                self._update_status()

    def on_index_complete(self, total_scanned):
        self.index_btn.configure(state="normal", text="⚙️ Actualizar Índice")
        self._update_status()
        messagebox.showinfo("Escaneo Completo", f"Se han escaneado e indexado {total_scanned} archivos exitosamente.")
        # Refrescar búsqueda actual
        self.execute_search()

    def on_search_type(self, *args):
        # Debouncing
        if self.debounce_timer is not None:
            self.after_cancel(self.debounce_timer)
        self.debounce_timer = self.after(300, self.execute_search)

    def execute_search(self):
        query = self.search_var.get().strip()
        
        # Limpiar resultados actuales
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if len(query) < 2:
            if not query:
                self.status_label.configure(text="Escribe al menos 2 caracteres.")
            return

        results = self.search_engine.search(query, limit=100)
        
        if not results:
            lbl = ctk.CTkLabel(self.results_frame, text="No se encontraron resultados.")
            lbl.pack(pady=20)
            return

        # Mostrar resultados
        for name, path, mtime in results:
            row = ctk.CTkFrame(self.results_frame)
            row.pack(fill="x", pady=2)
            
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            name_lbl = ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(weight="bold"), anchor="w")
            name_lbl.pack(fill="x")
            
            path_lbl = ctk.CTkLabel(info_frame, text=f"{mtime} | {path}", text_color="gray", font=ctk.CTkFont(size=11), anchor="w")
            path_lbl.pack(fill="x")
            
            open_btn = ctk.CTkButton(
                row, 
                text="Abrir Lector", 
                width=100,
                command=lambda p=path: self.open_document(p)
            )
            open_btn.pack(side="right", padx=10)

    def open_document(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Error", "El archivo ya no existe en la ruta especificada.")
            return
            
        viewer = DocumentViewer(self, path)
        viewer.focus()

if __name__ == "__main__":
    app = CardExiaSmartSearch()
    app.mainloop()
