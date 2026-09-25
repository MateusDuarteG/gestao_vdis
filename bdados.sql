-- Criação do banco de dados (caso não exista)
CREATE DATABASE IF NOT EXISTS vdi_db;
USE vdi_db;

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Instâncias VDI
CREATE TABLE IF NOT EXISTS instancias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    container_id VARCHAR(100) NOT NULL,
    tipo_ambiente VARCHAR(50) NOT NULL,
    porta_mapeada VARCHAR(10),
    status VARCHAR(20) DEFAULT 'ativo',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    encerrado_em TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES usuarios(id)
);

-- Tabela de Logs de Uso/Auditoria
CREATE TABLE IF NOT EXISTS logs_acesso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instancia_id INT NOT NULL,
    acao VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instancia_id) REFERENCES instancias(id)
);

-- Inserindo um usuário de teste (ID 1)
INSERT INTO usuarios (id, nome, email) 
VALUES (1, 'Usuario Teste', 'teste@vdi.com')
ON DUPLICATE KEY UPDATE nome=nome;