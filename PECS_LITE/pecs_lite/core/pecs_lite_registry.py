
from __future__ import annotations
import sqlite3
from pathlib import Path

class PECSLiteRegistry:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.db_path = (
            self.project_root
            / "pecs"
            / "registry"
            / "objects.db"
        )

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def query(self, sql: str, params=()):
        return self.conn.execute(sql, params)

    def fetchall(self, sql: str, params=()):
        return self.query(sql, params).fetchall()

    def fetchone(self, sql: str, params=()):
        return self.query(sql, params).fetchone()

    def execute(self, sql: str, params=()):
        self.query(sql, params)
        self.conn.commit()
