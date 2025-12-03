import sqlite3

def search_keywords(db_name, query):
    """Recherche des mots-clés et renvoie les résultats avec un extrait."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # La requête SQL magique. 
    # snippet(...) permet de récupérer le bout de texte autour du mot trouvé.
    sql = """
        SELECT path, filename, snippet(documents, 2, '<b>', '</b>', '...', 15) 
        FROM documents 
        WHERE documents MATCH ? 
        ORDER BY rank
        LIMIT 20
    """
    
    try:
        cursor.execute(sql, (query,))
        results = cursor.fetchall()
    except sqlite3.OperationalError:
        print("❌ Erreur de syntaxe dans la recherche.")
        return []
    
    conn.close()
    return results