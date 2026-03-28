# SEBTT 360° - Inteligência Cognitiva Aplicada à Evasão Acadêmica

![SEBTT 360](https://img.shields.io/badge/Status-Em_Desenvolvimento-blue)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blueviolet)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.2-FF4B4B)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-orange)

🚀 **SEBTT 360°** é uma plataforma e motor analítico ("SEBTT Engine") de Machine Learning focado em diagnosticar, monitorar e prever a evasão e a retenção de alunos em tempo real. Utiliza Painéis Executivos Institucionais (EDA interativo) e algoritmos de ML robustos como XGBoost otimizado com Optuna e XAI (Explainable AI com SHAP). 

---

## 🎯 Objetivos do Projeto
- **Exploração de Dados Institucional:** Identificar falhas sistêmicas na trilha de alunos usando bases extraídas do SUAP (Média, Assiduidade, Reprovações, etc).
- **Motor de Inferência Atuarial:** Inserir dados do estudante através de Telemetria e receber o risco de evasão calibrado, avaliado pelo algoritmo em conjunto com Painel 3D de Coorte.
- **Auditoria Plena:** Monitorar alunos críticos e extrair tabelas e alertas para coordenadores adotarem ações prescritivas de tutoria ativa.

---

## 📂 Arquitetura do Diretório

```plaintext
SEBTT_360/
├── app.py                      # Aplicação Principal do Dashboard Streamlit
├── preparacao_dados.ipynb      # Pipeline de Data Science (Limpeza, Optuna, Treino e Validação)
├── modelo_evasao.pkl           # (Artefato) Modelo ML Serializado Final
├── requirements.txt            # Dependências Python para recriar o ambiente
├── dados/
│   ├── cursos.parquet          # Histórico tabular compactado dos Cursos
│   └── discentes.parquet       # Histórico tabular compactado dos Alunos
├── .assets/                    # Material de UI/Identidade Visual (Logos)
└── .streamlit/
    └── secrets.toml            # Credenciais estáticas do administrador do app
```

## ⚙️ Instalação e Execução (Guia Rápido)

**1. Baixe o Repositório e acesse a pasta do projeto no Terminal:**
```bash
cd caminho/para/seu/projeto/SEBTT_360
```

**2. Opcional porém recomendado: Crie e ative um Ambiente Virtual:**
```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

**3. Instale todas as Bibliotecas listadas no `requirements.txt`:**
```bash
pip install -r requirements.txt
```

**4. Arquivo de Senhas:**
Certifique-se de preencher corretamente as chaves no seu `.streamlit/secrets.toml` antes de rodar.
```toml
ADMIN_USER = "seu_usuario"
ADMIN_PASS = "sua_senha"
```

**5. Execute o Front-End da Aplicação:**
```bash
streamlit run app.py
```

---

## 🧠 Ciclo de Vida do Machine Learning
O arquivo base de inteligência (`preparacao_dados.ipynb`) contempla uma visão madura em Governança ML:
1. **Engenharia de Rótulos:** Tradução dos status Cancelados/Evadidos em Label Encoding (1 ou 0).
2. **Treino Base XGBClassifier:** Pesado para tratar matrizes altamente desbalanceadas (`scale_pos_weight`).
3. **Optuna HPO:** Otimização Bayesiana iterativa buscando a métrica otimizadora focada na Curva PR-AUC (Precision-Recall) no lugar do ROC genérico.
4. **Isotonic Calibration:** Calibração estatística de hiper-probabilidades (Risco) e busca pelo ponto central pragmático de restrição de Falso Negativo (Custo maior na vida real acadêmica).
5. **SHAP Analysis (Interpretabilidade):** Explicação matemática detalhada provando _por que_ o motor tomou determinada provisão (Ex. Falta > Renda).
