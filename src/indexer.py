import os
import sqlite3
import fitz  # PyMuPDF
import time

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS documents 
        USING fts5(path, filename, content);
    ''')
    conn.commit()
    return conn

def extract_text_from_pdf(filepath):
    text = ""
    try:
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"⚠️ Erreur lecture {filepath}: {e}")
        return None
    return text

def index_file(db_name, filepath):
    """Indexe UN SEUL fichier."""
    conn = init_db(db_name)
    cursor = conn.cursor()
    
    # On vérifie si c'est un PDF
    if not filepath.lower().endswith(".pdf"):
        return False

    # Vérif si déjà existant
    cursor.execute("SELECT rowid FROM documents WHERE path = ?", (filepath,))
    if cursor.fetchone() is not None:
        return False # Déjà là

    print(f"📄 Indexation fichier unique : {filepath}")
    content = extract_text_from_pdf(filepath)
    
    if content:
        filename = os.path.basename(filepath)
        cursor.execute(
            "INSERT INTO documents (path, filename, content) VALUES (?, ?, ?)",
            (filepath, filename, content)
        )
        conn.commit()
        conn.close()
        return True
    return False

def index_folder(db_name, folder_path):
    """Parcourt le dossier récursivement."""
    if not os.path.exists(folder_path):
        return 0

    conn = init_db(db_name)
    cursor = conn.cursor()
    
    print(f"🔍 Scan du dossier : {folder_path} ...")
    count = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                
                cursor.execute("SELECT rowid FROM documents WHERE path = ?", (full_path,))
                if cursor.fetchone() is None:
                    print(f"   📄 Indexation : {file}")
                    content = extract_text_from_pdf(full_path)
                    if content:
                        cursor.execute(
                            "INSERT INTO documents (path, filename, content) VALUES (?, ?, ?)",
                            (full_path, file, content)
                        )
                        count += 1
                        if count % 10 == 0: conn.commit()

    conn.commit()
    conn.close()
    return count