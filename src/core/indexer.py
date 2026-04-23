import os
import threading
import time

class FileIndexer:
    def __init__(self, search_engine):
        self.search_engine = search_engine
        self.is_indexing = False
        self.total_scanned = 0
        self._batch = []
        self.batch_size = 5000

    def start_indexing(self, root_path, callback=None):
        """Inicia el escaneo en un hilo secundario para no bloquear el GUI"""
        if self.is_indexing:
            return
            
        self.is_indexing = True
        self.total_scanned = 0
        self.search_engine.clear_db()
        
        thread = threading.Thread(target=self._scan_directory, args=(root_path, callback))
        thread.daemon = True
        thread.start()

    def _scan_directory(self, root_path, callback):
        try:
            self._recursive_scan(root_path)
            # Flush de los restantes
            if self._batch:
                self.search_engine.add_documents(self._batch)
                self._batch.clear()
        finally:
            self.is_indexing = False
            if callback:
                callback(self.total_scanned)

    def _recursive_scan(self, path):
        if not self.is_indexing:
            return

        try:
            with os.scandir(path) as it:
                for entry in it:
                    if not self.is_indexing:
                        break
                        
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            self._recursive_scan(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            stat = entry.stat()
                            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                            
                            self._batch.append((entry.name, entry.path, mtime))
                            self.total_scanned += 1
                            
                            if len(self._batch) >= self.batch_size:
                                self.search_engine.add_documents(self._batch)
                                self._batch.clear()
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        except (PermissionError, FileNotFoundError, OSError):
            # Se ignora silenciosamente carpetas restringidas
            pass

    def stop_indexing(self):
        self.is_indexing = False
