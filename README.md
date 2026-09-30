# 🖥️ Gestão de VDIs

Uma aplicação completa desenvolvida para facilitar a gestão, monitoramento e controle de ambientes de **VDI (Virtual Desktop Infrastructure)**.

---

## 📌 Funcionalidades

- 📊 **Dashboard Interativo:** Visualização do status das máquinas virtuais e métricas do ambiente em tempo real.
- 🔌 **Integração via API:** Endpoints para gerenciamento e automação do ciclo de vida das VDIs.
- 🗄️ **Gestão de Dados:** Estrutura relacional para armazenamento de dados e histórico do sistema.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python
- **Interface/Dashboard:** Streamlit / Dash / Flask *(ajuste conforme sua biblioteca)*
- **API:** FastAPI / Flask
- **Banco de Dados:** SQLite / MySQL

---

## 📂 Estrutura do Projeto

```text
gerenciamentodevdi/
├── api.py           # Endpoints da API de gerenciamento
├── dashboard.py     # Interface do dashboard de monitoramento
├── bdados.sql       # Script de criação do banco de dados
└── README.md        # Documentação do projeto
