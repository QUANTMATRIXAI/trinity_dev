from __future__ import annotations
import pandas as pd
from typing import List, Dict, Any, Optional

class ValidationReport:
    """
    Collects rule outcomes.
    ok  – True if no rule has status='fail'
    rows – list of dicts (easy serialisation)
    """
    def __init__(self) -> None:
        self._rows: list[Dict[str, Any]] = []

    def add(
        self,
        check: str,
        status: str,
        msg: str = "",
        column: Optional[str] = None,
    ) -> None:
        self._rows.append(
            {"check": check, "status": status, "msg": msg, "column": column}
        )

    # convenient aliases
    def pass_(self, check: str, msg: str = "") -> None:
        self.add(check, "pass", msg)

    def warn(self, check: str, msg: str = "", column: str | None = None) -> None:
        self.add(check, "warn", msg, column)

    def fail(self, check: str, msg: str = "", column: str | None = None) -> None:
        self.add(check, "fail", msg, column)

    # ---- public API -------------------------------------------
    @property
    def ok(self) -> bool:
        return all(r["status"] != "fail" for r in self._rows)

    def rows(self) -> List[Dict[str, Any]]:
        return self._rows

    # pretty print (optional)
    def __str__(self) -> str:
        icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
        lines = [
            f"{icon[r['status']]} {r['check']}"
            + (f" ({r['column']})" if r.get("column") else "")
            + (f": {r['msg']}" if r["msg"] else "")
            for r in self._rows
        ]
        overall = "✔︎ PASS" if self.ok else "✖︎ FAIL"
        return "\n".join(lines) + f"\n— {overall} —"

# Helper functions for validators
def clean_columns(df: pd.DataFrame, rep: ValidationReport) -> None:
    ren = {c: c.strip() for c in df.columns if c != c.strip()}
    if ren:
        df.rename(columns=ren, inplace=True)
        rep.pass_("cleanup", f"renamed columns {list(ren.keys())}")

def check_missing(
    df: pd.DataFrame,
    rep: ValidationReport,
    critical: Optional[List[str]] = None,
) -> None:
    crit = set(critical or [])
    for col in df.columns:
        n = df[col].isna().sum()
        pct = (n / len(df)) * 100 if len(df) > 0 else 0
        if n:
            lvl = rep.fail if col in crit else rep.warn
            lvl("missing", f"{n} missing ({pct:.2f}%)", col)

def check_dtypes(
    df: pd.DataFrame,
    rep: ValidationReport,
    expected: Dict[str, str],
) -> None:
    for col, exp in expected.items():
        if col in df.columns and str(df[col].dtype) != exp:
            rep.warn("dtype", f"found {df[col].dtype}, expected {exp}", col)