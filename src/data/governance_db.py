"""
Governance and Operational Persistence Engine for TATTVA (MOIL Limited - SIH 2026 PS 26009).
Provides self-healing SQLite database storage for:
1. Employees & 3-Tier Semantic Credentials (9-char site, 10-char HQ, 'IN' Apex)
2. Weekly Operational Production Submissions (WSR Week 1-4)
3. Dynamic Custom Mines commissioned by Apex Board Authority
4. Immutable Statutory Audit Trail
Safeguarded with automatic schema initialization and transparent fallback.
"""

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import settings

# Semantic Mine Code mapping to MOIL canonical ID
MINE_CODE_MAP = {
    "MPB": ("MOIL_BALAGHAT", "Madhya Pradesh", "Balaghat"),
    "MPU": ("MOIL_UKWA", "Madhya Pradesh", "Balaghat"),
    "MPT": ("MOIL_TIRODI", "Madhya Pradesh", "Balaghat"),
    "MPS": ("MOIL_SITAPATORE", "Madhya Pradesh", "Balaghat"),
    "MHD": ("MOIL_DONGRI_BUZURG", "Maharashtra", "Bhandara"),
    "MHC": ("MOIL_CHIKLA", "Maharashtra", "Bhandara"),
    "MHB": ("MOIL_BELDONGRI", "Maharashtra", "Nagpur"),
    "MHK": ("MOIL_KANDRI", "Maharashtra", "Nagpur"),
    "MHM": ("MOIL_MUNSAR", "Maharashtra", "Nagpur"),
    "MHG": ("MOIL_GUMGAON", "Maharashtra", "Nagpur"),
    "MHN": ("MOIL_HQ", "Maharashtra", "Nagpur HQ"),
}


def hash_pin(pin: str) -> str:
    """Returns SHA-256 hash of a 6-digit PIN with a fixed system salt."""
    salt = "moil_tattva_2026_salt_"
    return hashlib.sha256((salt + str(pin).strip()).encode("utf-8")).hexdigest()


