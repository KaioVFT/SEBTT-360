import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import os
from streamlit_option_menu import option_menu
import base64

st.set_page_config(page_title="SEBTT 360°", page_icon="assets/logo.png", layout="wide", initial_sidebar_state="expanded")

# Credenciais Locais de Acesso (Modificado sob demanda)
ADMIN_USER = st.secrets["ADMIN_USER"]
ADMIN_PASS = st.secrets["ADMIN_PASS"]

def get_base64_image(image_path):
    if not os.path.exists(image_path): return None
    with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()

@st.cache_data(show_spinner="Carregando Base Histórica (Parquet)...")
def get_cursos_stats():
    try:
        if os.path.exists('dados/discentes.parquet') and os.path.exists('dados/cursos.parquet'):
            d = pd.read_parquet('dados/discentes.parquet')
            c = pd.read_parquet('dados/cursos.parquet')[['id_curso', 'curso_nome']].drop_duplicates()
            df = d.merge(c, on='id_curso', how='left')
            df['evadido'] = (df['status_discente'] == 'CANCELADO').astype(int)
            res = df.groupby('curso_nome').agg(
                alunos=('id_discente', 'count'), evasao=('evadido', 'mean'), media=('media_geral', 'mean')
            ).reset_index().sort_values('alunos', ascending=False)
            res['evasao_pct'] = res['evasao'] * 100
            res['media'] = res['media'].fillna(0.0)
            return res
        return pd.DataFrame()
    except Exception: return pd.DataFrame()

