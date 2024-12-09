import sqlite3
from datetime import datetime
import json
from pathlib import Path


class Database:
    def __init__(self, db_path="data/clipper.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    markdown_path TEXT,
                    pdf_path TEXT,
                    organization TEXT,
                    tags TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create organizations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS organizations (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE,
                    description TEXT
                )
            """
            )

            conn.commit()

    def add_result(self, result_id: str, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO results (id, title, url, markdown_path, pdf_path, organization, tags, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result_id,
                    data.get("title"),
                    data.get("url"),
                    data.get("markdown_path"),
                    data.get("pdf_path"),
                    data.get("organization"),
                    json.dumps(data.get("tags", [])),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def get_results(
        self,
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        organization: str = None,
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM results WHERE 1=1"
            params = []

            if search:
                query += " AND (title LIKE ? OR url LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])

            if organization:
                query += " AND organization = ?"
                params.append(organization)

            # Get total count
            count_cursor = conn.cursor()
            count_cursor.execute(f"SELECT COUNT(*) FROM ({query})", params)
            total = count_cursor.fetchone()[0]

            # Get paginated results
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([per_page, (page - 1) * per_page])

            cursor.execute(query, params)
            results = []
            for row in cursor.fetchall():
                result = {
                    "id": row[0],
                    "title": row[1],
                    "url": row[2],
                    "markdown_path": row[3],
                    "pdf_path": row[4],
                    "organization": row[5],
                    "tags": json.loads(row[6]) if row[6] else [],
                    "timestamp": row[7],
                }
                results.append(result)

            return {"results": results, "total": total}

    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get total clips
            cursor.execute("SELECT COUNT(*) FROM results")
            total_clips = cursor.fetchone()[0]

            # Get total organizations
            cursor.execute("SELECT COUNT(*) FROM organizations")
            total_organizations = cursor.fetchone()[0]

            # Get active projects (unique organizations in results)
            cursor.execute(
                "SELECT COUNT(DISTINCT organization) FROM results WHERE organization IS NOT NULL"
            )
            active_projects = cursor.fetchone()[0]

            # Calculate storage used
            cursor.execute("SELECT markdown_path, pdf_path FROM results")
            storage_used = 0
            for row in cursor.fetchall():
                markdown_path, pdf_path = row
                if markdown_path:
                    try:
                        storage_used += Path(markdown_path).stat().st_size
                    except OSError:
                        pass
                if pdf_path:
                    try:
                        storage_used += Path(pdf_path).stat().st_size
                    except OSError:
                        pass

            storage_used_gb = round(storage_used / (1024 * 1024 * 1024), 2)

            return {
                "total_clips": total_clips,
                "total_organizations": total_organizations,
                "active_projects": active_projects,
                "storage_used": storage_used_gb,
            }

    def add_organization(self, org_id: str, name: str, description: str = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO organizations (id, name, description)
                VALUES (?, ?, ?)
            """,
                (org_id, name, description),
            )
            conn.commit()

    def get_organizations(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM organizations")
            return [
                {"id": row[0], "name": row[1], "description": row[2]}
                for row in cursor.fetchall()
            ]

    def update_result(self, result_id: str, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if result exists
            cursor.execute("SELECT id FROM results WHERE id = ?", (result_id,))
            if not cursor.fetchone():
                return None

            # Update the result
            cursor.execute(
                """
                UPDATE results 
                SET title = ?, organization = ?, tags = ?
                WHERE id = ?
            """,
                (
                    data.get("title"),
                    data.get("organization"),
                    json.dumps(data.get("tags", [])),
                    result_id,
                ),
            )
            conn.commit()
            return True

    def delete_result(self, result_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM results WHERE id = ?", (result_id,))
            if not cursor.fetchone():
                return None
            cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
            conn.commit()
            return True

    def get_tags(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tags FROM results WHERE tags IS NOT NULL")
            all_tags = set()
            for (tags_json,) in cursor.fetchall():
                if tags_json:
                    tags = json.loads(tags_json)
                    all_tags.update(tags)
            return sorted(list(all_tags))

    def get_result(self, result_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM results WHERE id = ?", (result_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "title": row[1],
                "url": row[2],
                "markdown_path": row[3],
                "pdf_path": row[4],
                "organization": row[5],
                "tags": json.loads(row[6]) if row[6] else [],
                "timestamp": row[7],
            }
