import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ghostdroid.db")


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db()
        self._create_tables()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                device_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT
            );
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_serial TEXT UNIQUE,
                model TEXT,
                android_version TEXT,
                api_level INTEGER,
                security_patch TEXT,
                battery_level INTEGER,
                usb_debugging INTEGER DEFAULT 0,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                risk_score REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                module_name TEXT,
                finding_type TEXT,
                severity TEXT,
                description TEXT,
                details TEXT,
                timestamp TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                level TEXT,
                module TEXT,
                message TEXT,
                timestamp TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                version TEXT,
                description TEXT,
                risk_level TEXT,
                enabled INTEGER DEFAULT 1,
                last_run TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                report_type TEXT,
                format TEXT,
                path TEXT,
                created_at TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    def add_device(self, device_data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO devices 
            (device_serial, model, android_version, api_level, security_patch, 
             battery_level, usb_debugging, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            device_data.get("serial"),
            device_data.get("model"),
            device_data.get("android_version"),
            device_data.get("api_level"),
            device_data.get("security_patch"),
            device_data.get("battery_level"),
            1 if device_data.get("usb_debugging") else 0,
            now
        ))
        conn.commit()
        conn.close()
        return 1

    def create_session(self, session_id: str, device_id: str = None) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, device_id, start_time, status)
            VALUES (?, ?, ?, 'active')
        """, (session_id, device_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return session_id

    def end_session(self, session_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions SET end_time = ?, status = 'closed'
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        conn.commit()
        conn.close()

    def add_finding(self, session_id: str, module_name: str, finding_type: str,
                    severity: str, description: str, details: str = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO findings (session_id, module_name, finding_type, severity, 
                                  description, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, module_name, finding_type, severity, description,
              details, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def add_log(self, session_id: str, level: str, module: str, message: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (session_id, level, module, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, level, module, message, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_devices(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices ORDER BY last_seen DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_sessions(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_findings(self, session_id: str = None) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if session_id:
            cursor.execute("SELECT * FROM findings WHERE session_id = ? ORDER BY timestamp DESC", (session_id,))
        else:
            cursor.execute("SELECT * FROM findings ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_logs(self, session_id: str = None, level: str = None) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM logs WHERE 1=1"
        params = []
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if level:
            query += " AND level = ?"
            params.append(level)
        query += " ORDER BY timestamp DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_reports(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