class GovernanceDB:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            self.db_path = settings.DATA_DIR / "governance.db"
        else:
            self.db_path = db_path
        self._in_memory = False
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._in_memory:
            return sqlite3.connect(":memory:")
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception:
            # Fallback to memory if disk write is forbidden
            self._in_memory = True
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            self._create_schema(conn)
            return conn

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                tier INTEGER NOT NULL,
                mine_id TEXT NOT NULL,
                state TEXT NOT NULL,
                department TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS weekly_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mine_id TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                reporting_period TEXT NOT NULL,
                supervisor_id TEXT NOT NULL,
                planned_tonnes REAL NOT NULL,
                actual_tonnes REAL NOT NULL,
                equipment_availability_pct REAL NOT NULL,
                rainfall_mm REAL NOT NULL,
                blasting_delays_count INTEGER NOT NULL DEFAULT 0,
                maintenance_hours REAL NOT NULL DEFAULT 0.0,
                validation_status TEXT NOT NULL DEFAULT 'VERIFIED',
                notes TEXT DEFAULT '',
                ingested_at TEXT NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS custom_mines (
                mine_id TEXT PRIMARY KEY,
                mine_name TEXT NOT NULL,
                code_prefix TEXT NOT NULL,
                company TEXT NOT NULL DEFAULT 'MOIL Limited',
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                mineral TEXT NOT NULL DEFAULT 'Manganese Ore',
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                lease_area_ha REAL NOT NULL DEFAULT 100.0,
                mining_method TEXT NOT NULL DEFAULT 'Opencast',
                annual_target_tonnes REAL NOT NULL DEFAULT 50000.0,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)
        conn.commit()

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            self._create_schema(conn)
            self._seed_default_data(conn)
        finally:
            conn.close()

    def _seed_default_data(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM employees;")
        if cur.fetchone()[0] == 0:
            now = datetime.utcnow().isoformat()
            demo_users = [
                (
                    "MPB260001",
                    "Rajesh Verma",
                    "MINE_OPERATOR",
                    1,
                    "MOIL_BALAGHAT",
                    "Madhya Pradesh",
                    "Balaghat Mine Shift Operations",
                    hash_pin("123456"),
                    now,
                ),
                (
                    "MHN2601001",
                    "Dr. Ananya Sen",
                    "EXECUTIVE_MANAGEMENT",
                    2,
                    "MOIL_HQ",
                    "Maharashtra",
                    "Nagpur MOIL Headquarters Directorate",
                    hash_pin("654321"),
                    now,
                ),
                (
                    "IN26009",
                    "Shri V. K. Mehta",
                    "SUPER_ADMIN",
                    3,
                    "ALL",
                    "National",
                    "MOIL Board / Ministry of Mines Apex",
                    hash_pin("999999"),
                    now,
                ),
                (
                    "MHD260002",
                    "Sunil Gaikwad",
                    "MINE_OPERATOR",
                    1,
                    "MOIL_DONGRI_BUZURG",
                    "Maharashtra",
                    "Dongri Buzurg Pit & EMD Plant",
                    hash_pin("123456"),
                    now,
                ),
                (
                    "MPU260003",
                    "Amitabh Shukla",
                    "MINE_OPERATOR",
                    1,
                    "MOIL_UKWA",
                    "Madhya Pradesh",
                    "Ukwa Underground Mining Division",
                    hash_pin("123456"),
                    now,
                ),
            ]
            cur.executemany(
                """
                INSERT INTO employees (employee_id, full_name, role, tier, mine_id, state, department, pin_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                demo_users,
            )

            # Seed realistic weekly submissions for the 10 MOIL mines
            # Current Month: September 2026 (Month 9)
            base_submissions = [
                # Balaghat (Submitted Week 1 and Week 2)
                ("MOIL_BALAGHAT", 2026, 9, 1, "2026-W36", "MPB260001", 4200.0, 4310.0, 88.5, 35.0, 0, 8.0, "VERIFIED", "Standard opencast bench blast; quota surpassed.", now),
                ("MOIL_BALAGHAT", 2026, 9, 2, "2026-W37", "MPB260001", 4200.0, 4120.0, 84.0, 48.0, 1, 14.5, "VERIFIED", "Sub-level haul road slippery after monsoon rain.", now),
                # Dongri Buzurg (Submitted Week 1 and Week 2)
                ("MOIL_DONGRI_BUZURG", 2026, 9, 1, "2026-W36", "MHD260002", 3100.0, 3180.0, 89.0, 20.0, 0, 6.0, "VERIFIED", "Electrolytic Grade ore extraction nominal.", now),
                ("MOIL_DONGRI_BUZURG", 2026, 9, 2, "2026-W37", "MHD260002", 3100.0, 3050.0, 82.5, 30.0, 0, 10.0, "VERIFIED", "Primary crusher jaw maintenance completed.", now),
                # Ukwa (Submitted Week 1)
                ("MOIL_UKWA", 2026, 9, 1, "2026-W36", "MPU260003", 2400.0, 2350.0, 81.0, 52.0, 1, 16.0, "VERIFIED", "Underground ventilation fan auxiliary sync.", now),
                # Chikla (Submitted Week 1)
                ("MOIL_CHIKLA", 2026, 9, 1, "2026-W36", "MHC260004", 1900.0, 1920.0, 86.0, 18.0, 0, 7.5, "VERIFIED", "West section stope extraction on plan.", now),
            ]
            cur.executemany(
                """
                INSERT INTO weekly_submissions (
                    mine_id, year, month, week_number, reporting_period, supervisor_id,
                    planned_tonnes, actual_tonnes, equipment_availability_pct, rainfall_mm,
                    blasting_delays_count, maintenance_hours, validation_status, notes, ingested_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                base_submissions,
            )

            # Audit trail
            cur.execute(
                """
                INSERT INTO audit_trail (event_type, actor_id, target_entity, details, timestamp)
                VALUES ('SYSTEM_INIT', 'SYSTEM', 'DATABASE', 'Initialized TATTVA governance database with 5 demo personnel and statutory compliance baseline.', ?);
                """,
                (now,),
            )
            conn.commit()

    # --- Employee & Auth Operations ---

    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM employees WHERE employee_id = ?;", (employee_id.strip().upper(),))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def verify_credentials(self, employee_id: str, pin: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        emp = self.get_employee(employee_id)
        if not emp:
            return False, None, "Employee ID not recognized in MOIL directory."
        if emp["pin_hash"] != hash_pin(pin):
            return False, None, "Invalid 6-digit security PIN."
        return True, emp, "Authentication successful."

    def add_employee(self, employee_data: Dict[str, Any]) -> bool:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            now = datetime.utcnow().isoformat()
            cur.execute(
                """
                INSERT OR REPLACE INTO employees (employee_id, full_name, role, tier, mine_id, state, department, pin_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    employee_data["employee_id"].strip().upper(),
                    employee_data["full_name"].strip(),
                    employee_data["role"].strip(),
                    int(employee_data.get("tier", 1)),
                    employee_data["mine_id"].strip(),
                    employee_data.get("state", "MP"),
                    employee_data.get("department", "Operations"),
                    employee_data.get("pin_hash") or hash_pin(employee_data.get("temp_pin", "123456")),
                    now,
                ),
            )
            # Log audit
            cur.execute(
                """
                INSERT INTO audit_trail (event_type, actor_id, target_entity, details, timestamp)
                VALUES ('ONBOARD_EMPLOYEE', ?, ?, ?, ?);
                """,
                (
                    employee_data.get("created_by", "EXECUTIVE"),
                    employee_data["employee_id"],
                    f"Onboarded {employee_data['full_name']} ({employee_data['role']}) for mine {employee_data['mine_id']}",
                    now,
                ),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Weekly Submissions Operations ---

    def insert_weekly_submission(self, data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            now = datetime.utcnow().isoformat()
            cur.execute(
                """
                INSERT INTO weekly_submissions (
                    mine_id, year, month, week_number, reporting_period, supervisor_id,
                    planned_tonnes, actual_tonnes, equipment_availability_pct, rainfall_mm,
                    blasting_delays_count, maintenance_hours, validation_status, notes, ingested_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    data["mine_id"],
                    int(data.get("year", 2026)),
                    int(data.get("month", 9)),
                    int(data.get("week_number", 3)),
                    data.get("reporting_period", f"2026-W{int(data.get('week_number', 3)):02d}"),
                    data["supervisor_id"],
                    float(data["planned_tonnes"]),
                    float(data["actual_tonnes"]),
                    float(data["equipment_availability_pct"]),
                    float(data.get("rainfall_mm", 0.0)),
                    int(data.get("blasting_delays_count", 0)),
                    float(data.get("maintenance_hours", 0.0)),
                    data.get("validation_status", "VERIFIED"),
                    data.get("notes", ""),
                    now,
                ),
            )
            new_id = cur.lastrowid

            # Audit
            cur.execute(
                """
                INSERT INTO audit_trail (event_type, actor_id, target_entity, details, timestamp)
                VALUES ('WEEKLY_INGESTION', ?, ?, ?, ?);
                """,
                (
                    data["supervisor_id"],
                    data["mine_id"],
                    f"Logged Week {data.get('week_number')} WSR: {data['actual_tonnes']}t (Plan: {data['planned_tonnes']}t, Status: {data.get('validation_status', 'VERIFIED')})",
                    now,
                ),
            )
            conn.commit()
            return new_id
        finally:
            conn.close()

    def get_weekly_submissions(self, mine_id: Optional[str] = None, year: int = 2026, month: int = 9) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if mine_id and mine_id.upper() not in ("ALL", "MOIL_HQ"):
                cur.execute(
                    """
                    SELECT * FROM weekly_submissions
                    WHERE mine_id = ? AND year = ? AND month = ?
                    ORDER BY week_number ASC, ingested_at DESC;
                    """,
                    (mine_id.strip().upper(), year, month),
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM weekly_submissions
                    WHERE year = ? AND month = ?
                    ORDER BY mine_id ASC, week_number ASC;
                    """,
                    (year, month),
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # --- Custom Commissioned Mines Operations ---

    def commission_mine(self, mine_data: Dict[str, Any]) -> bool:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            now = datetime.utcnow().isoformat()
            cur.execute(
                """
                INSERT OR REPLACE INTO custom_mines (
                    mine_id, mine_name, code_prefix, company, state, district,
                    mineral, latitude, longitude, lease_area_ha, mining_method,
                    annual_target_tonnes, created_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    mine_data["mine_id"].strip().upper(),
                    mine_data["mine_name"].strip(),
                    mine_data["code_prefix"].strip().upper(),
                    mine_data.get("company", "MOIL Limited"),
                    mine_data["state"].strip(),
                    mine_data["district"].strip(),
                    mine_data.get("mineral", "Manganese Ore"),
                    float(mine_data["latitude"]),
                    float(mine_data["longitude"]),
                    float(mine_data.get("lease_area_ha", 100.0)),
                    mine_data.get("mining_method", "Opencast"),
                    float(mine_data.get("annual_target_tonnes", 50000.0)),
                    mine_data.get("created_by", "IN26009"),
                    now,
                ),
            )
            # Log audit
            cur.execute(
                """
                INSERT INTO audit_trail (event_type, actor_id, target_entity, details, timestamp)
                VALUES ('COMMISSION_MINE', ?, ?, ?, ?);
                """,
                (
                    mine_data.get("created_by", "IN26009"),
                    mine_data["mine_id"],
                    f"Commissioned new mining lease {mine_data['mine_name']} in {mine_data['district']}, {mine_data['state']} (Prefix: {mine_data['code_prefix']})",
                    now,
                ),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_custom_mines(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM custom_mines ORDER BY created_at DESC;")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # --- Audit Trail & Compliance Matrix Operations ---

    def get_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM audit_trail ORDER BY id DESC LIMIT ?;", (limit,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()


# Singleton instance
governance_db = GovernanceDB()
