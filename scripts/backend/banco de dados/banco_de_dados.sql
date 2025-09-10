CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(50),
    sobrenome VARCHAR(100),
    apelido VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(60) NOT NULL, 
    data_nascimento DATE,
    tipo_pessoa VARCHAR(10) CHECK (tipo_pessoa IN ('aluno', 'professor'))
);

CREATE TABLE Escolas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cidade VARCHAR(150),
    estado CHAR(2)
);

CREATE TABLE Alunos (
    id_profile UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
    pontuacao_total INT DEFAULT 0,
    avatar_url VARCHAR(255),
    id_escola INT REFERENCES Escolas(id) ON DELETE SET NULL
);

CREATE TABLE Professores (
    id_profile UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE TABLE Professor_Escolas (
    id_professor UUID REFERENCES Professores(id_profile) ON DELETE CASCADE,
    id_escola INT REFERENCES Escolas(id) ON DELETE CASCADE,
    PRIMARY KEY (id_professor, id_escola)
);

CREATE TABLE Turmas (
    id SERIAL PRIMARY KEY,
    id_professor UUID NOT NULL REFERENCES Professores(id_profile) ON DELETE CASCADE,
    id_escola INT NOT NULL REFERENCES Escolas(id) ON DELETE CASCADE,
    nome VARCHAR(150) NOT NULL,
    codigo_convite VARCHAR(10) UNIQUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Turma_Alunos (
    id_turma INT REFERENCES Turmas(id) ON DELETE CASCADE,
    id_aluno UUID REFERENCES Alunos(id_profile) ON DELETE CASCADE,
    PRIMARY KEY (id_turma, id_aluno)
);

CREATE TABLE Locais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    url_midia VARCHAR(255)
);

CREATE TABLE QRCodes (
    id SERIAL PRIMARY KEY,
    codigo_unico VARCHAR(255) UNIQUE NOT NULL,
    id_local INT REFERENCES Locais(id) ON DELETE SET NULL,
    titulo_conteudo VARCHAR(255),
    descricao_conteudo TEXT,
    pontos INT NOT NULL DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE Leituras (
    id SERIAL PRIMARY KEY,
    id_aluno UUID NOT NULL REFERENCES Alunos(id_profile) ON DELETE CASCADE,
    id_qrcode INT NOT NULL REFERENCES QRCodes(id) ON DELETE CASCADE,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pontos_ganhos INT NOT NULL,
    UNIQUE(id_aluno, id_qrcode)
);
