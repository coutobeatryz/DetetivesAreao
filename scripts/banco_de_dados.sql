CREATE TABLE Pessoas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    sobrenome VARCHAR(100),
    apelido VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    data_nascimento DATE,
    tipo_pessoa VARCHAR(10) NOT NULL CHECK (tipo_pessoa IN ('aluno', 'professor'))
);

CREATE TABLE Escolas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cidade VARCHAR(150),
    estado CHAR(2)
);

CREATE TABLE Alunos (
    id_pessoa INT PRIMARY KEY,
    pontuacao_total INT DEFAULT 0,
    avatar_url VARCHAR(255),
    id_escola INT,
    FOREIGN KEY (id_pessoa) REFERENCES Pessoas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_escola) REFERENCES Escolas(id) ON DELETE SET NULL
);

CREATE TABLE Professores (
    id_pessoa INT PRIMARY KEY,
    FOREIGN KEY (id_pessoa) REFERENCES Pessoas(id) ON DELETE CASCADE
);

CREATE TABLE Professor_Escolas (
    id_professor INT,
    id_escola INT,
    PRIMARY KEY (id_professor, id_escola),
    FOREIGN KEY (id_professor) REFERENCES Professores(id_pessoa) ON DELETE CASCADE,
    FOREIGN KEY (id_escola) REFERENCES Escolas(id) ON DELETE CASCADE
);

CREATE TABLE Turmas (
    id SERIAL PRIMARY KEY,
    id_professor INT NOT NULL,
    id_escola INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    codigo_convite VARCHAR(10) UNIQUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_professor) REFERENCES Professores(id_pessoa) ON DELETE CASCADE,
    FOREIGN KEY (id_escola) REFERENCES Escolas(id) ON DELETE CASCADE
);

CREATE TABLE Turma_Alunos (
    id_turma INT,
    id_aluno INT,
    PRIMARY KEY (id_turma, id_aluno),
    FOREIGN KEY (id_turma) REFERENCES Turmas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_aluno) REFERENCES Alunos(id_pessoa) ON DELETE CASCADE
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
    id_local INT,
    titulo_conteudo VARCHAR(255),
    descricao_conteudo TEXT,
    pontos INT NOT NULL DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_local) REFERENCES Locais(id) ON DELETE SET NULL
);

CREATE TABLE Leituras (
    id SERIAL PRIMARY KEY,
    id_aluno INT NOT NULL,
    id_qrcode INT NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pontos_ganhos INT NOT NULL,
    UNIQUE(id_aluno, id_qrcode),
    FOREIGN KEY (id_aluno) REFERENCES Alunos(id_pessoa) ON DELETE CASCADE,
    FOREIGN KEY (id_qrcode) REFERENCES QRCodes(id) ON DELETE CASCADE
);