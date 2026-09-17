"""
Authentication & Semantic Employee Verification Router for TATTVA
Handles 3-Tier Semantic Employee ID authentication:
- Tier 1 (9 chars): Site Engineer (MPB260001) -> MINE_OPERATOR
- Tier 2 (10 chars): High Management / HQ (MHN2601001) -> EXECUTIVE_MANAGEMENT
- Tier 3 ('IN' prefix): Apex Board / Ministry Owner (IN26009) -> SUPER_ADMIN
"""

import base64
import json
import re
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from src.data.governance_db import MINE_CODE_MAP, governance_db, hash_pin

router = APIRouter(prefix="/auth", tags=["Role-Based Semantic Authentication"])


class LoginRequest(BaseModel):
    employee_id: str = Field(..., example="MPB260001", description="Semantic Employee ID")
    pin: str = Field(..., min_length=4, max_length=10, example="123456", description="6-digit security PIN")


class UserProfile(BaseModel):
    employee_id: str
    full_name: str
    role: str
    tier: int
    mine_id: str
    state: str
    department: str


class LoginResponse(BaseModel):
    token: str
    user: UserProfile
    message: str


def _create_token(user_dict: Dict[str, Any]) -> str:
    payload = {
        "sub": user_dict["employee_id"],
        "name": user_dict["full_name"],
        "role": user_dict["role"],
        "tier": user_dict["tier"],
        "mine_id": user_dict["mine_id"],
        "state": user_dict["state"],
        "exp": int(time.time()) + 86400 * 7,  # 7 days validity
    }
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8"))
        payload = json.loads(raw.decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def parse_semantic_id(emp_id: str) -> Dict[str, Any]:
    """
    Parses and categorizes semantic ID:
    - Tier 3: ^IN[A-Z0-9]{3,}$ (e.g. IN26009, IN20009)
    - Tier 2: ^[A-Z]{3}[0-9]{7}$ (e.g. MHN2601001) - 10 characters
    - Tier 1: ^[A-Z]{3}[0-9]{6}$ (e.g. MPB260001) - 9 characters
    """
    norm = emp_id.strip().upper()

    # Tier 3 Apex (e.g. IN26009, IN20009, IN-BOARD01)
    if re.match(r"^IN[0-9]{3,8}$", norm) or re.match(r"^IN-[A-Z0-9]{3,8}$", norm):
        return {
            "tier": 3,
            "role": "SUPER_ADMIN",
            "mine_id": "ALL",
            "state": "National",
            "mine_name": "MOIL National Grid (All Mines)",
            "default_dept": "MOIL Board / Ministry of Mines Apex",
        }

    # Tier 2 High Management (10 chars)
    if len(norm) == 10 and re.match(r"^[A-Z]{3}[0-9]{7}$", norm):
        code = norm[:3]
        mine_info = MINE_CODE_MAP.get(code, ("MOIL_HQ", "Maharashtra", "Nagpur HQ"))
        return {
            "tier": 2,
            "role": "EXECUTIVE_MANAGEMENT",
            "mine_id": mine_info[0],
            "state": mine_info[1],
            "mine_name": mine_info[2],
            "default_dept": f"{mine_info[2]} Regional Executive Directorate",
        }

    # Tier 1 Site Operations (9 chars)
    if len(norm) == 9 and re.match(r"^[A-Z]{3}[0-9]{6}$", norm):
        code = norm[:3]
        if code not in MINE_CODE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown mine code prefix '{code}'. Valid MOIL prefixes: {list(MINE_CODE_MAP.keys())}",
            )
        mine_info = MINE_CODE_MAP[code]
        return {
            "tier": 1,
            "role": "MINE_OPERATOR",
            "mine_id": mine_info[0],
            "state": mine_info[1],
            "mine_name": mine_info[2],
            "default_dept": f"{mine_info[2]} Mine Operations",
        }

    raise HTTPException(
        status_code=400,
        detail=(
            "Invalid Employee ID structure. Expected: "
            "Tier 1 (9-char site ID, e.g. MPB260001), "
            "Tier 2 (10-char HQ ID, e.g. MHN2601001), or "
            "Tier 3 (National ID starting with 'IN', e.g. IN26009)."
        ),
    )


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> Dict[str, Any]:
    norm_id = req.employee_id.strip().upper()
    parsed = parse_semantic_id(norm_id)

    emp = governance_db.get_employee(norm_id)
    if emp:
        # Check PIN
        if emp["pin_hash"] != hash_pin(req.pin):
            raise HTTPException(status_code=401, detail="Invalid 6-digit security PIN for this employee ID.")
        user_dict = emp
    else:
        # If valid semantic format and matches standard demo PINs, auto-provision
        tier = parsed["tier"]
        allowed_demo_pins = {1: ["123456"], 2: ["654321", "123456"], 3: ["999999", "123456"]}
        if req.pin.strip() not in allowed_demo_pins.get(tier, ["123456"]):
            raise HTTPException(
                status_code=401,
                detail=f"Employee '{norm_id}' is not yet in roster. Default onboarding PIN for Tier {tier} is not matched.",
            )

        # Auto-provision employee so the user experiences zero friction
        user_dict = {
            "employee_id": norm_id,
            "full_name": f"Engineer {norm_id}",
            "role": parsed["role"],
            "tier": parsed["tier"],
            "mine_id": parsed["mine_id"],
            "state": parsed["state"],
            "department": parsed["default_dept"],
            "temp_pin": req.pin.strip(),
            "created_by": "AUTO_PROVISION",
        }
        governance_db.add_employee(user_dict)
        user_dict = governance_db.get_employee(norm_id)

    token = _create_token(user_dict)
    return {
        "token": token,
        "user": {
            "employee_id": user_dict["employee_id"],
            "full_name": user_dict["full_name"],
            "role": user_dict["role"],
            "tier": user_dict["tier"],
            "mine_id": user_dict["mine_id"],
            "state": user_dict["state"],
            "department": user_dict["department"],
        },
        "message": f"Welcome, {user_dict['full_name']} ({user_dict['role']})",
    }


@router.get("/me")
def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Expired or invalid token.")
    return payload


@router.get("/presets")
def get_demo_presets() -> Dict[str, Any]:
    """Provides 1-click test credentials for evaluators."""
    return {
        "presets": [
            {
                "label": "Tier 1: Site Engineer (Balaghat Mine)",
                "employee_id": "MPB260001",
                "pin": "123456",
                "role": "MINE_OPERATOR",
                "mine": "MOIL Balaghat (Madhya Pradesh)",
                "scope": "Scoped to Balaghat Weekly Production",
            },
            {
                "label": "Tier 2: HQ General Manager (Nagpur Directorate)",
                "employee_id": "MHN2601001",
                "pin": "654321",
                "role": "EXECUTIVE_MANAGEMENT",
                "mine": "Nagpur HQ (All 10 Mines Oversight)",
                "scope": "Weekly/Monthly Compliance Matrix & Bulk Onboarding",
            },
            {
                "label": "Tier 3: Apex Authority (MOIL Board / Ministry)",
                "employee_id": "IN26009",
                "pin": "999999",
                "role": "SUPER_ADMIN",
                "mine": "National Mineral Grid",
                "scope": "Dynamic Commissioning of New Mining Leases",
            },
        ]
    }
