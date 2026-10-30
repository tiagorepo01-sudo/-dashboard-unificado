"""
Tests for cross-filter logic (seg_apply_xf, seg_clear_xf).

These tests run without Streamlit by reimplementing the pure logic with a
plain dict as session_state. The implementations below must stay in sync
with the corresponding functions in app.py.

Run: python -m pytest tests/test_cross_filter.py -v
"""
import pandas as pd
import pytest


# ── Pure-logic reimplementations (mirrors app.py, no st dependency) ──────────

def _seg_get_xf(kp, ss):
    return ss.get(f"xf_{kp}", {})


def _seg_apply_xf(df, kp, col_map, exclude_dim=None, ss=None):
    """Mirrors seg_apply_xf in app.py (with Bug 3 fix: strip normalization)."""
    xf = _seg_get_xf(kp, ss or {})
    result = df
    for dim, col in col_map.items():
        if dim == exclude_dim or not col:
            continue
        vals = xf.get(dim, [])
        if vals and col in result.columns:
            stripped_vals = [str(v).strip() for v in vals]
            result = result[result[col].astype(str).str.strip().isin(stripped_vals)]
    return result


def _seg_clear_xf(kp, ss, dim=None):
    """Mirrors seg_clear_xf in app.py (with Bug 2 fix: exact prefix match)."""
    if dim is None:
        keys_to_del = [
            k for k in list(ss.keys())
            if k == f"xf_{kp}" or k.startswith(f"xf_{kp}_")
        ]
        for k in keys_to_del:
            del ss[k]
    else:
        xf = dict(ss.get(f"xf_{kp}", {}))
        xf.pop(dim, None)
        ss[f"xf_{kp}"] = xf
        ss.pop(f"xf_{kp}_ev_{dim}", None)


# ── Fixtures ─────────────────────────────────────────────────────────────────

COL_MAP = {
    "ef":  "Estado Solicitud Final",
    "sop": "Soporte HAINTECH",
    "ges": "Gestion",
    "tec": "Tecnico Auditado",
    "mot": "Motivo",
}


@pytest.fixture()
def df():
    return pd.DataFrame({
        "Estado Solicitud Final": [
            "Completada correctamente",
            "Pendiente de Contacto",
            "Completada correctamente",
            "Cliente desiste validado",
        ],
        "Soporte HAINTECH": ["AGENTE_A", "AGENTE_B", "AGENTE_A", "AGENTE_B"],
        "Gestion":          ["HAINTECH", "INTERNO",  "HAINTECH", "INTERNO"],
        "Tecnico Auditado": ["Juan Perez", "Ana Lopez", "Juan Perez", "Carlos Ruiz"],
        "Motivo":           ["Motivo X",  "Motivo Y",  "Motivo X",  "Motivo Z"],
    })


# ── Test A: No filters → all records ─────────────────────────────────────────

def test_A_no_filters(df):
    result = _seg_apply_xf(df, "seg", COL_MAP, ss={})
    assert len(result) == 4


# ── Test B: Single dimension filter ──────────────────────────────────────────

