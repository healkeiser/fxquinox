# Built-in
import os
from pathlib import Path
import sqlite3
from typing import Dict, Optional

# Internal
from fxquinox import fxenvironment


def initialize_db(db_path: str) -> None:
    """Create the database and the table if they don't exist.

    Args:
        db_path (str): Path to the SQLite database file.
    """

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_metadata (
                folder_path TEXT PRIMARY KEY,
                creator TEXT,
                purpose TEXT,
                entity TEXT
            );
            """
        )
        conn.commit()


def upsert_folder_metadata(db_path: str, folder_path: str, creator: str, purpose: str, entity: str) -> None:
    """Insert or update metadata for a folder.

    Args:
        db_path (str): Path to the SQLite database file.
        folder_path (str): Path to the folder.
        creator (str): Creator of the folder.
        purpose (str): Purpose of the folder.
        entity (str): Entity type of the folder.
    """

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO folder_metadata (folder_path, creator, purpose, entity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(folder_path) DO UPDATE SET
                creator = excluded.creator,
                purpose = excluded.purpose,
                entity = excluded.entity
            """,
            (folder_path, creator, purpose, entity),
        )
        conn.commit()


def get_folder_metadata(db_path: str, folder_path: str) -> Optional[Dict]:
    """Get metadata for a folder.

    Args:
        db_path (str): Path to the SQLite database file.
        folder_path (str): Path to the folder.

    Returns:
        Optional[Dict]: Metadata for the folder.
    """

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT creator, purpose, entity FROM folder_metadata WHERE folder_path = ?", (folder_path,))
        row = cursor.fetchone()

    if row:
        return {"creator": row[0], "purpose": row[1], "entity": row[2]}
    else:
        return None


if __name__ == "__main__":

    folder_path = "D:/Projects/fxquinox/production/shots/000"
    creator = "fxquinox"
    purpose = "Store shot files"
    entity = "sequence"

    initialize_db(fxenvironment.FXQUINOX_METADATA_DB)
    upsert_folder_metadata(fxenvironment.FXQUINOX_METADATA_DB, folder_path, creator, purpose, entity)
    metadata = get_folder_metadata(fxenvironment.FXQUINOX_METADATA_DB, folder_path)
    print(type(metadata))
