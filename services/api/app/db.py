import sqlite3
from pathlib import Path


class Database:
  def __init__(self, path: str) -> None:
    self._path = path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    self._init_schema()

  def _connect(self) -> sqlite3.Connection:
    conn = sqlite3.connect(self._path)
    conn.row_factory = sqlite3.Row
    return conn

  def _init_schema(self) -> None:
    with self._connect() as conn:
      conn.execute(
        """
        CREATE TABLE IF NOT EXISTS objects (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          image_url TEXT NOT NULL,
          width INTEGER NOT NULL,
          height INTEGER NOT NULL
        )
        """
      )

  def create(self, image_url: str, width: int, height: int) -> dict:
    with self._connect() as conn:
      cursor = conn.execute(
        "INSERT INTO objects (image_url, width, height) VALUES (?, ?, ?)",
        (image_url, width, height),
      )
      conn.commit()
      return self.get(cursor.lastrowid)

  def get(self, record_id: int) -> dict | None:
    with self._connect() as conn:
      row = conn.execute("SELECT * FROM objects WHERE id = ?", (record_id,)).fetchone()
      return dict(row) if row else None

  def list(self) -> list[dict]:
    with self._connect() as conn:
      rows = conn.execute("SELECT * FROM objects ORDER BY id").fetchall()
      return [dict(row) for row in rows]