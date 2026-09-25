import streamlit as st
import requests

st.set_page_config(page_title="Painel VDI", layout="wide")
st.title("🖥️ Meu Painel VDI - Minhas Áreas de Trabalho")

# Botão para criar nova instância
if st.button("🚀 Criar Novo Desktop Ubuntu"):
    try:
        res = requests.post("http://localhost:8000/instances/create?user_id=1&environment_type=ubuntu_desktop")
        if res.status_code == 200:
            data = res.json()
            st.success("Área de trabalho criada com sucesso!")
            st.markdown(f"[👉 Clique aqui para Acessar sua VDI]({data['access_url']})")
            st.rerun()
        else:
            st.error("Erro ao criar a instância na API.")
    except Exception as e:
        st.error(f"Não foi possível conectar à API: {e}")

st.divider()

# Dashboard de Recursos
st.subheader("📊 Consumo de Recursos do Sistema")

try:
    metrics_res = requests.get("http://localhost:8000/metrics")
    if metrics_res.status_code == 200:
        metrics = metrics_res.json()
        ativos = metrics.get("active_containers", 0)
        limite = metrics.get("max_limit", 5)
        ram_percent = metrics.get("ram_usage_percent", 0.0)

        st.metric(label="Contêineres Ativos", value=f"{ativos} / {limite}")
        st.progress(ram_percent / 100, text=f"Uso Geral de RAM: {ram_percent}%")
    else:
        st.error("Falha ao obter métricas da API.")
except Exception:
    st.metric(label="Contêineres Ativos", value="Desconectado")

st.divider()

# Minhas Instâncias Ativas com botão de exclusão
st.subheader("🖥️ Gerenciar Instâncias Ativas")

try:
    instances_res = requests.get("http://localhost:8000/instances/active")
    if instances_res.status_code == 200:
        instancias = instances_res.json()

        if not instancias:
            st.info("Nenhuma área de trabalho ativa no momento.")
        else:
            for item in instancias:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"🖥️ **ID:** `{item['short_id']}`")
                with col2:
                    if item['access_url']:
                        st.markdown(f"[🔗 Abrir VDI]({item['access_url']})")
                with col3:
                    if st.button("🔴 Encerrar", key=item['container_id']):
                        del_res = requests.delete(f"http://localhost:8000/instances/{item['container_id']}")
                        if del_res.status_code == 200:
                            st.success("Instância encerrada!")
                            st.rerun()
                        else:
                            st.error("Erro ao encerrar a instância.")
    else:
        st.error("Não foi possível carregar a lista de instâncias.")
except Exception as e:
    st.warning(f"Erro ao conectar com a API: {e}")