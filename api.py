import docker
import psutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS (SQLite Local) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./vdi_banco.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class InstanciaBD(Base):
    __tablename__ = "instancias"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    container_id = Column(String(100), nullable=False)
    tipo_ambiente = Column(String(50), nullable=False)
    porta_mapeada = Column(String(10))
    status = Column(String(20), default="ativo")
    criado_em = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        raise RuntimeError("O Docker Desktop não está rodando no sistema.") from e

def cleanup_inactive_containers():
    try:
        client = get_docker_client()
        containers = client.containers.list(filters={"label": "type=vdi-instance"})
        for container in containers:
            print(f"Verificando container {container.short_id}")
    except Exception as e:
        print(f"Aviso no Agendador: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_inactive_containers, 'interval', minutes=15)
    scheduler.start()
    print("🚀 Agendador de tarefas iniciado!")
    yield
    scheduler.shutdown()
    print("🛑 Agendador finalizado.")

app = FastAPI(lifespan=lifespan)

@app.get("/metrics")
def get_metrics():
    try:
        docker_client = get_docker_client()
        containers = docker_client.containers.list(filters={"label": "type=vdi-instance", "status": "running"})
        active_count = len(containers)
        ram_usage = psutil.virtual_memory().percent
        
        return {
            "active_containers": active_count,
            "max_limit": 5,
            "ram_usage_percent": round(ram_usage, 1)
        }
    except Exception as e:
        return {"error": str(e), "active_containers": 0, "max_limit": 5, "ram_usage_percent": 0.0}

@app.get("/instances/active")
def get_active_instances():
    """Retorna todas as instâncias VDI em execução no Docker"""
    try:
        docker_client = get_docker_client()
        containers = docker_client.containers.list(filters={"label": "type=vdi-instance", "status": "running"})
        active_list = []
        for c in containers:
            port = c.ports.get('3000/tcp')
            host_port = port[0]['HostPort'] if port else None
            active_list.append({
                "container_id": c.id,
                "short_id": c.short_id,
                "name": c.name,
                "access_url": f"http://localhost:{host_port}" if host_port else None
            })
        return active_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/instances/create")
def create_vdi_instance(user_id: int, environment_type: str):
    image_map = {
        "ubuntu_desktop": "lscr.io/linuxserver/webtop:ubuntu-xfce",
        "vscode_server": "codercom/code-server:latest"
    }
    
    selected_image = image_map.get(environment_type)
    if not selected_image:
        raise HTTPException(status_code=400, detail="Ambiente inválido")

    try:
        docker_client = get_docker_client()

        try:
            docker_client.images.get(selected_image)
        except docker.errors.ImageNotFound:
            print(f"Baixando imagem {selected_image}...")
            docker_client.images.pull(selected_image)

        container = docker_client.containers.run(
            selected_image,
            detach=True,
            ports={'3000/tcp': None},
            mem_limit="2g",
            nano_cpus=2000000000,
            labels={"owner": str(user_id), "type": "vdi-instance"}
        )

        container.reload()
        mapped_port = container.ports['3000/tcp'][0]['HostPort']

        # Registra no banco
        try:
            db = SessionLocal()
            nova_instancia = InstanciaBD(
                user_id=user_id,
                container_id=container.id,
                tipo_ambiente=environment_type,
                porta_mapeada=str(mapped_port),
                status="ativo"
            )
            db.add(nova_instancia)
            db.commit()
            db.refresh(nova_instancia)
            db.close()
        except Exception as db_err:
            print(f"⚠️ Aviso ao salvar no banco: {db_err}")
        
        return {
            "status": "success",
            "container_id": container.id,
            "access_url": f"http://localhost:{mapped_port}"
        }
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Erro no Docker: {err}")

@app.delete("/instances/{container_id}")
def delete_vdi_instance(container_id: str):
    """Para e remove um contêiner ativo"""
    try:
        docker_client = get_docker_client()
        container = docker_client.containers.get(container_id)
        container.stop()
        container.remove()

        try:
            db = SessionLocal()
            instancia = db.query(InstanciaBD).filter(InstanciaBD.container_id == container_id).first()
            if instancia:
                instancia.status = "encerrado"
                db.commit()
            db.close()
        except Exception as db_err:
            print(f"Aviso BD: {db_err}")

        return {"status": "success", "message": "Instância encerrada com sucesso!"}
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Erro ao encerrar contêiner: {err}")