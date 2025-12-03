import tkinter as tk
from tkinter import ttk, messagebox, filedialog # <--- On ajoute filedialog
import os
import threading
from src import searcher, indexer

# --- CONFIGURATION ---
DB_NAME = "medical_index.db"

class MedicalSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Doc Search - V2")
        self.root.geometry("900x600")

        # --- 1. Zone de Recherche (Haut) ---
        frame_top = tk.Frame(root, pady=10, padx=10, bg="#e1e1e1")
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="🔍", bg="#e1e1e1", font=("Arial", 14)).pack(side=tk.LEFT)
        
        self.entry_search = tk.Entry(frame_top, font=("Arial", 12))
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.entry_search.bind("<Return>", self.perform_search)

        btn_search = tk.Button(frame_top, text="CHERCHER", command=self.perform_search, bg="#007bff", fg="white", font=("Arial", 10, "bold"))
        btn_search.pack(side=tk.LEFT)

        # --- 2. Zone Résultats (Milieu) ---
        frame_results = tk.Frame(root, padx=10, pady=5)
        frame_results.pack(fill=tk.BOTH, expand=True)

        columns = ("filename", "snippet", "path")
        self.tree = ttk.Treeview(frame_results, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("filename", text="Fichier")
        self.tree.column("filename", width=150, anchor="w")
        
        self.tree.heading("snippet", text="Contexte")
        self.tree.column("snippet", width=600, anchor="w")
        
        # On affiche le chemin maintenant pour savoir d'où ça vient
        self.tree.heading("path", text="Emplacement") 
        self.tree.column("path", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(frame_results, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.open_file)

        # --- 3. Zone d'Actions (Bas) ---
        frame_bottom = tk.Frame(root, pady=10, padx=10, bg="#333")
        frame_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = tk.Label(frame_bottom, text="Prêt", bg="#333", fg="white", anchor="w")
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bouton Ajouter un fichier unique
        btn_add_file = tk.Button(frame_bottom, text="📄 Ajouter un fichier", command=self.select_single_file)
        btn_add_file.pack(side=tk.RIGHT, padx=5)

        # Bouton Ajouter un dossier entier
        btn_add_folder = tk.Button(frame_bottom, text="📂 Ajouter un dossier", command=self.select_folder)
        btn_add_folder.pack(side=tk.RIGHT, padx=5)

    # --- LOGIQUE ---

    def perform_search(self, event=None):
        query = self.entry_search.get()
        if not query.strip(): return

        for item in self.tree.get_children(): self.tree.delete(item)

        results = searcher.search_keywords(DB_NAME, query)
        self.lbl_status.config(text=f"{len(results)} documents trouvés pour '{query}'")
        
        for path, filename, snippet in results:
            clean_snippet = snippet.replace("<b>", "").replace("</b>", "").replace("\n", " ")
            self.tree.insert("", tk.END, values=(filename, clean_snippet, path))

    def open_file(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        item = self.tree.item(selected_item)
        file_path = item['values'][2]
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir : {e}")

    # --- NOUVELLES FONCTIONS DE SÉLECTION ---

    def select_folder(self):
        """Ouvre une fenêtre pour choisir un dossier"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            # On lance l'indexation dans un thread séparé pour ne pas geler l'appli
            self.lbl_status.config(text=f"Indexation de {folder_selected} en cours...")
            threading.Thread(target=self.run_folder_index, args=(folder_selected,)).start()

    def select_single_file(self):
        """Ouvre une fenêtre pour choisir un fichier PDF"""
        file_selected = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_selected:
            self.lbl_status.config(text=f"Lecture de {os.path.basename(file_selected)}...")
            threading.Thread(target=self.run_file_index, args=(file_selected,)).start()

    def run_folder_index(self, folder):
        count = indexer.index_folder(DB_NAME, folder)
        self.lbl_status.config(text=f"✅ Terminé ! {count} fichiers ajoutés depuis le dossier.")

    def run_file_index(self, filepath):
        success = indexer.index_file(DB_NAME, filepath)
        if success:
            self.lbl_status.config(text="✅ Fichier ajouté à la base de données !")
        else:
            self.lbl_status.config(text="⚠️ Fichier déjà présent ou erreur.")

def launch():
    root = tk.Tk()
    app = MedicalSearchApp(root)
    root.mainloop()