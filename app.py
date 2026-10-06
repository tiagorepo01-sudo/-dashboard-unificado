import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Panel Unificado · HAINTECH",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&family=Barlow+Condensed:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Work Sans', sans-serif; }
.stApp { background-color: #07070F; }
section[data-testid="stSidebar"] { background-color: #0C0C18; border-right: 1px solid #1C1C2C; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 1rem 1rem 1rem !important; }
.dash-header {
    background: #0A0A16; padding: 14px 20px;
    display: flex; align-items: center; gap: 20px;
    margin: 0 -1rem 1.2rem -1rem;
}
.logo-box {
    padding: 6px 16px;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px; font-weight: 700; color: white; letter-spacing: 1px;
}
.header-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px; font-weight: 700; color: white; letter-spacing: 1px;
}
.header-sub { font-size: 11px; color: #6A6A85; margin-top: 2px; }
.kpi-grid { display: flex; gap: 8px; margin-bottom: 14px; }
.kpi-card {
    flex: 1; background: #0D0D1A;
    border: 1px solid #1C1C2C; border-top: 3px solid; border-left: 3px solid;
    padding: 12px 14px 10px; position: relative;
}
.kpi-value { font-family: 'Barlow Condensed', sans-serif; font-size: 38px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.kpi-label { font-size: 10px; color: #6A6A85; letter-spacing: 0.08em; text-transform: uppercase; }
.kpi-dot { width: 8px; height: 8px; border-radius: 50%; position: absolute; bottom: 8px; right: 8px; }
.panel {
    background: #0D0D1A; border: 1px solid #1C1C2C;
    border-top: 3px solid; border-left: 3px solid;
    padding: 14px 16px; margin-bottom: 10px;
}
.panel-title { font-family: 'Barlow Condensed', sans-serif; font-size: 13px; font-weight: 600; color: white; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 2px; }
.panel-sub { font-size: 10px; color: #353545; margin-bottom: 10px; }
.sidebar-section { font-family: 'Barlow Condensed', sans-serif; font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; padding: 8px 0 4px; border-bottom: 1px solid #1C1C2C; margin-bottom: 8px; }
.dash-footer { background: #090914; border-top: 2px solid; padding: 8px 20px; font-size: 9px; color: #2E2E40; display: flex; justify-content: space-between; margin: 1rem -1rem 0; }
.rank-panel { background: #0D0D1A; border: 1px solid #1C1C2C; border-top: 3px solid; border-left: 3px solid; padding: 14px 16px; margin-bottom: 10px; }
.rank-row { display: flex; align-items: center; gap: 10px; padding: 7px 10px; margin-bottom: 4px; border-radius: 4px; background: #0A0A16; border: 1px solid #1C1C2C; }
.rank-pos { font-family: 'Barlow Condensed', sans-serif; font-size: 15px; font-weight: 700; min-width: 28px; text-align: center; }
.rank-name { flex: 1; font-size: 12px; color: #D0D0E0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-bar-wrap { width: 60px; height: 5px; background: #1C1C2C; border-radius: 3px; overflow: hidden; }
.rank-bar-fill { height: 100%; border-radius: 3px; }
.rank-metric { font-family: 'Barlow Condensed', sans-serif; font-size: 13px; font-weight: 700; min-width: 42px; text-align: right; }
.rank-metric-sm { font-size: 10px; color: #4A4A6A; min-width: 38px; text-align: right; }
</style>
""", unsafe_allow_html=True)

# ── SHARED HELPERS ────────────────────────────────────────────────────────────
CHART_BG    = "#0D0D1A"
GRID_COLOR  = "#1C1C2C"
TEXT_COLOR  = "#8A8A9A"
FONT_FAMILY = "Work Sans"

def chart_layout(fig, height=260):
    fig.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY, size=11),
        margin=dict(l=8, r=8, t=14, b=8), height=height,
        legend=dict(bgcolor=CHART_BG, bordercolor=GRID_COLOR, borderwidth=1,
                    font=dict(size=10), orientation="h",
                    yanchor="bottom", y=-0.28, xanchor="left", x=0),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(size=10)),
    )
    return fig

def rank_color(pct):
    if pct >= 60: return "#0F9B8E"
    if pct >= 40: return "#BA7517"
    return "#C83050"

def rank_pos_html(pos):
    if pos == 1: return '<span class="rank-pos" style="color:#FFD700">🥇</span>'
    if pos == 2: return '<span class="rank-pos" style="color:#C0C0C0">🥈</span>'
    if pos == 3: return '<span class="rank-pos" style="color:#CD7F32">🥉</span>'
    return f'<span class="rank-pos" style="color:#353550">{pos}</span>'

def groupby_comp(df, group_col, comp_col):
    result = pd.DataFrame({"Total": df.groupby(group_col).size()}).reset_index()
    comp_counts = df.groupby(group_col)[comp_col].apply(lambda x: (x == "Si").sum()).reset_index()
    comp_counts.columns = [group_col, "Completadas"]
    result = result.merge(comp_counts, on=group_col, how="left")
    result["No_Comp"]  = result["Total"] - result["Completadas"]
    result["Pct_Comp"] = (result["Completadas"] / result["Total"] * 100).round(1)
    return result.fillna(0)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 · GESTIÓN NPS · CLARO
# ══════════════════════════════════════════════════════════════════════════════
NPS_URL = "https://docs.google.com/spreadsheets/d/10Gkvo98fO-aLa5FKLdDNR9Iv0OLm3r6POejykHdkGkM/export?format=csv&gid=1940977728"
NPS_ACCENT = "#C8102E"

NPS_AREA_COLORS = {
    "Tecnico": "#0F9B8E", "Cliente": "#7F77DD", "Soporte Tecnico": "#BA7517",
    "Comercial": "#C83050", "Redes": "#378ADD", "Sistema": "#888780",
    "No se Puede determinar": "#4A4A5A", "Tecnico / Comercial": "#D85A30",
}
NPS_CONTACT_COLORS = {"Contactado": "#0F9B8E", "No Contactado": "#C83050", "Intento 3": "#BA7517"}

@st.cache_data(ttl=60, show_spinner="Cargando datos NPS…")
def load_nps():
    df = pd.read_csv(NPS_URL)
    rename_map = {}
    for col in df.columns:
        s = col.strip()
        if s == "Unnamed: 0":       rename_map[col] = "Fecha"
        elif s == "Unnamed: 2":     rename_map[col] = "Asignación"
        elif s.startswith("Asignaci"): rename_map[col] = "Soporte"
    if rename_map:
        df = df.rename(columns=rename_map)
    df.columns = [c.strip() if c not in ["Fecha","Asignación","Soporte"] else c for c in df.columns]
    for col in ["Contactado","Asignación","Soporte","Tipo_Red","Zona"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df["Dia"] = df["Fecha"].dt.day
    if "Semana_Actual" in df.columns:
        df["Semana_Actual"] = pd.to_numeric(df["Semana_Actual"], errors="coerce")
    return df

def soporte_metrics_nps(df):
    grp = df.groupby("Soporte")
    result = pd.DataFrame({"Total": grp.size()}).reset_index()
    for estado, col_name in [("Contactado","Contactados"),("No Contactado","No_Contactados"),("Intento 3","Intento3")]:
        counts = grp["Contactado"].apply(lambda x: (x == estado).sum()).reset_index()
        counts.columns = ["Soporte", col_name]
        result = result.merge(counts, on="Soporte", how="left")
    result["Pct_Efect"]  = (result["Contactados"]    / result["Total"] * 100).round(1)
    result["Pct_NoCont"] = (result["No_Contactados"] / result["Total"] * 100).round(1)
    result["Pct_Int3"]   = (result["Intento3"]        / result["Total"] * 100).round(1)
    return result.fillna(0)

def render_nps(df):
    total       = len(df)
    contactados = (df["Contactado"] == "Contactado").sum() if "Contactado" in df.columns else 0
    no_contact  = (df["Contactado"] == "No Contactado").sum() if "Contactado" in df.columns else 0
    intento3    = (df["Contactado"] == "Intento 3").sum() if "Contactado" in df.columns else 0
    pct_efect   = round(contactados / total * 100, 1) if total else 0

    st.markdown(f"""
    <div class="dash-header" style="border-bottom:3px solid {NPS_ACCENT}">
      <div class="logo-box" style="background:{NPS_ACCENT}">Claro</div>
      <div>
        <div class="header-title">GESTIÓN NPS</div>
        <div class="header-sub">PANEL DE CONTROL · MAYO 2026 · {total} casos filtrados</div>
      </div>
    </div>""", unsafe_allow_html=True)

    kpi_color = rank_color(pct_efect)
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card" style="border-color:{NPS_ACCENT}"><div class="kpi-value" style="color:{NPS_ACCENT}">{total}</div><div class="kpi-label">Total asignados</div><div class="kpi-dot" style="background:{NPS_ACCENT}"></div></div>
      <div class="kpi-card" style="border-color:#0F9B8E"><div class="kpi-value" style="color:#0F9B8E">{contactados}</div><div class="kpi-label">Contactados</div><div class="kpi-dot" style="background:#0F9B8E"></div></div>
      <div class="kpi-card" style="border-color:#C83050"><div class="kpi-value" style="color:#C83050">{no_contact}</div><div class="kpi-label">No contactados</div><div class="kpi-dot" style="background:#C83050"></div></div>
      <div class="kpi-card" style="border-color:{kpi_color}"><div class="kpi-value" style="color:{kpi_color}">{pct_efect}%</div><div class="kpi-label">% Efectividad</div><div class="kpi-dot" style="background:{kpi_color}"></div></div>
      <div class="kpi-card" style="border-color:#BA7517"><div class="kpi-value" style="color:#BA7517">{intento3}</div><div class="kpi-label">Intento 3</div><div class="kpi-dot" style="background:#BA7517"></div></div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.1, 1.6, 1.3])
    p_style = f'style="border-color:{NPS_ACCENT}"'

    with col1:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Registro semanal</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Semanas seleccionadas</div>', unsafe_allow_html=True)
        if not df.empty and "Semana_Actual" in df.columns and "Contactado" in df.columns:
            pivot = df.groupby(["Semana_Actual","Contactado"]).size().unstack(fill_value=0).reset_index().sort_values("Semana_Actual")
            for c in ["Contactado","No Contactado","Intento 3"]:
                if c not in pivot.columns: pivot[c] = 0
            pivot["Total"] = pivot[["Contactado","No Contactado","Intento 3"]].sum(axis=1)
            fig = go.Figure()
            for cat in ["Contactado","No Contactado","Intento 3"]:
                fig.add_trace(go.Bar(name=cat, x=pivot["Semana_Actual"].astype(str), y=pivot[cat],
                    marker_color=NPS_CONTACT_COLORS.get(cat,"#888"),
                    text=pivot[cat], textposition="inside", textfont=dict(size=10, color="white")))
            fig.update_layout(barmode="stack")
            chart_layout(fig, height=230); fig.update_xaxes(title_text="Semana")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            tbl = pivot[["Semana_Actual","Contactado","No Contactado","Intento 3","Total"]].copy()
            tbl.columns = ["Sem","Contact.","No Cont.","Int.3","Total"]
            st.dataframe(tbl.set_index("Sem"), width="stretch", height=110)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Árbol de causas · contactados</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Distribución por área y etapas</div>', unsafe_allow_html=True)
        df_cont = df[df["Contactado"] == "Contactado"].copy() if "Contactado" in df.columns else pd.DataFrame()
        tab_bar, tab_sun = st.tabs(["Por área", "Por etapa 1→2→3"])
        with tab_bar:
            if not df_cont.empty and "Area" in df_cont.columns:
                ac = df_cont["Area"].fillna("Sin área").value_counts().reset_index()
                ac.columns = ["Area","Casos"]
                ac["Pct"] = (ac["Casos"]/ac["Casos"].sum()*100).round(1)
                ac["Color"] = ac["Area"].map(NPS_AREA_COLORS).fillna("#888")
                fig = go.Figure(go.Bar(x=ac["Casos"], y=ac["Area"], orientation="h",
                    marker_color=ac["Color"].tolist(),
                    text=ac.apply(lambda r: f"{r['Casos']}  {r['Pct']}%", axis=1),
                    textposition="outside", textfont=dict(size=10, color=TEXT_COLOR)))
                chart_layout(fig, height=310); fig.update_yaxes(autorange="reversed")
                fig.update_layout(showlegend=False, margin=dict(l=8,r=80,t=14,b=8))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with tab_sun:
            if not df_cont.empty and "Etapa1" in df_cont.columns:
                ed = df_cont.groupby(["Etapa1","Etapa2","Etapa3"]).size().reset_index(name="Casos").dropna(subset=["Etapa1"]).sort_values("Casos",ascending=False).head(20)
                if not ed.empty:
                    fig = px.sunburst(ed, path=["Etapa1","Etapa2","Etapa3"], values="Casos",
                        color="Etapa1", color_discrete_sequence=px.colors.qualitative.Dark24)
                    fig.update_traces(textfont_size=10)
                    fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_COLOR), margin=dict(l=0,r=0,t=0,b=0), height=280)
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">% Contactado por día</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Atendidas · tendencia diaria</div>', unsafe_allow_html=True)
        df_at = df[df["Asignación"] == "Atendida"].copy() if "Asignación" in df.columns else pd.DataFrame()
        if not df_at.empty and "Dia" in df_at.columns and "Contactado" in df_at.columns:
            dg = df_at.groupby(["Dia","Contactado"]).size().unstack(fill_value=0).reset_index()
            for c in ["Contactado","No Contactado"]:
                if c not in dg.columns: dg[c] = 0
            dg["Total"] = dg["Contactado"] + dg["No Contactado"]
            dg["Pct_C"]  = (dg["Contactado"]    / dg["Total"] * 100).round(1)
            dg["Pct_NC"] = (dg["No Contactado"]  / dg["Total"] * 100).round(1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dg["Dia"], y=dg["Pct_C"], name="% Contactado",
                mode="lines+markers", line=dict(color="#0F9B8E", width=2),
                marker=dict(size=5), fill="tozeroy", fillcolor="rgba(15,155,142,0.08)"))
            fig.add_trace(go.Scatter(x=dg["Dia"], y=dg["Pct_NC"], name="% No contactado",
                mode="lines+markers", line=dict(color="#C83050", width=2, dash="dot"), marker=dict(size=4)))
            fig.add_hline(y=50, line_dash="dash", line_color="#353545", line_width=1,
                annotation_text="50%", annotation_font=dict(color="#353545", size=9))
            chart_layout(fig, height=310); fig.update_xaxes(title_text="Día", dtick=1); fig.update_yaxes(title_text="%", range=[0,105])
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns([1.1, 1.3, 1.6])

    with col4:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Efectividad por agente</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">% contactado sobre asignados</div>', unsafe_allow_html=True)
        if not df.empty and "Soporte" in df.columns:
            ag = soporte_metrics_nps(df).sort_values("Pct_Efect", ascending=True)
            fig = go.Figure()
            for _, row in ag.iterrows():
                c = "#0F9B8E" if row["Pct_Efect"] >= 50 else "#C83050"
                fig.add_trace(go.Bar(x=[row["Pct_Efect"]], y=[row["Soporte"]], orientation="h",
                    marker_color=c,
                    text=f"{row['Pct_Efect']}%  ({int(row['Contactados'])}/{int(row['Total'])})",
                    textposition="outside", textfont=dict(size=10, color=TEXT_COLOR), showlegend=False))
            fig.add_vline(x=50, line_dash="dash", line_color="#353545", line_width=1,
                annotation_text="meta 50%", annotation_font=dict(color="#353545",size=9), annotation_position="top")
            chart_layout(fig, height=220); fig.update_xaxes(range=[0,115], title_text="%")
            fig.update_layout(margin=dict(l=8,r=90,t=14,b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Cumplimiento de visita</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Resultado del agendamiento técnico</div>', unsafe_allow_html=True)
        col_cumpl = "cumplimiento_fecha_inicial_agendamiento"
        if col_cumpl in df.columns:
            df_c = df[df[col_cumpl].notna()].copy()
            if not df_c.empty:
                cumpl_map = {
                    "Sí se cumplió, el Técnico llego el día y la hora acordadas": "Cumplió · día y hora",
                    "Sí se cumplió, llego el día acordado pero en un horario diferente": "Cumplió · horario diferente",
                    "No se cumplió, se tuvo que reagendar": "No cumplió · reagendado",
                    "No se cumplió y no se ha reagendado": "No cumplió · sin reagendar",
                }
                df_c["Resultado"] = df_c[col_cumpl].map(cumpl_map).fillna("Otro")
                cg = df_c["Resultado"].value_counts().reset_index(); cg.columns = ["Resultado","Casos"]
                CUMPL_C = {"Cumplió · día y hora":"#0F9B8E","Cumplió · horario diferente":"#BA7517","No cumplió · reagendado":"#C83050","No cumplió · sin reagendar":"#7F3040"}
                fig = go.Figure(go.Pie(labels=cg["Resultado"], values=cg["Casos"], hole=0.55,
                    marker_colors=[CUMPL_C.get(r,"#888") for r in cg["Resultado"]],
                    textfont=dict(size=10), textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>%{value} · %{percent}<extra></extra>"))
                fig.add_annotation(text=f"<b>{len(df_c)}</b><br><span style='font-size:9px'>casos</span>",
                    x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="white", family="Barlow Condensed"))
                fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
                    margin=dict(l=0,r=0,t=0,b=30), height=220,
                    legend=dict(bgcolor=CHART_BG, bordercolor=GRID_COLOR, font=dict(size=9),
                                orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Asignación por semana</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Atendida vs Gestión</div>', unsafe_allow_html=True)
        if not df.empty and "Semana_Actual" in df.columns and "Asignación" in df.columns:
            asig = df.groupby(["Semana_Actual","Asignación"]).size().unstack(fill_value=0).reset_index()
            fig = go.Figure()
            for cn in [c for c in ["Atendida","Gestión"] if c in asig.columns]:
                fig.add_trace(go.Bar(x=asig["Semana_Actual"].astype(str), y=asig[cn], name=cn,
                    marker_color="#0F9B8E" if cn=="Atendida" else "#BA7517",
                    text=asig[cn], textposition="inside", textfont=dict(size=10, color="white")))
            chart_layout(fig, height=220); fig.update_layout(barmode="group"); fig.update_xaxes(title_text="Semana")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Ranking NPS
    st.markdown(f'<div class="panel-title" style="color:white;font-family:\'Barlow Condensed\',sans-serif;font-size:15px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin:18px 0 10px;">🏆 RANKING · SOPORTES</div>', unsafe_allow_html=True)
    if not df.empty and "Soporte" in df.columns:
        rank_df = soporte_metrics_nps(df)
        sort_opts = {"% Efectividad":("Pct_Efect",False),"Total asignados":("Total",False),"% No contactado":("Pct_NoCont",False),"% Intento 3":("Pct_Int3",False)}
        cs1, cs2 = st.columns([2,1])
        with cs1: sort_label = st.selectbox("Ordenar por", list(sort_opts.keys()), key="nps_sort")
        with cs2: min_ord = st.slider("Mín. casos", 1, 20, 1, key="nps_min")
        sc, sa = sort_opts[sort_label]
        rank_df = rank_df[rank_df["Total"] >= min_ord].sort_values(sc, ascending=sa).reset_index(drop=True)
        rows_html = ""
        for i, row in rank_df.iterrows():
            pos = i+1; pct_e = row["Pct_Efect"]; color = rank_color(pct_e); bar_w = min(int(pct_e),100)
            rows_html += f"""<div class="rank-row">{rank_pos_html(pos)}<span class="rank-name">{row['Soporte']}</span><div class="rank-bar-wrap"><div class="rank-bar-fill" style="width:{bar_w}%;background:{color}"></div></div><span class="rank-metric" style="color:{color}">{pct_e}%</span><span class="rank-metric-sm" style="color:#C83050">NC:{row['Pct_NoCont']:.0f}%</span><span class="rank-metric-sm" style="color:#BA7517">I3:{row['Pct_Int3']:.0f}%</span><span class="rank-metric-sm">{int(row['Total'])} casos</span></div>"""
        st.markdown(f'<div class="rank-panel" style="border-color:{NPS_ACCENT}">{rows_html}</div>', unsafe_allow_html=True)
        st.caption("🟢 ≥60% efectividad   🟡 40–60%   🔴 <40%   |   NC: % No contactado   I3: % Intento 3")
        with st.expander("Ver tabla completa", expanded=False):
            tbl = rank_df[["Soporte","Total","Contactados","No_Contactados","Intento3","Pct_Efect","Pct_NoCont","Pct_Int3"]].rename(columns={"Soporte":"Agente","Pct_Efect":"% Efect.","Pct_NoCont":"% No Cont.","Pct_Int3":"% Int.3","No_Contactados":"No Cont.","Intento3":"Intento 3"})
            tbl.index = range(1, len(tbl)+1)
            st.dataframe(tbl, width="stretch", height=min(400, len(tbl)*35+40))
            st.download_button("⬇ Exportar CSV", tbl.to_csv().encode("utf-8"), "ranking_nps.csv", "text/csv", key="dl_nps")

    # Tabla detalle NPS
    st.markdown(f'<div class="panel" style="border-color:{NPS_ACCENT}">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Detalle de registros</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Todos los casos según filtros</div>', unsafe_allow_html=True)
    cols_show = [c for c in ["Fecha","Soporte","Asignación","Contactado","nombre_cliente","Zona","Tipo_Red","Area","Etapa1","Semana_Actual","Observacion contacto telefonico cliente."] if c in df.columns]
    df_show = df[cols_show].copy()
    df_show["Fecha"] = df_show["Fecha"].dt.strftime("%d/%m/%Y")
    if "Observacion contacto telefonico cliente." in df_show.columns:
        df_show["Observacion contacto telefonico cliente."] = df_show["Observacion contacto telefonico cliente."].fillna("").astype(str).str[:80]
    df_show = df_show.fillna("—")
    df_show.columns = [c.replace("Observacion contacto telefonico cliente.","Observación").replace("nombre_cliente","Cliente").replace("Semana_Actual","Sem.") for c in df_show.columns]
    st.dataframe(df_show, width="stretch", height=280, hide_index=True)
    st.download_button("⬇ Exportar CSV filtrado", df[cols_show].assign(Fecha=df["Fecha"].dt.strftime("%d/%m/%Y")).to_csv(index=False).encode("utf-8"), "nps_filtrado.csv", "text/csv", key="dl_nps_det")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="dash-footer" style="border-color:{NPS_ACCENT}"><span>Fuente: Google Sheets · Gestión NPS · Actualización automática</span><span>Claro Colombia · {datetime.now().strftime("%d/%m/%Y %H:%M")}</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 · QA MIGRACIÓN JUN–JUL
# ══════════════════════════════════════════════════════════════════════════════
HAINTECH_SHEET = "1xH0flWB44fl0qrqCnoVQ53ZkDgMEkJtBHjxKwhLSuU8"
QA_ACCENT      = "#1D6FE8"

QA_ESTADO_COLORS = {
    "Ejecución normal":"#0F9B8E","Sin Moradores":"#BA7517","Cliente desiste":"#C83050",
    "Cliente reagenda":"#378ADD","Orden no asistida":"#7F77DD","NAP Problema ubicación":"#D85A30",
    "Ductos tapados":"#888780","Sin acceso a vivienda":"#4A4A5A","Solicita Suspender":"#14b8a6",
    "Falta de dotación":"#a78bfa","Orden Cancelada Siebel":"#6A6A85",
}

COL_INTERV = "¿Se requiere intervenir al tecnico?"
COL_COMP   = "¿Se logra completar la migración?"

@st.cache_data(ttl=300, show_spinner="Cargando datos QA Migración…")
def load_qa():
    url = f"https://docs.google.com/spreadsheets/d/{HAINTECH_SHEET}/export?format=csv&gid=879767691"
    df = pd.read_csv(url, encoding="utf-8", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    date_col = "SF"
    if date_col in df.columns:
        df.rename(columns={date_col: "Fecha"}, inplace=True)
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df["Semana"] = df["Fecha"].dt.isocalendar().week.astype(int)
    for col in [COL_INTERV, COL_COMP]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df

def render_qa(df, source_name="QA Migración Jun–Jul"):
    total       = len(df)
    completadas = (df[COL_COMP] == "Si").sum() if COL_COMP in df.columns else 0
    no_comp     = (df[COL_COMP] == "No").sum() if COL_COMP in df.columns else 0
    requieren   = (df[COL_INTERV] == "Si").sum() if COL_INTERV in df.columns else 0
    sin_asist   = (df[COL_INTERV] == "Sin Asistencia").sum() if COL_INTERV in df.columns else 0
    pct_comp    = round(completadas / total * 100, 1) if total else 0
    kpi_color   = rank_color(pct_comp)

    st.markdown(f"""
    <div class="dash-header" style="border-bottom:3px solid {QA_ACCENT}">
      <div class="logo-box" style="background:{QA_ACCENT}">HAINTECH</div>
      <div>
        <div class="header-title">PILOTO TÉCNICOS · QA MIGRACIÓN</div>
        <div class="header-sub">PANEL DE CONTROL · {source_name.upper()} · {total} órdenes filtradas</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card" style="border-color:{QA_ACCENT}"><div class="kpi-value" style="color:{QA_ACCENT}">{total}</div><div class="kpi-label">Total órdenes</div><div class="kpi-dot" style="background:{QA_ACCENT}"></div></div>
      <div class="kpi-card" style="border-color:#0F9B8E"><div class="kpi-value" style="color:#0F9B8E">{completadas}</div><div class="kpi-label">Completadas</div><div class="kpi-dot" style="background:#0F9B8E"></div></div>
      <div class="kpi-card" style="border-color:#C83050"><div class="kpi-value" style="color:#C83050">{no_comp}</div><div class="kpi-label">No completadas</div><div class="kpi-dot" style="background:#C83050"></div></div>
      <div class="kpi-card" style="border-color:{kpi_color}"><div class="kpi-value" style="color:{kpi_color}">{pct_comp}%</div><div class="kpi-label">% Completitud</div><div class="kpi-dot" style="background:{kpi_color}"></div></div>
      <div class="kpi-card" style="border-color:#BA7517"><div class="kpi-value" style="color:#BA7517">{requieren}</div><div class="kpi-label">Requieren intervención</div><div class="kpi-dot" style="background:#BA7517"></div></div>
      <div class="kpi-card" style="border-color:#C83050"><div class="kpi-value" style="color:#C83050">{sin_asist}</div><div class="kpi-label">Sin asistencia</div><div class="kpi-dot" style="background:#C83050"></div></div>
    </div>""", unsafe_allow_html=True)

    p_style = f'style="border-color:{QA_ACCENT}"'
    col1, col2, col3 = st.columns([1.1, 1.6, 1.3])

    with col1:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Registro semanal</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Completadas vs No completadas por semana</div>', unsafe_allow_html=True)
        if not df.empty and COL_COMP in df.columns:
            pivot = df.groupby(["Semana", COL_COMP]).size().unstack(fill_value=0).reset_index().sort_values("Semana")
            for c in ["Si","No"]:
                if c not in pivot.columns: pivot[c] = 0
            pivot["Total"] = pivot["Si"] + pivot["No"]
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Completada", x=pivot["Semana"].astype(str), y=pivot["Si"], marker_color="#0F9B8E", text=pivot["Si"], textposition="inside", textfont=dict(size=10,color="white")))
            fig.add_trace(go.Bar(name="No completada", x=pivot["Semana"].astype(str), y=pivot["No"], marker_color="#C83050", text=pivot["No"], textposition="inside", textfont=dict(size=10,color="white")))
            fig.update_layout(barmode="stack"); chart_layout(fig, height=230); fig.update_xaxes(title_text="Semana ISO")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            tbl = pivot[["Semana","Si","No","Total"]].copy(); tbl.columns = ["Sem.","Complet.","No comp.","Total"]
            st.dataframe(tbl.set_index("Sem."), width="stretch", height=110)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Estado solicitud inicial</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Distribución de motivos de apertura</div>', unsafe_allow_html=True)
        if not df.empty and "Estado Solicitud Inicial" in df.columns:
            tb, tp = st.tabs(["Barras","Donut"])
            cnt = df["Estado Solicitud Inicial"].value_counts().reset_index(); cnt.columns = ["Estado","Cantidad"]
            cnt["Pct"] = (cnt["Cantidad"]/cnt["Cantidad"].sum()*100).round(1)
            cnt["Color"] = cnt["Estado"].map(QA_ESTADO_COLORS).fillna("#64748b")
            cnt = cnt.sort_values("Cantidad", ascending=True)
            with tb:
                fig = go.Figure(go.Bar(x=cnt["Cantidad"], y=cnt["Estado"], orientation="h", marker_color=cnt["Color"].tolist(),
                    text=cnt.apply(lambda r: f"{r['Cantidad']}  {r['Pct']}%", axis=1), textposition="outside", textfont=dict(size=10,color=TEXT_COLOR)))
                chart_layout(fig, height=310); fig.update_layout(showlegend=False, margin=dict(l=8,r=90,t=14,b=8))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            with tp:
                fig = go.Figure(go.Pie(labels=cnt["Estado"], values=cnt["Cantidad"], hole=0.55, marker_colors=cnt["Color"].tolist(), textfont=dict(size=10), textinfo="percent"))
                fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>órdenes</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=14,color="white",family="Barlow Condensed"))
                fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_COLOR,family=FONT_FAMILY), margin=dict(l=0,r=0,t=0,b=0), height=310, legend=dict(bgcolor=CHART_BG,bordercolor=GRID_COLOR,font=dict(size=9),x=1.0,y=0.5))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">% Completitud por día</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Tendencia diaria</div>', unsafe_allow_html=True)
        if not df.empty and COL_COMP in df.columns and "ID Orden" in df.columns:
            daily = df.groupby("Fecha").agg(Total=("ID Orden","count"), Comp=(COL_COMP, lambda x: (x=="Si").sum())).reset_index().sort_values("Fecha")
            daily["Pct_C"] = (daily["Comp"]/daily["Total"]*100).round(1)
            daily["Pct_NC"] = (100-daily["Pct_C"]).round(1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily["Fecha"], y=daily["Pct_C"], name="% Completada", mode="lines+markers", line=dict(color="#0F9B8E",width=2), marker=dict(size=5), fill="tozeroy", fillcolor="rgba(15,155,142,0.08)"))
            fig.add_trace(go.Scatter(x=daily["Fecha"], y=daily["Pct_NC"], name="% No completada", mode="lines+markers", line=dict(color="#C83050",width=2,dash="dot"), marker=dict(size=4)))
            fig.add_hline(y=50, line_dash="dash", line_color="#353545", line_width=1, annotation_text="50%", annotation_font=dict(color="#353545",size=9))
            chart_layout(fig, height=310); fig.update_yaxes(title_text="%", range=[0,108])
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns([1.1, 1.0, 1.9])

    with col4:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Completitud por soporte</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">% migración exitosa por agente</div>', unsafe_allow_html=True)
        if not df.empty and COL_COMP in df.columns and "Soporte HAINTECH" in df.columns:
            ag = groupby_comp(df, "Soporte HAINTECH", COL_COMP).sort_values("Pct_Comp", ascending=True)
            fig = go.Figure()
            for _, row in ag.iterrows():
                c = "#0F9B8E" if row["Pct_Comp"] >= 50 else "#C83050"
                fig.add_trace(go.Bar(x=[row["Pct_Comp"]], y=[row["Soporte HAINTECH"]], orientation="h", marker_color=c, text=f"{row['Pct_Comp']}%  ({int(row['Completadas'])}/{int(row['Total'])})", textposition="outside", textfont=dict(size=10,color=TEXT_COLOR), showlegend=False))
            fig.add_vline(x=50, line_dash="dash", line_color="#353545", line_width=1, annotation_text="meta 50%", annotation_font=dict(color="#353545",size=9), annotation_position="top")
            chart_layout(fig, height=230); fig.update_xaxes(range=[0,120], title_text="%"); fig.update_layout(margin=dict(l=8,r=90,t=14,b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Requiere intervención</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Distribución de nivel de gestión</div>', unsafe_allow_html=True)
        if not df.empty and COL_INTERV in df.columns:
            ig = df[COL_INTERV].value_counts().reset_index(); ig.columns = ["Tipo","Cantidad"]
            IC = {"Si":"#BA7517","No":"#0F9B8E","Sin Asistencia":"#C83050"}
            fig = go.Figure(go.Pie(labels=ig["Tipo"], values=ig["Cantidad"], hole=0.55, marker_colors=[IC.get(t,"#888") for t in ig["Tipo"]], textfont=dict(size=10), textinfo="percent"))
            fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>órdenes</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=14,color="white",family="Barlow Condensed"))
            fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_COLOR,family=FONT_FAMILY), margin=dict(l=0,r=0,t=0,b=30), height=230, legend=dict(bgcolor=CHART_BG,bordercolor=GRID_COLOR,font=dict(size=10),orientation="h",yanchor="bottom",y=-0.22,xanchor="center",x=0.5))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Top técnicos · completitud</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Top 15 por volumen — color según tasa de éxito</div>', unsafe_allow_html=True)
        tec_col = next((c for c in ["Tecnico Auditado","tecnico","Técnico"] if c in df.columns), None)
        if not df.empty and tec_col and COL_COMP in df.columns:
            tec = groupby_comp(df, tec_col, COL_COMP).nlargest(15,"Total").sort_values("Total",ascending=True)
            tec["Color"] = tec["Pct_Comp"].apply(lambda p: "#0F9B8E" if p>=60 else ("#BA7517" if p>=40 else "#C83050"))
            fig = go.Figure(go.Bar(x=tec["Total"], y=tec[tec_col], orientation="h", marker_color=tec["Color"].tolist(),
                text=tec.apply(lambda r: f"{int(r['Total'])}  ({r['Pct_Comp']}%)", axis=1), textposition="outside", textfont=dict(size=10,color=TEXT_COLOR)))
            chart_layout(fig, height=260); fig.update_layout(showlegend=False, margin=dict(l=8,r=110,t=14,b=8)); fig.update_xaxes(title_text="Órdenes")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            st.caption("🟢 ≥60%   🟡 40–60%   🔴 <40%")
        st.markdown('</div>', unsafe_allow_html=True)

    # Tabla detalle QA
    st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Detalle de registros</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Todos los casos según filtros aplicados</div>', unsafe_allow_html=True)
    cols_show = [c for c in ["Fecha","ID Orden","Tecnico Auditado","Soporte HAINTECH","Estado Solicitud Inicial", COL_INTERV, COL_COMP,"Estado Solicitud Final","Observacion"] if c in df.columns]
    df_show = df[cols_show].copy()
    df_show["Fecha"] = df_show["Fecha"].dt.strftime("%d/%m/%Y")
    if "Observacion" in df_show.columns:
        df_show["Observacion"] = df_show["Observacion"].fillna("").astype(str).str[:80]
    df_show = df_show.fillna("—")
    df_show.columns = [c.replace(COL_INTERV,"Intervención").replace(COL_COMP,"Completada") for c in df_show.columns]
    st.dataframe(df_show, width="stretch", height=280, hide_index=True)
    st.download_button("⬇ Exportar CSV filtrado", df[cols_show].assign(Fecha=df["Fecha"].dt.strftime("%d/%m/%Y")).to_csv(index=False).encode("utf-8"), "qa_filtrado.csv", "text/csv", key="dl_qa_det")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="dash-footer" style="border-color:{QA_ACCENT}"><span>Fuente: Google Sheets · {source_name} · Actualización automática cada 5 min</span><span>HAINTECH · {datetime.now().strftime("%d/%m/%Y %H:%M")}</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 · SEGUIMIENTO DERIVACIONES
# ══════════════════════════════════════════════════════════════════════════════
SEG_ACCENT = "#0F9B8E"
COL_GESTION = "Gestion"
COL_DERIV   = "Veces que cliente ha sido derivado"

SEG_ESTADO_INI_COLORS = {"Cliente reagenda validado":"#378ADD","Sin Moradores validado":"#BA7517","Cliente desiste validado":"#C83050"}
SEG_ESTADO_FIN_COLORS = {"Completada correctamente":"#0F9B8E","Pendiente de Contacto":"#378ADD","Cliente desiste validado":"#C83050","Sin Moradores validado":"#BA7517","Problema Comercial validado":"#D85A30","Sin acceso a vivienda validado":"#7F77DD","Ductos tapados (Deriva Supervisor)":"#888780","NAP Problema ubicación validado":"#D85A30","Cliente reagenda validado":"#4A90D9","Orden Suspendida":"#6A6A85"}
SEG_GESTION_COLORS = {"INTERNO":"#1D6FE8","HAINTECH":"#0F9B8E"}

@st.cache_data(ttl=300, show_spinner="Cargando datos Seguimiento…")
def load_seg():
    url = f"https://docs.google.com/spreadsheets/d/{HAINTECH_SHEET}/export?format=csv&gid=1058963747"
    df = pd.read_csv(url, encoding="utf-8", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    if "Fecha inicial" in df.columns:
        df.rename(columns={"Fecha inicial": "Fecha"}, inplace=True)
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df["Semana"] = df["Fecha"].dt.isocalendar().week.astype(int)
    for col in [COL_COMP, COL_GESTION, "Estado Solicitud Inicial", "Estado Solicitud Final", "Soporte HAINTECH"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    if COL_DERIV in df.columns:
        df[COL_DERIV] = pd.to_numeric(df[COL_DERIV], errors="coerce")
    return df

def render_seg(df):
    total        = len(df)
    completadas  = (df[COL_COMP] == "Si").sum() if COL_COMP in df.columns else 0
    no_comp      = (df[COL_COMP] == "No").sum() if COL_COMP in df.columns else 0
    pct_comp     = round(completadas / total * 100, 1) if total else 0
    prom_deriv   = round(df[COL_DERIV].mean(), 1) if COL_DERIV in df.columns and not df[COL_DERIV].isna().all() else 0
    cnt_haintech = (df[COL_GESTION] == "HAINTECH").sum() if COL_GESTION in df.columns else 0
    kpi_color    = rank_color(pct_comp)

    st.markdown(f"""
    <div class="dash-header" style="border-bottom:3px solid {SEG_ACCENT}">
      <div class="logo-box" style="background:{SEG_ACCENT}">HAINTECH</div>
      <div>
        <div class="header-title">SEGUIMIENTO DE DERIVACIONES</div>
        <div class="header-sub">PANEL DE CONTROL · SEPT 2026 · {total} órdenes filtradas</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card" style="border-color:#1D6FE8"><div class="kpi-value" style="color:#1D6FE8">{total}</div><div class="kpi-label">Total órdenes</div><div class="kpi-dot" style="background:#1D6FE8"></div></div>
      <div class="kpi-card" style="border-color:#0F9B8E"><div class="kpi-value" style="color:#0F9B8E">{completadas}</div><div class="kpi-label">Completadas</div><div class="kpi-dot" style="background:#0F9B8E"></div></div>
      <div class="kpi-card" style="border-color:#C83050"><div class="kpi-value" style="color:#C83050">{no_comp}</div><div class="kpi-label">No completadas</div><div class="kpi-dot" style="background:#C83050"></div></div>
      <div class="kpi-card" style="border-color:{kpi_color}"><div class="kpi-value" style="color:{kpi_color}">{pct_comp}%</div><div class="kpi-label">% Completitud</div><div class="kpi-dot" style="background:{kpi_color}"></div></div>
      <div class="kpi-card" style="border-color:#BA7517"><div class="kpi-value" style="color:#BA7517">{prom_deriv}x</div><div class="kpi-label">Prom. derivaciones</div><div class="kpi-dot" style="background:#BA7517"></div></div>
      <div class="kpi-card" style="border-color:#7F77DD"><div class="kpi-value" style="color:#7F77DD">{cnt_haintech}</div><div class="kpi-label">Gestión HAINTECH</div><div class="kpi-dot" style="background:#7F77DD"></div></div>
    </div>""", unsafe_allow_html=True)

    p_style = f'style="border-color:{SEG_ACCENT}"'
    col1, col2, col3 = st.columns([1.1, 1.6, 1.3])

    with col1:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Registro semanal</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Completadas vs No completadas por semana</div>', unsafe_allow_html=True)
        if not df.empty and COL_COMP in df.columns:
            pivot = df.groupby(["Semana", COL_COMP]).size().unstack(fill_value=0).reset_index().sort_values("Semana")
            for c in ["Si","No"]:
                if c not in pivot.columns: pivot[c] = 0
            pivot["Total"] = pivot["Si"] + pivot["No"]
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Completada", x=pivot["Semana"].astype(str), y=pivot["Si"], marker_color="#0F9B8E", text=pivot["Si"], textposition="inside", textfont=dict(size=10,color="white")))
            fig.add_trace(go.Bar(name="No completada", x=pivot["Semana"].astype(str), y=pivot["No"], marker_color="#C83050", text=pivot["No"], textposition="inside", textfont=dict(size=10,color="white")))
            fig.update_layout(barmode="stack"); chart_layout(fig, height=230); fig.update_xaxes(title_text="Semana ISO")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            tbl = pivot[["Semana","Si","No","Total"]].copy(); tbl.columns = ["Sem.","Complet.","No comp.","Total"]
            st.dataframe(tbl.set_index("Sem."), width="stretch", height=110)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Estado solicitud inicial</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Distribución de motivos de entrada</div>', unsafe_allow_html=True)
        if not df.empty and "Estado Solicitud Inicial" in df.columns:
            tb, tp = st.tabs(["Barras","Donut"])
            cnt = df["Estado Solicitud Inicial"].value_counts().reset_index(); cnt.columns = ["Estado","Cantidad"]
            cnt["Pct"] = (cnt["Cantidad"]/cnt["Cantidad"].sum()*100).round(1)
            cnt["Color"] = cnt["Estado"].map(SEG_ESTADO_INI_COLORS).fillna("#64748b")
            cnt = cnt.sort_values("Cantidad", ascending=True)
            with tb:
                fig = go.Figure(go.Bar(x=cnt["Cantidad"], y=cnt["Estado"], orientation="h", marker_color=cnt["Color"].tolist(),
                    text=cnt.apply(lambda r: f"{r['Cantidad']}  {r['Pct']}%", axis=1), textposition="outside", textfont=dict(size=10,color=TEXT_COLOR)))
                chart_layout(fig, height=310); fig.update_layout(showlegend=False, margin=dict(l=8,r=90,t=14,b=8))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            with tp:
                fig = go.Figure(go.Pie(labels=cnt["Estado"], values=cnt["Cantidad"], hole=0.55, marker_colors=cnt["Color"].tolist(), textfont=dict(size=10), textinfo="percent"))
                fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>órdenes</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=14,color="white",family="Barlow Condensed"))
                fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_COLOR,family=FONT_FAMILY), margin=dict(l=0,r=0,t=0,b=0), height=310, legend=dict(bgcolor=CHART_BG,bordercolor=GRID_COLOR,font=dict(size=9),x=1.0,y=0.5))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">% Completitud por día</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Tendencia diaria de órdenes completadas</div>', unsafe_allow_html=True)
        if not df.empty and COL_COMP in df.columns and "ID Orden" in df.columns:
            daily = df.groupby("Fecha").agg(Total=("ID Orden","count"), Comp=(COL_COMP, lambda x: (x=="Si").sum())).reset_index().sort_values("Fecha")
            daily["Pct_C"] = (daily["Comp"]/daily["Total"]*100).round(1); daily["Pct_NC"] = (100-daily["Pct_C"]).round(1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily["Fecha"], y=daily["Pct_C"], name="% Completada", mode="lines+markers", line=dict(color="#0F9B8E",width=2), marker=dict(size=5), fill="tozeroy", fillcolor="rgba(15,155,142,0.08)"))
            fig.add_trace(go.Scatter(x=daily["Fecha"], y=daily["Pct_NC"], name="% No completada", mode="lines+markers", line=dict(color="#C83050",width=2,dash="dot"), marker=dict(size=4)))
            fig.add_hline(y=50, line_dash="dash", line_color="#353545", line_width=1, annotation_text="50%", annotation_font=dict(color="#353545",size=9))
            chart_layout(fig, height=310); fig.update_yaxes(title_text="%", range=[0,108])
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns([1.2, 0.9, 1.9])

    with col4:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Completitud por soporte</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">% migración exitosa por agente</div>', unsafe_allow_html=True)
        if not df.empty and COL_COMP in df.columns and "Soporte HAINTECH" in df.columns:
            ag = groupby_comp(df, "Soporte HAINTECH", COL_COMP).sort_values("Pct_Comp", ascending=True)
            fig = go.Figure()
            for _, row in ag.iterrows():
                c = "#0F9B8E" if row["Pct_Comp"] >= 50 else "#C83050"
                fig.add_trace(go.Bar(x=[row["Pct_Comp"]], y=[row["Soporte HAINTECH"]], orientation="h", marker_color=c, text=f"{row['Pct_Comp']}%  ({int(row['Completadas'])}/{int(row['Total'])})", textposition="outside", textfont=dict(size=10,color=TEXT_COLOR), showlegend=False))
            fig.add_vline(x=50, line_dash="dash", line_color="#353545", line_width=1, annotation_text="meta 50%", annotation_font=dict(color="#353545",size=9), annotation_position="top")
            chart_layout(fig, height=270); fig.update_xaxes(range=[0,120], title_text="%"); fig.update_layout(margin=dict(l=8,r=110,t=14,b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Tipo de gestión</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">INTERNO vs HAINTECH</div>', unsafe_allow_html=True)
        if not df.empty and COL_GESTION in df.columns:
            gc = df[COL_GESTION].value_counts().reset_index(); gc.columns = ["Gestión","Cantidad"]
            fig = go.Figure(go.Pie(labels=gc["Gestión"], values=gc["Cantidad"], hole=0.55, marker_colors=[SEG_GESTION_COLORS.get(g,"#64748b") for g in gc["Gestión"]], textfont=dict(size=10), textinfo="percent+value"))
            fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>órdenes</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=14,color="white",family="Barlow Condensed"))
            fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_COLOR,family=FONT_FAMILY), margin=dict(l=0,r=0,t=0,b=30), height=270, legend=dict(bgcolor=CHART_BG,bordercolor=GRID_COLOR,font=dict(size=10),orientation="h",yanchor="bottom",y=-0.18,xanchor="center",x=0.5))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Veces derivado · distribución</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Número de veces que el cliente ha sido derivado</div>', unsafe_allow_html=True)
        if not df.empty and COL_DERIV in df.columns:
            dc = df[COL_DERIV].dropna().astype(int).value_counts().sort_index().reset_index(); dc.columns = ["Veces","Cantidad"]
            dc["Pct"] = (dc["Cantidad"]/dc["Cantidad"].sum()*100).round(1)
            def dc_color(v): return "#0F9B8E" if v<=1 else ("#BA7517" if v<=3 else "#C83050")
            fig = go.Figure(go.Bar(x=dc["Veces"].astype(str), y=dc["Cantidad"], marker_color=[dc_color(v) for v in dc["Veces"]],
                text=dc.apply(lambda r: f"{r['Cantidad']} ({r['Pct']}%)", axis=1), textposition="outside", textfont=dict(size=10,color=TEXT_COLOR)))
            chart_layout(fig, height=270); fig.update_xaxes(title_text="Número de derivaciones"); fig.update_yaxes(title_text="Órdenes"); fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            st.caption("🟢 1 derivación   🟡 2–3   🔴 4+")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Estado Solicitud Final · distribución</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Resultado final después de la gestión</div>', unsafe_allow_html=True)
    if not df.empty and "Estado Solicitud Final" in df.columns:
        fc = df["Estado Solicitud Final"].replace("nan", pd.NA).dropna().value_counts().reset_index(); fc.columns = ["Estado","Cantidad"]
        fc["Pct"] = (fc["Cantidad"]/fc["Cantidad"].sum()*100).round(1)
        fc["Color"] = fc["Estado"].map(SEG_ESTADO_FIN_COLORS).fillna("#64748b")
        fc = fc.sort_values("Cantidad", ascending=True)
        fig = go.Figure(go.Bar(x=fc["Cantidad"], y=fc["Estado"], orientation="h", marker_color=fc["Color"].tolist(),
            text=fc.apply(lambda r: f"{r['Cantidad']}  ({r['Pct']}%)", axis=1), textposition="outside", textfont=dict(size=10,color=TEXT_COLOR)))
        chart_layout(fig, height=300); fig.update_layout(showlegend=False, margin=dict(l=8,r=110,t=14,b=8)); fig.update_xaxes(title_text="Órdenes")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabla detalle Seguimiento
    st.markdown(f'<div class="panel" {p_style}>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Detalle de registros</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Todos los casos según filtros aplicados</div>', unsafe_allow_html=True)
    cols_show = [c for c in ["Fecha","ID Orden","Rut Cliente","Soporte HAINTECH","Estado Solicitud Inicial", COL_GESTION, COL_DERIV, COL_COMP,"Estado Solicitud Final","Observacion Inicial"] if c in df.columns]
    df_show = df[cols_show].copy()
    df_show["Fecha"] = df_show["Fecha"].dt.strftime("%d/%m/%Y")
    if COL_DERIV in df_show.columns:
        df_show[COL_DERIV] = df_show[COL_DERIV].apply(lambda x: str(int(x)) if pd.notna(x) else "—")
    if "Observacion Inicial" in df_show.columns:
        df_show["Observacion Inicial"] = df_show["Observacion Inicial"].fillna("").astype(str).str[:80]
    df_show = df_show.fillna("—")
    df_show.columns = [c.replace(COL_COMP,"Completada").replace(COL_GESTION,"Gestión").replace(COL_DERIV,"# Deriv.") for c in df_show.columns]
    st.dataframe(df_show, width="stretch", height=300, hide_index=True)
    st.download_button("⬇ Exportar CSV filtrado", df[cols_show].assign(Fecha=df["Fecha"].dt.strftime("%d/%m/%Y")).to_csv(index=False).encode("utf-8"), "seguimiento_filtrado.csv", "text/csv", key="dl_seg_det")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="dash-footer" style="border-color:{SEG_ACCENT}"><span>Fuente: Google Sheets · Seguimiento Derivaciones · Actualización automática cada 5 min</span><span>HAINTECH · {datetime.now().strftime("%d/%m/%Y %H:%M")}</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR · SELECTOR DE MÓDULO + FILTROS
# ══════════════════════════════════════════════════════════════════════════════
MODULOS = ["📊 Gestión NPS · Claro", "📡 QA Migración Jun–Jul", "📋 Seguimiento Derivaciones"]

with st.sidebar:
    st.markdown('<div class="sidebar-section" style="color:#1D6FE8">Módulo</div>', unsafe_allow_html=True)
    modulo = st.selectbox("Selecciona módulo", MODULOS, label_visibility="collapsed")

    st.markdown('<div class="sidebar-section" style="color:#1D6FE8;margin-top:10px">Filtros</div>', unsafe_allow_html=True)

    # ── NPS filters ──
    if modulo == MODULOS[0]:
        df_raw = load_nps()
        meses = ["Todos"] + sorted(df_raw["Mes_Actual"].dropna().unique().tolist()) if "Mes_Actual" in df_raw.columns else ["Todos"]
        mes = st.selectbox("Mes", meses, index=meses.index("May") if "May" in meses else 0)
        soportes = ["Todos"] + sorted(df_raw["Soporte"].dropna().unique().tolist()) if "Soporte" in df_raw.columns else ["Todos"]
        soporte = st.selectbox("Soporte / Agente", soportes)
        semanas_disp = sorted(df_raw["Semana_Actual"].dropna().unique().tolist()) if "Semana_Actual" in df_raw.columns else []
        semanas_sel = st.multiselect("Semanas", semanas_disp, default=[s for s in semanas_disp if s >= 18])
        asig_opts = ["Todas"] + (df_raw["Asignación"].dropna().unique().tolist() if "Asignación" in df_raw.columns else [])
        asignacion = st.selectbox("Asignación", asig_opts)
        tipo_red = st.multiselect("Tipo de red", df_raw["Tipo_Red"].dropna().unique().tolist() if "Tipo_Red" in df_raw.columns else [], default=df_raw["Tipo_Red"].dropna().unique().tolist() if "Tipo_Red" in df_raw.columns else [])
        zonas = st.multiselect("Zona", df_raw["Zona"].dropna().unique().tolist() if "Zona" in df_raw.columns else [], default=df_raw["Zona"].dropna().unique().tolist() if "Zona" in df_raw.columns else [])
        df = df_raw.copy()
        if mes != "Todos" and "Mes_Actual" in df.columns: df = df[df["Mes_Actual"] == mes]
        if soporte != "Todos" and "Soporte" in df.columns: df = df[df["Soporte"] == soporte]
        if semanas_sel and "Semana_Actual" in df.columns: df = df[df["Semana_Actual"].isin(semanas_sel)]
        if asignacion != "Todas" and "Asignación" in df.columns: df = df[df["Asignación"] == asignacion]
        if tipo_red and "Tipo_Red" in df.columns: df = df[df["Tipo_Red"].isin(tipo_red)]
        if zonas and "Zona" in df.columns: df = df[df["Zona"].isin(zonas)]

    # ── QA filters ──
    elif modulo == MODULOS[1]:
        df_raw = load_qa()
        min_d, max_d = df_raw["Fecha"].min().date(), df_raw["Fecha"].max().date()
        date_range = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        MESES_ES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
        meses_num = sorted(df_raw["Fecha"].dt.month.dropna().unique().tolist())
        meses_disp = [MESES_ES[m] for m in meses_num]
        meses_sel = st.multiselect("Mes", meses_disp, default=meses_disp)
        meses_num_sel = [k for k,v in MESES_ES.items() if v in meses_sel]
        semanas_disp = sorted(df_raw["Semana"].dropna().unique().tolist())
        semanas_sel = st.multiselect("Semanas", semanas_disp, default=semanas_disp)
        soportes = ["Todos"] + sorted(df_raw["Soporte HAINTECH"].dropna().unique().tolist()) if "Soporte HAINTECH" in df_raw.columns else ["Todos"]
        soporte_sel = st.selectbox("Soporte HAINTECH", soportes)
        estados_disp = df_raw["Estado Solicitud Inicial"].dropna().unique().tolist() if "Estado Solicitud Inicial" in df_raw.columns else []
        estados_sel = st.multiselect("Estado Inicial", estados_disp, default=estados_disp)
        start = pd.Timestamp(date_range[0]) if len(date_range) >= 1 else df_raw["Fecha"].min()
        end   = pd.Timestamp(date_range[1]) if len(date_range) == 2 else df_raw["Fecha"].max()
        df = df_raw[(df_raw["Fecha"] >= start) & (df_raw["Fecha"] <= end)].copy()
        if meses_num_sel: df = df[df["Fecha"].dt.month.isin(meses_num_sel)]
        if semanas_sel: df = df[df["Semana"].isin(semanas_sel)]
        if soporte_sel != "Todos" and "Soporte HAINTECH" in df.columns: df = df[df["Soporte HAINTECH"] == soporte_sel]
        if estados_sel and "Estado Solicitud Inicial" in df.columns: df = df[df["Estado Solicitud Inicial"].isin(estados_sel)]

    # ── Seguimiento filters ──
    else:
        df_raw = load_seg()
        min_d, max_d = df_raw["Fecha"].min().date(), df_raw["Fecha"].max().date()
        date_range = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        MESES_ES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
        meses_num = sorted(df_raw["Fecha"].dt.month.dropna().unique().tolist())
        meses_disp = [MESES_ES[m] for m in meses_num]
        meses_sel = st.multiselect("Mes", meses_disp, default=meses_disp)
        meses_num_sel = [k for k,v in MESES_ES.items() if v in meses_sel]
        semanas_disp = sorted(df_raw["Semana"].dropna().unique().tolist())
        semanas_sel = st.multiselect("Semanas", semanas_disp, default=semanas_disp)
        soportes = ["Todos"] + sorted(df_raw["Soporte HAINTECH"].dropna().unique().tolist()) if "Soporte HAINTECH" in df_raw.columns else ["Todos"]
        soporte_sel = st.selectbox("Soporte HAINTECH", soportes)
        estados_disp = df_raw["Estado Solicitud Inicial"].dropna().unique().tolist() if "Estado Solicitud Inicial" in df_raw.columns else []
        estados_sel = st.multiselect("Estado Inicial", estados_disp, default=estados_disp)
        gestion_opts = ["Todas"] + sorted(df_raw[COL_GESTION].dropna().unique().tolist() if COL_GESTION in df_raw.columns else [])
        gestion_sel = st.selectbox("Gestión", gestion_opts)
        start = pd.Timestamp(date_range[0]) if len(date_range) >= 1 else df_raw["Fecha"].min()
        end   = pd.Timestamp(date_range[1]) if len(date_range) == 2 else df_raw["Fecha"].max()
        df = df_raw[(df_raw["Fecha"] >= start) & (df_raw["Fecha"] <= end)].copy()
        if meses_num_sel: df = df[df["Fecha"].dt.month.isin(meses_num_sel)]
        if semanas_sel: df = df[df["Semana"].isin(semanas_sel)]
        if soporte_sel != "Todos" and "Soporte HAINTECH" in df.columns: df = df[df["Soporte HAINTECH"] == soporte_sel]
        if estados_sel and "Estado Solicitud Inicial" in df.columns: df = df[df["Estado Solicitud Inicial"].isin(estados_sel)]
        if gestion_sel != "Todas" and COL_GESTION in df.columns: df = df[df[COL_GESTION] == gestion_sel]

    st.markdown("---")
    st.markdown('<p style="font-size:10px;color:#353545;text-align:center">Datos actualizados automáticamente<br>desde Google Sheets</p>', unsafe_allow_html=True)
    if st.button("🔄  Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ── RENDERIZAR MÓDULO SELECCIONADO ────────────────────────────────────────────
if modulo == MODULOS[0]:
    render_nps(df)
elif modulo == MODULOS[1]:
    render_qa(df)
else:
    render_seg(df)
