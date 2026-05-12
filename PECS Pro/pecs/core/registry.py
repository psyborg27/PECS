from __future__ import annotations

import sqlite3
from pathlib import Path


class PECSRegistry:
    def __init__(
        self,
        project_root: str,
    ):
        self.project_root = Path(
            project_root
        )

        self.db_path = (
            self.project_root
            / "pecs"
            / "registry"
            / "objects.db"
        )

        self.conn = sqlite3.connect(
            self.db_path
        )

        self.conn.row_factory = (
            sqlite3.Row
        )

    def execute(
        self,
        sql: str,
        params=(),
    ):
        cursor = self.conn.execute(
            sql,
            params,
        )

        self.conn.commit()

        return cursor

    def fetchall(
        self,
        sql: str,
        params=(),
    ):
        return self.conn.execute(
            sql,
            params,
        ).fetchall()

    def fetchone(
        self,
        sql: str,
        params=(),
    ):
        return self.conn.execute(
            sql,
            params,
        ).fetchone()

    def objects(
        self,
        limit: int | None = None,
    ):
        sql = """
        SELECT *
        FROM objects
        ORDER BY
            recurrence_weight DESC,
            locality_confidence DESC
        """

        params = ()

        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)

        return self.fetchall(
            sql,
            params,
        )

    def localities(
        self,
        object_id: str,
    ):
        return self.fetchall(
            """
            SELECT *
            FROM object_locality
            WHERE object_id = ?
            ORDER BY locality_weight DESC
            """,
            (object_id,),
        )

    def relations(
        self,
        object_id: str,
    ):
        return self.fetchall(
            """
            SELECT *
            FROM object_relations
            WHERE source_object = ?
            ORDER BY confidence DESC
            """,
            (object_id,),
        )
