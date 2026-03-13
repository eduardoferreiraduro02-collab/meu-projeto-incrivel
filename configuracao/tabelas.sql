-- Tabela de Alunos (Foco em Metas e Retenção)
CREATE TABLE alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    meta_curso VARCHAR(50),      -- Ex: Medicina
    universidade_alvo VARCHAR(50), -- Ex: USP
    ano_escolar VARCHAR(30),      -- Ex: Cursinho
    status_retencao VARCHAR(20) DEFAULT 'Ativo' -- Ativo, Em Risco, Inativo
);

-- Tabela de Redações (Onde o aluno envia o conteúdo)
CREATE TABLE redacoes (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER REFERENCES alunos(id),
    tema VARCHAR(255),
    texto TEXT,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nota INTEGER
);