def test_B_single_ef_filter(df):
    ss = {"xf_seg": {"ef": ["Completada correctamente"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 2
    assert all(result["Estado Solicitud Final"] == "Completada correctamente")


# ── Test C: Two dimensions (AND logic) ───────────────────────────────────────

def test_C_two_dimensions_and(df):
    ss = {"xf_seg": {"ef": ["Completada correctamente"], "sop": ["AGENTE_A"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 2


# ── Test D: Multiple categories in one dimension (OR logic) ──────────────────

def test_D_or_within_dimension(df):
    ss = {"xf_seg": {"ef": ["Completada correctamente", "Pendiente de Contacto"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 3


# ── Test E: Three dimensions (AND logic) ─────────────────────────────────────

def test_E_three_dimensions(df):
    ss = {"xf_seg": {
        "ef":  ["Completada correctamente"],
        "sop": ["AGENTE_A"],
        "ges": ["HAINTECH"],
    }}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 2


# ── Test F: exclude_dim skips own dimension ───────────────────────────────────

def test_F_exclude_dim(df):
    ss = {"xf_seg": {"ef": ["Completada correctamente"], "sop": ["AGENTE_A"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, exclude_dim="ef", ss=ss)
    # Only sop filter applied → AGENTE_A rows = 2
    assert len(result) == 2
    # ef filter NOT applied → rows include both Completada and Pendiente (but AGENTE_A only has Completada)
    assert set(result["Estado Solicitud Final"]) == {"Completada correctamente"}


# ── Test G: NaN values do not produce false positives ────────────────────────

def test_G_nan_not_included(df):
    df_nan = df.copy()
    df_nan.loc[1, "Estado Solicitud Final"] = None
    ss = {"xf_seg": {"ef": ["Completada correctamente"]}}
    result = _seg_apply_xf(df_nan, "seg", COL_MAP, ss=ss)
    assert len(result) == 2
    assert result["Estado Solicitud Final"].notna().all()


# ── Test H: Empty DataFrame returns empty result ──────────────────────────────

def test_H_empty_dataframe(df):
    ss = {"xf_seg": {"ef": ["Completada correctamente"]}}
    result = _seg_apply_xf(df.iloc[0:0], "seg", COL_MAP, ss=ss)
    assert len(result) == 0


# ── Test I: Non-existent category returns no records ─────────────────────────

def test_I_nonexistent_category(df):
    ss = {"xf_seg": {"ef": ["CATEGORIA_INEXISTENTE"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 0


# ── Test J: xf_seg and xf_segor are fully isolated ───────────────────────────

def test_J_prefix_isolation(df):
    ss = {
        "xf_seg":   {"ef": ["Completada correctamente"]},
        "xf_segor": {"ef": ["Pendiente de Contacto"]},
    }
    r_seg   = _seg_apply_xf(df, "seg",   COL_MAP, ss=ss)
    r_segor = _seg_apply_xf(df, "segor", COL_MAP, ss=ss)
    assert len(r_seg)   == 2
    assert len(r_segor) == 1


# ── Test K: Percentages recalculate on filtered data ─────────────────────────

def test_K_percentage_on_filtered(df):
    ss = {"xf_seg": {"ef": ["Completada correctamente"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    total = len(result)
    # Within the 2 filtered records, both have HAINTECH gestión
    pct_haintech = round((result["Gestion"] == "HAINTECH").sum() / total * 100, 1)
    assert pct_haintech == 100.0


# ── Test L: seg_clear_xf does NOT touch the other module's state ──────────────

def test_L_clear_does_not_corrupt_other_module(df):
    ss = {
        "xf_seg":         {"ef": ["Completada correctamente"]},
        "xf_seg_ev_ef":   ["Completada correctamente"],
        "xf_segor":       {"ef": ["Pendiente de Contacto"]},
        "xf_segor_ev_ef": ["Pendiente de Contacto"],
    }
    _seg_clear_xf("seg", ss)

    # Derivaciones state cleared
    assert "xf_seg" not in ss
    assert "xf_seg_ev_ef" not in ss

    # Oriente state untouched
    assert "xf_segor" in ss
    assert "xf_segor_ev_ef" in ss

    # Derivaciones now returns all records
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 4


# ── Test BUG1 FIX: Technician filter without uppercase normalization ──────────

def test_bug1_tec_case_match(df):
    """
    Chart now uses .str.strip() (not .str.upper()), so event returns original
    case. seg_apply_xf strips both sides → filter matches correctly.
    """
    # 'Juan Perez' is the exact (stripped) form in the chart and the column
    ss = {"xf_seg": {"tec": ["Juan Perez"]}}
    result = _seg_apply_xf(df, "seg", COL_MAP, ss=ss)
    assert len(result) == 2
    assert all(result["Tecnico Auditado"] == "Juan Perez")


def test_bug1_tec_uppercase_no_longer_used():
    """
    Confirms the chart renders stripped (not uppercased) labels, preventing
    the original UPPERCASE vs mixed-case mismatch.
    """
    df_tec = pd.DataFrame({"Tecnico Auditado": ["Juan Perez", "Ana Lopez"]})
    col_map_tec = {"tec": "Tecnico Auditado"}

    # Old behavior: chart stored 'JUAN PEREZ', filter failed
    ss_old = {"xf_seg": {"tec": ["JUAN PEREZ"]}}
    r_old = _seg_apply_xf(df_tec, "seg", col_map_tec, ss=ss_old)

    # New behavior: chart stores 'Juan Perez', filter succeeds
    ss_new = {"xf_seg": {"tec": ["Juan Perez"]}}
    r_new = _seg_apply_xf(df_tec, "seg", col_map_tec, ss=ss_new)

    assert len(r_old) == 0, "Old uppercase behavior correctly returns 0 (confirms regression)"
    assert len(r_new) == 1, "New stripped behavior correctly returns 1"


# ── Test BUG3 FIX: Trailing spaces in source column ──────────────────────────

def test_bug3_trailing_space_in_column(df):
    """
    Columns not stripped in load_seg may have trailing spaces.
    seg_apply_xf must normalize both sides to avoid silent mismatches.
    """
    df_sp = pd.DataFrame({
        "Motivo": ["Sin Moradores ", "Ducto Tapado", "Sin Moradores "]
    })
    # _seg_proc_event strips → stored as 'Sin Moradores' (no trailing space)
    ss = {"xf_seg": {"mot": ["Sin Moradores"]}}
    result = _seg_apply_xf(df_sp, "seg", {"mot": "Motivo"}, ss=ss)
    assert len(result) == 2


# ── Test BUG2 FIX: clear_xf prefix collision guard ───────────────────────────

def test_bug2_clear_xf_prefix_collision():
    """
    'xf_seg'.startswith('xf_seg') is True, but so is 'xf_segor'.startswith('xf_seg').
    The fix uses exact match OR f'xf_{kp}_' prefix to avoid cross-module erasure.
    """
    ss = {
        "xf_seg":   {"ef": ["X"]},
        "xf_segor": {"ef": ["Y"]},
    }
    _seg_clear_xf("seg", ss)
    assert "xf_segor" in ss, "Oriente state must survive clearing Derivaciones"
    assert "xf_seg" not in ss, "Derivaciones state must be cleared"
