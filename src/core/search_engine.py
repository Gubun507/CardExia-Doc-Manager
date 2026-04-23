import sqlite3
import os
from src.core.brain_engine import BrainEngine

class SearchEngine:
    def __init__(self, db_path='cardexia_index.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(
                name, path UNINDEXED, modified_time UNINDEXED
            )
        ''')
        self.conn.commit()

    def add_documents(self, docs):
        """ Agrega un lote de documentos a la base de datos.
            docs es una lista de tuplas: (name, path, modified_time)
        """
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO documents (name, path, modified_time) 
            VALUES (?, ?, ?)
        ''', docs)
        self.conn.commit()
        
    def clear_db(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM documents')
        self.conn.commit()

    def count_documents(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM documents')
        return cursor.fetchone()[0]

    def search(self, query, limit=50):
        # El Cerebro Interno se encarga de analizar y expandir la consulta semánticamente
        fts_query = BrainEngine.build_fts5_query(query)
        
        if not fts_query:
            return []
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT name, path, modified_time 
                FROM documents 
                WHERE documents MATCH ? 
                ORDER BY rank 
                LIMIT ?
            ''', (fts_query, limit))
            return cursor.fetchall()
        except sqlite3.OperationalError:
            # En caso de sintaxis malformada de fts5 durante el tipeo
            return []