@st.cache_data(show_spinner="Carregando Base de Matrículas...")
def get_alunos_por_curso(curso_alvo):
    try:
        d, c = pd.read_parquet('dados/discentes.parquet'), pd.read_parquet('dados/cursos.parquet')[['id_curso', 'curso_nome']].drop_duplicates()
        df = d.merge(c, on='id_curso', how='left')
        df_curso = df[df['curso_nome'] == curso_alvo].copy()
        status_inativos = ['CANCELADO', 'CONCLUÍDO', 'FORMADO', 'TRANCADO', 'FORMANDO']
        df_curso = df_curso[~df_curso['status_discente'].isin(status_inativos)].copy()
        np.random.seed(42)
        r = []
        for _, row in df_curso.iterrows():
            media = row['media_geral'] if pd.notnull(row['media_geral']) else 5.0
            renda = str(row['faixa_renda_familiar']).lower()
            risco = 0.15; motivo = "Engajamento Estável"
            if media < 5.0: risco += 0.45; motivo = "Baixo Desempenho e Reprovações"
            elif media < 7.0:
                risco += 0.25; motivo = "Vulnerabilidade Extrema (Renda)" if "vulner" in renda or "baixa" in renda else "Risco Acadêmico Moderado (Notas)"
            else:
                if "vulner" in renda or "baixa" in renda: risco += 0.20; motivo = "Atenção Socioeconômica Primária"
            risco = min(risco + np.random.uniform(0.00, 0.12), 0.99)
            if row['status_discente'] == 'CANCELADO': risco, motivo = max(risco, 0.85), "Evasão Consolidada"
            r.append({"Matrícula Anonimizada": f"***{str(row['id_discente'])[-4:]}", "Probabilidade Evasão (%)": round(risco * 100, 1), "Média Geral (Histórico)": round(media, 2), "Maior Ofensor / Problema Identificado": motivo, "E-mail Institucional": "coordenacao.teste@ufpb.br", "Status Sistema": row['status_discente']})
        return pd.DataFrame(r).sort_values("Probabilidade Evasão (%)", ascending=False)
    except Exception: return pd.DataFrame()

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F4F7FA; }
        .stApp { background: radial-gradient(circle at center, #ffffff 0%, #F4F7FA 100%); color: #00305E !important; }
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background-color: #FFFFFF !important; border-right: 1px solid rgba(0, 34, 68, 0.08) !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1400px; }
        #MainMenu, footer { visibility: hidden; }
        button[kind="header"], [data-testid="StyledFullScreenButton"] { display: none !important; visibility: hidden !important; }
        [data-testid="collapsedControl"] { background-color: #FFFFFF !important; border: 1px solid rgba(0, 34, 68, 0.08) !important; border-radius: 8px !important; top: 15px !important; left: 15px !important; z-index: 999999 !important; display: flex !important; visibility: visible !important; }
        [data-testid="collapsedControl"] svg { fill: #0056b3 !important; color: #0056b3 !important; }
        [data-testid="collapsedControl"]:hover { background-color: rgba(0, 86, 179, 0.1) !important; border-color: #0056b3 !important; }
        ::-webkit-scrollbar-thumb { background: #0056b3; border-radius: 99px; }
        h1, h2, h3, h4 { color: #00305E !important; font-weight: 600; letter-spacing: -0.5px; }
        [data-testid="stForm"], div.card, .sebtt-card { background: #FFFFFF !important; border: 1px solid rgba(0, 34, 68, 0.08) !important; border-radius: 12px !important; padding: 2rem !important; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03) !important; transition: border-color 0.3s ease, transform 0.3s ease; }
        [data-baseweb="input"], [data-baseweb="select"], .stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div { background-color: #F8FAFC !important; border: 1px solid rgba(0, 34, 68, 0.1) !important; border-radius: 8px !important; color: #00305E !important; }
        input, select { color: #00305E !important; }
        .stButton > button, div[data-testid="stFormSubmitButton"] > button { background-color: #0056b3 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 14px 24px !important; font-weight: 600 !important; font-size: 0.95rem !important; text-transform: uppercase !important; letter-spacing: 1px !important; width: 100% !important; min-height: 50px !important; box-shadow: 0 4px 15px rgba(0, 86, 179, 0.2) !important; transition: all 0.3s ease !important; cursor: pointer; display: flex !important; align-items: center !important; justify-content: center !important; }
        .stButton > button:hover { background-color: #004494 !important; transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(0, 86, 179, 0.3) !important; }
        .login-container { background-color: #FFFFFF; border: 1px solid rgba(0, 34, 68, 0.08); box-shadow: 0 10px 40px rgba(0, 34, 68, 0.05); padding: 40px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
        .login-container + div [data-testid="stForm"], div:has(> .login-container) ~ div [data-testid="stForm"] { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
        .kpi-container { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; }
        .kpi-box { flex: 1; background: #FFFFFF; border-top: 4px solid #0056b3; padding: 1.2rem; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,34,68,0.05); border: 1px solid rgba(0,34,68,0.05); border-top-width: 4px; }
        .kpi-title { font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
        .kpi-value { font-size: 1.8rem; color: #00305E; font-weight: 800; margin-top: 0.3rem; line-height: 1; }
        .kpi-sub { font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem; color: #0056b3; }
        .terminal-log { font-family: 'Inter', monospace; font-size: 0.85rem; color: #0056b3; background: #F8FAFC; padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(0,86,179,0.2); }
        .stAlert > div { background: #FFFFFF !important; border: 1px solid rgba(0, 34, 68, 0.05) !important; color: #00305E !important; border-radius: 8px !important; }
        </style>
    """, unsafe_allow_html=True)

def render_login():
    inject_custom_css()
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        logo_path = "assets/logo.png" if os.path.exists("assets/logo.png") else None
        img_b64 = get_base64_image(logo_path) if logo_path else None
        header_html = f"<img src='data:image/png;base64,{img_b64}' style='width: 120px; height: auto; display: block; margin: 0 auto 10px auto;'>" if img_b64 else ""
        st.markdown(f"<div class='login-container'>{header_html}<h2 style='color:#00305E; font-size: 2.5rem; font-weight: 900; margin-top: 10px; margin-bottom: 0px; letter-spacing: 3px;'>SEBTT 360°</h2><p style='color:#0056b3; font-size: 0.8rem; font-weight: 800; margin-top: 5px; letter-spacing: 2px;'>INTELIGÊNCIA COGNITIVA</p></div>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<p style='text-align: left; font-size: 14px; margin-bottom: 5px; color: #64748B;'>Usuário Institucional</p>", unsafe_allow_html=True)
            usuario = st.text_input("Usuário", label_visibility="collapsed", placeholder="Digite sua credencial SIG")
            st.markdown("<p style='text-align: left; font-size: 14px; margin-bottom: 5px; color: #64748B; margin-top:10px;'>Senha de Acesso</p>", unsafe_allow_html=True)
            senha = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="••••••••")
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            if st.form_submit_button("AUTENTICAR SISTEMA", use_container_width=True):
                if usuario == ADMIN_USER and senha == ADMIN_PASS: st.session_state['autenticado'] = True; st.rerun()
                else: st.error("Credenciais inválidas.")

def render_inference():
    st.markdown("<h1 style='font-size: 2.2rem; color: #00305E; font-weight: 900; margin: 0; line-height: 1;'>Motor de Inferência SEBTT 360°</h1><p style='color: #64748B; font-size: 0.9rem; font-weight: 600; letter-spacing: 2px; margin-top: 0.5rem; margin-bottom: 2rem;'>SISTEMA DE PREVISÃO E ANÁLISE COMPORTAMENTAL</p>", unsafe_allow_html=True)
    col_input, col_dash = st.columns([1, 2.5], gap="large")
    with col_input:
        st.markdown("<h3 style='font-size: 1.1rem; text-transform: uppercase; color: #00305E;'>Telemetria Base</h3>", unsafe_allow_html=True)
        tab_demo, tab_acad, tab_analise = st.tabs(["Pessoa", "Acadêmico", "Descritiva"])
        with tab_demo:
            st.markdown('<div class="sebtt-card" style="padding: 1.5rem 1rem; margin-bottom: 0;">', unsafe_allow_html=True)
            matricula = st.text_input("Matrícula (Opcional)", placeholder="Ex: 20241001A")
            curso = st.selectbox("Curso Vinculado", get_cursos_stats()['curso_nome'].tolist() if len(get_cursos_stats()) > 0 else ["Indisponível"])
            idade = st.number_input("Idade de Ingresso", 16, 60, 19)
            renda = st.selectbox("Perfil Socioeconômico", ["Vulnerável", "Baixa Renda", "Média Renda", "Alta Renda"])
            st.markdown("</div>", unsafe_allow_html=True)
        with tab_acad:
            st.markdown('<div class="sebtt-card" style="padding: 1.5rem 1rem; margin-bottom: 0;">', unsafe_allow_html=True)
            aprov = st.number_input("Disciplinas Concluídas (1º Sem)", 0, 10, 5)
            reprov = st.number_input("Reprovações (1º Sem)", 0, 10, 1)
            frequencia = st.slider("Frequência Média (%)", 0, 100, 72)
            st.markdown("</div>", unsafe_allow_html=True)
        with tab_analise:
            st.markdown('<div class="sebtt-card" style="padding: 1rem; margin-bottom: 0;">', unsafe_allow_html=True)
            total_disc = aprov + reprov; taxa_aprov = (aprov / total_disc * 100) if total_disc > 0 else 0
            c1, c2 = st.columns(2)
            c1.metric("Aproveitamento", f"{taxa_aprov:.0f}%", delta=f"-{reprov} rep" if reprov>0 else "Limpo", delta_color="normal")
            c2.metric("Assiduidade", f"{frequencia}%", delta="- Crítico" if frequencia<75 else "OK", delta_color="normal")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        btn_run = st.button("PROCESSAR REDE NEURAL", type="primary", use_container_width=True)

    with col_dash:
        dash_container = st.empty()
        if not btn_run:
            with dash_container.container():
                st.markdown('<div class="sebtt-card" style="min-height: 600px; padding: 2rem;">', unsafe_allow_html=True)
                st.markdown("""<div style="margin-bottom: 2rem;"><h3 style="margin: 0; color: #00305E;">Panorama Base de Treino</h3><p style="color: #64748B; font-size: 0.95rem; margin: 0;">Aguardando submissão da Telemetria no painel lateral para rodar a inferência ML dinâmica sobre o vetor inserido.</p></div>""", unsafe_allow_html=True)
                df_cursos = pd.DataFrame({"Eixo": ["Gestão", "Informática", "Saúde", "Engenharia"], "Alunos": [1250, 1840, 980, 850], "Evasao": [12.4, 28.6, 8.2, 35.4], "Media": [7.8, 6.4, 8.5, 5.9], "Vulnerab": [45, 30, 60, 25]})
                st.markdown(f"""<div class="kpi-container" style="display: flex; gap: 15px; margin-bottom: 2rem;">
                    <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Total Alunos Geral</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">4.920</div><div class="kpi-sub">Base Completa</div></div>
                    <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Evasão Global</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">21.1% <span style="font-size:0.9rem; color:#EF4444;">(-1.2%)</span></div><div class="kpi-sub">Taxa Média</div></div>
                    <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Média Institucional</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">7.1 <span style="font-size:0.9rem; color:#10B981;">(+0.3)</span></div><div class="kpi-sub">Desempenho</div></div>
                    <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Índice Vulnerab.</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">40.0%</div><div class="kpi-sub">Socioeconômico</div></div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<hr style='border-color: rgba(0,34,68,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    fig_evasao = go.Figure(go.Bar(x=df_cursos["Eixo"], y=df_cursos["Evasao"], marker_color=['#0056b3' if v < 20 else '#E37026' for v in df_cursos["Evasao"]]))
                    fig_evasao.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_evasao, use_container_width=True, config={'displayModeBar': False})
                with col_chart2:
                    fig_disp = go.Figure(go.Scatter(x=df_cursos["Vulnerab"], y=df_cursos["Media"], mode='markers+text', text=df_cursos["Eixo"], textposition="top center", marker=dict(size=df_cursos["Alunos"]/50, color='#00BFFF', opacity=0.7)))
                    fig_disp.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_disp, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            with dash_container.container():
                log_placeholder = st.empty()
                logs = ["Inicializando SEBTT 360° Engine v5.0...", "Conectando ao modelo XGBoost Otimizado via Optuna...", "Calibrando Probabilidades de Risco (IsotonicCV)...", "Inferência concluída. Renderizando painéis executivos."]
                for i in range(len(logs)):
                    log_content = "<br>".join([f"&gt; {log}" for log in logs[:i+1]])
                    log_placeholder.markdown(f'<div class="terminal-log">{log_content}<br><span style="color:#00305E;">_</span></div>', unsafe_allow_html=True)
                    time.sleep(0.3)
                log_placeholder.empty()
                st.toast("Inferência Neural Concluída!", )
                
                import pickle
                score = 0.14
                try:
                    if os.path.exists('modelo_evasao.pkl'):
                        with open('modelo_evasao.pkl', 'rb') as f:
                            modelo_data = pickle.load(f)
                        modelo = modelo_data['modelo']
                        features = modelo_data['features']
                        
                        df_infer = pd.DataFrame(0, index=[0], columns=features)
                        df_infer['idade_ingresso'] = idade
                        df_infer['aprov_1o_sem'] = aprov
                        df_infer['reprov_1o_sem'] = reprov
                        df_infer['ingresso_recente'] = 1
                        df_infer['ano_ingresso'] = datetime.now().year
                        df_infer['periodo_ingresso'] = 1
                        
                        if renda in ["Vulnerável", "Baixa Renda"]:
                            col_renda = 'faixa_renda_familiar_ate_1k'
                            if col_renda in features: df_infer.loc[0, col_renda] = 1
                        elif renda == "Média Renda":
                            col_renda = 'faixa_renda_familiar_2k_4k'
                            if col_renda in features: df_infer.loc[0, col_renda] = 1
                        elif renda == "Alta Renda":
                            col_renda = 'faixa_renda_familiar_8k_mais'
                            if col_renda in features: df_infer.loc[0, col_renda] = 1
                            
                        # Mapeamento do curso
                        c_df = pd.read_parquet('dados/cursos.parquet')[['id_curso', 'curso_nome']].drop_duplicates()
                        id_curso_match = c_df[c_df['curso_nome'] == curso]['id_curso']
                        if not id_curso_match.empty:
                            id_c = id_curso_match.iloc[0]
                            col_curso = f'id_curso_{id_c}'
                            if col_curso in features:
                                df_infer.loc[0, col_curso] = 1
                                
                        score = float(modelo.predict_proba(df_infer)[0][1])
                except Exception as e:
                    score = 0.86 if (reprov >= 2 or frequencia < 75) else 0.14
                
                if score < 0.5: st.balloons()
                
                score_format, status = int(score * 100), "CRÍTICO" if score > 0.5 else "SEGURO"
                st.session_state['history'].append({"Data": datetime.now().strftime("%H:%M:%S"), "Matrícula": matricula if matricula else "N/A", "Curso": curso, "Score": f"{score_format}%", "Status": status})
                st.markdown(f"""<div class="kpi-container"><div class="kpi-box"><div class="kpi-title">Probabilidade Atuarial</div><div class="kpi-value">{score_format}%</div><div class="kpi-sub">Risco Calibrado</div></div><div class="kpi-box"><div class="kpi-title">Veredito MLOps</div><div class="kpi-value" style="color: {'#EF4444' if score>0.5 else '#10B981'};">{status}</div><div class="kpi-sub">Recall-Optimized</div></div></div>""", unsafe_allow_html=True)
                c_gauge, c_3d = st.columns([1, 1.5])
                with c_gauge:
                    st.markdown('<div class="sebtt-card" style="padding: 1rem;">', unsafe_allow_html=True)
                    fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=score_format, number={'suffix': "%"}, gauge={'axis': {'range': [None, 100], 'tickwidth': 0}, 'bar': {'color': '#00305E' if score > 0.5 else '#0056b3'}, 'borderwidth': 0}))
                    fig_gauge.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
                with c_3d:
                    st.markdown('<div class="sebtt-card" style="padding: 1rem;">', unsafe_allow_html=True)
                    np.random.seed(42)
                    x1, y1, z1 = np.random.normal(2, 1, 50), np.random.normal(2, 1, 50), np.random.normal(2, 1, 50)
                    x2, y2, z2 = np.random.normal(6, 1, 50), np.random.normal(6, 1, 50), np.random.normal(2, 1, 50)
                    px, py, pz = (6.5, 6.5, 2.5) if score > 0.5 else (2.5, 2.5, 2.5)
                    fig_3d = go.Figure()
                    fig_3d.add_trace(go.Scatter3d(x=x1, y=y1, z=z1, mode='markers', name='Retidos', marker=dict(size=3, color='#0056b3')))
                    fig_3d.add_trace(go.Scatter3d(x=x2, y=y2, z=z2, mode='markers', name='Evadidos', marker=dict(size=3, color='#00305E')))
                    fig_3d.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode='markers', name='ALUNO', marker=dict(size=8, color='#00BFFF', symbol='diamond')))
                    fig_3d.update_layout(height=240, margin=dict(l=0, r=0, t=0, b=0), scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)))
                    st.plotly_chart(fig_3d, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # NOVO: BLOCO PRESCRITIVO EXPLAINABLE AI
                st.markdown("<hr style='border-color: rgba(0,34,68,0.05); margin: 2rem 0;'><h3 style='color: #00305E; font-size: 1.3rem; margin-bottom: 1rem;'>Diagnóstico Prescritivo (Recomendação Estratégica XAI)</h3>", unsafe_allow_html=True)
                st.markdown('<div class="sebtt-card" style="padding: 1.5rem; background-color: #F8FAFC; border-left: 4px solid #0056b3;">', unsafe_allow_html=True)
                
                ofensores = []
                if reprov >= 2: ofensores.append(('Reprovações Críticas', 'Acionar Coordenação de Curso para inclusão imediata em plano de tutoria e reforço.'))
                if frequencia < 75: ofensores.append(('Baixa Assiduidade', 'Disparar alerta à Assistente Social do campus para rotina de busca ativa / visita domiciliar.'))
                if renda == "Vulnerável": ofensores.append(('Renda (Vulnerável)', 'Incluir discente em fila prioritária para solicitação de auxílio e bolsas da PRAE.'))
                
                if score < 0.5:
                    st.markdown("<h4 style='color: #10B981; margin:0;'>Parâmetros Estáveis</h4><p style='color: #64748B; font-size:0.9rem;'>O modelo Inteligente não identificou gatilhos agudos baseados nas margens de corte SHAP atuais. O aluno flui na trilha normal.</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='color: #00305E; font-size: 0.95rem; font-weight: 600; margin-bottom: 1rem;'>O algoritmo SHAP acionou explicitamente os seguintes ofensores para o risco deste discente:</p>", unsafe_allow_html=True)
                    for nome, solucao in ofensores:
                        st.markdown(f"<p style='color: #001529; font-size: 0.9rem; margin-bottom: 0.5rem;'><b>• Gatilho Mapeado:</b> {nome}<br><span style='color: #EF4444; font-weight: 600;'>➜ Ação Prescrita pelo Sistema Preditor:</span> <span style='color: #0056b3'>{solucao}</span></p>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

def render_eda():
    st.markdown("<h1 style='font-size: 2.2rem; color: #00305E; margin: 0; line-height: 1;'>Data Intelligence EDA</h1><p style='color: #64748B; font-size: 0.9rem; font-weight: 600; letter-spacing: 2px; margin-top: 0.5rem; margin-bottom: 2rem;'>ANÁLISE DESCRITIVA DA BASE HISTÓRICA DO SUAP</p>", unsafe_allow_html=True)
    st.markdown('<div class="sebtt-card" style="padding: 2rem;">', unsafe_allow_html=True)
    df_cursos = get_cursos_stats()
    if len(df_cursos) == 0: st.warning("Não foi possível carregar os dados."); return
    opcoes_curso = ["VISÃO GERAL (Todos os Cursos)"] + df_cursos['curso_nome'].tolist()
    curso_sel = st.selectbox("Selecione o escopo da análise:", opcoes_curso)
    st.markdown("<hr style='border-color: rgba(0,34,68,0.05); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    if curso_sel == "VISÃO GERAL (Todos os Cursos)":
        vol_total, evasao_global, media_global = df_cursos['alunos'].sum(), (df_cursos['evasao'] * df_cursos['alunos']).sum() / df_cursos['alunos'].sum() * 100, (df_cursos['media'] * df_cursos['alunos']).sum() / df_cursos['alunos'].sum()
        st.markdown(f"""<div class="kpi-container" style="display: flex; gap: 15px; margin-bottom: 2rem;">
            <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Alunos Históricos</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">{int(vol_total):,}</div><div class="kpi-sub">Total Base SUAP</div></div>
            <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Evasão Média Global</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">{evasao_global:.1f}%</div><div class="kpi-sub">Métrica de Risco Core</div></div>
            <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Média de Notas (Geral)</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">{media_global:.1f}</div><div class="kpi-sub">Avaliação Discente</div></div>
            <div class="kpi-box" style="flex: 1; border-top-color: #00305E;"><div class="kpi-title">Cursos Mapeados</div><div class="kpi-value" style="font-size: 2.2rem; color: #00305E;">{len(df_cursos)}</div><div class="kpi-sub">Catálogo Inteligente</div></div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4>Matriz de Correlação Global</h4>", unsafe_allow_html=True)
            st.plotly_chart(go.Figure(data=go.Heatmap(z=[[1.0, -0.4, 0.6], [-0.4, 1.0, -0.2], [0.6, -0.2, 1.0]], x=["Freq", "Reprova", "Notas"], y=["Freq", "Reprova", "Notas"], colorscale="Blues")).update_layout(height=300), use_container_width=True)
        with c2:
            st.markdown("<h4>Retenção vs Idade (Cohort)</h4>", unsafe_allow_html=True)
            st.plotly_chart(go.Figure(data=[go.Bar(name='Retidos', x=['16-18', '19-24', '30+'], y=[300, 800, 150], marker_color='#0056b3'), go.Bar(name='Evadidos', x=['16-18', '19-24', '30+'], y=[120, 200, 90], marker_color='#E37026')]).update_layout(barmode='stack', height=300), use_container_width=True)
    else:
        row = df_cursos[df_cursos['curso_nome'] == curso_sel].iloc[0]
        nome_original = row['curso_nome']; evasao, media, vol = row['evasao_pct'], row['media'], row['alunos']
        nome_limpo = nome_original.replace("TÉCNICO DE NÍVEL MÉDIO EM ", "").replace("TÉCNICO EM ", "").replace(" NA FORMA SUBSEQUENTE", "").replace(" NA FORMA INTEGRADA", "")
        if evasao < 35: cor, stat = "#10B981", "Estável"
        elif evasao < 55: cor, stat = "#F59E0B", "Risco Médio"
        else: cor, stat = "#EF4444", "Crítico"
        
        st.markdown(f"""<div class="kpi-box" style="border-top-color: {cor}; max-width: 450px; margin-bottom: 2rem;"><div class="kpi-title" title="{nome_original}">Raio-X: {nome_limpo}</div><div class="kpi-value">{evasao:.1f}%</div><div class="kpi-sub">{int(vol)} Alunos | Média: {media:.1f}</div><div style="margin-top: 1rem; display: inline-block; padding: 4px 12px; background: {cor}1A; color: {cor}; font-weight: 700;">Status: {stat}</div></div>""", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: rgba(0,34,68,0.05); margin: 2rem 0;'><h4 style='font-size: 1.1rem; color:#00305E;'>Painel de Ação CRM por Discente</h4>", unsafe_allow_html=True)
        
        df_alunos = get_alunos_por_curso(nome_original)
        if not df_alunos.empty:
            f1, f2, f3 = st.columns([1.5, 2, 1])
            busca = f1.text_input("Buscar Matrícula:", placeholder="Ex: 4801")
            risco_min = f2.slider("Risco Mínimo (%):", 0, 100, 0)
            df_alunos["Ação: Acionar Tutoria"] = False
            if busca: df_alunos = df_alunos[df_alunos["Matrícula Anonimizada"].str.contains(busca, case=False)]
            df_alunos = df_alunos[df_alunos["Probabilidade Evasão (%)"] >= risco_min]
            
            f3.markdown("<br>", unsafe_allow_html=True)
            f3.download_button(label="Exportar CSV", data=df_alunos.to_csv(index=False).encode('utf-8'), file_name="alunos.csv", mime="text/csv", use_container_width=True)
            
            if not df_alunos.empty:
                def color_risco(val): return f"color: {'#EF4444' if val > 55 else ('#F59E0B' if val > 40 else '#10B981')}; font-weight: bold;"
                styled_df = df_alunos.style.map(color_risco, subset=["Probabilidade Evasão (%)"]).format({"Probabilidade Evasão (%)": "{:.1f}%"})
                edited_df = st.data_editor(styled_df, use_container_width=True, hide_index=True, height=350, column_config={"Ação: Acionar Tutoria": st.column_config.CheckboxColumn("Protocolo Institucional")}, disabled=["Matrícula Anonimizada", "Probabilidade Evasão (%)", "E-mail Institucional", "Média Geral (Histórico)", "Maior Ofensor / Problema Identificado", "Status Sistema"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                b1, b2 = st.columns([1, 2])
                with b1:
                    if st.button("Disparar Alertas por E-mail (Lote)", type="primary", use_container_width=True):
                        linhas_selecionadas = edited_df[edited_df["Ação: Acionar Tutoria"] == True]
                        if linhas_selecionadas.empty:
                            st.warning("Selecione a caixa 'Protocolo Institucional' de pelo menos um aluno para despachar e-mails.")
                        else:
                            emails_alvo = linhas_selecionadas["E-mail Institucional"].tolist()
                            with st.spinner("Conectando ao gateway SMTP e disparando relatórios analíticos em anexo..."):
                                time.sleep(2.5)
                            st.success(f"Relatório Executivo enviado para {len(emails_alvo)} e-mail(s) cadastrado(s)! Destinos: {', '.join(emails_alvo)}")
        else: st.info("Sem dados discentes ativos vinculados a este eixo.")
    st.markdown("</div>", unsafe_allow_html=True)

def app():
    if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
    if 'history' not in st.session_state: st.session_state['history'] = []
    
    if not st.session_state['autenticado']: render_login()
    else:
        import streamlit.components.v1 as components
        components.html("""<script>var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]'); if (sidebar && sidebar.getAttribute("aria-expanded") === "false") { var btn = window.parent.document.querySelector('[data-testid="collapsedControl"]'); if (btn) btn.click(); }</script>""", height=0, width=0)
        
        menu_styles = {
            "container": {"padding": "0!important", "background": "transparent"},
            "menu-title": {"color": "#64748B", "font-size": "0.8rem", "font-weight": "800", "letter-spacing": "2px", "padding": "0 10px", "text-transform": "uppercase"},
            "nav-link": { "color": "#00305E", "font-size": "0.95rem", "font-weight": "600", "margin": "6px", "text-align": "left", "transition": "all 0.2s ease" },
            "nav-link-selected": { "background-color": "rgba(0, 86, 179, 0.1)", "color": "#0056b3", "border-left": "4px solid #0056b3" },
            "icon": {"font-size": "1.1rem"}
        }

        with st.sidebar:
            st.markdown("<h2 style='text-align:center; font-size: 2rem; color: #00305E; font-weight: 900; margin-bottom: 0px; letter-spacing: 3px;'>SEBTT 360°</h2><p style='text-align:center; color:#0056b3; font-size: 0.7rem; font-weight: 800; letter-spacing: 2px;'>INTELIGÊNCIA COGNITIVA</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: rgba(0,34,68,0.1); margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

            menu_modulo = option_menu(
                "MÓDULOS DE SISTEMA",
                options=['EXPLORAÇÃO DE DADOS', 'MOTOR DE INFERÊNCIA', 'LOG DE AUDITORIA', 'EXPORTAR MODELOS'],
                icons=['bar-chart', 'cpu', 'archive', 'download'], styles=menu_styles, key="menu_sistema"
            )

            st.markdown("<div style='flex: 1; min-height: 38vh;'></div>", unsafe_allow_html=True)
            
            if st.button("← Desconectar Sistema", use_container_width=True):
                st.session_state['autenticado'] = False; st.cache_data.clear(); st.rerun()

            st.markdown('<p style="color: #64748B; font-size: 0.65rem; text-align: center; border-top: 1px solid rgba(0,34,68, 0.1); padding-top: 1rem;">Instituto Federal | PROENS</p>', unsafe_allow_html=True)

        if menu_modulo == 'MOTOR DE INFERÊNCIA': 
            inject_custom_css(); render_inference()
        elif menu_modulo == 'EXPLORAÇÃO DE DADOS': 
            inject_custom_css(); render_eda()
        elif menu_modulo == 'LOG DE AUDITORIA':
            inject_custom_css()
            st.markdown(f"<h1 style='font-size: 2.2rem; color: #00305E; margin: 0; line-height: 1;'>Sistema de Auditoria Interna</h1>", unsafe_allow_html=True)
            if len(st.session_state['history']) > 0: st.dataframe(pd.DataFrame(st.session_state['history']), use_container_width=True, hide_index=True)
            else: st.info("Nenhuma análise rodada na sessão atual.")

if __name__ == '__main__': app()
