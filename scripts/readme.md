## 📌 Modelo de Entidades e Atributos

### 👤 Pessoa
- `id_pessoa` **Int** (PK)
- `nome` **Varchar(50)**
- `sobrenome` **Varchar(100)**
- `apelido` **Varchar(100)** (Unique)
- `email` **Varchar(100)** (Unique)
- `senha_hash` **Varchar(255)**
- `data_nascimento` **Date**
- `tipo_pessoa` **Enum('aluno', 'professor')**

### 🎓 Aluno
- `id_pessoa` **Int** (PK, FK → Pessoa)
- `pontuacao_total` **Int**
- `avatar_url` **Varchar(200)**
- `id_escola` **Int** (FK → Escola)

### 👨‍🏫 Professor
- `id_pessoa` **Int** (PK, FK → Pessoa)

### 🏫 Escola
- `id_escola` **Int** (PK)
- `nome_escola` **Varchar(200)**
- `cidade` **Varchar(200)**
- `estado` **VARCHAR(200)**

### 📚 Professor_Escolas
- `id_pessoa` **Int** (PK, FK → Professor)
- `id_escola` **Int** (PK, FK → Escola)

### 🏷️ Turma
- `id_turma` **Int** (PK)
- `id_professor` **Int** (FK → Professor)
- `nome_turma` **Varchar(30)**
- `codigo_convite` **Varchar(10)** (Unique)
- `data_criacao` **Timestamp**
- `id_escola` **Int** (FK → Escola)

### 📍 Local
- `id_local` **Int** (PK)
- `nome_local` **Varchar(50)**
- `descricao_local` **Varchar(200)**
- `url_midia_local` **Varchar(200)**

### 🔲 QRCode
- `id_qrcode` **Int** (PK)
- `codigo_qr` **Varchar(200)**
- `id_local` **Int** (FK → Local)
- `url_midia_qrcode` **Varchar(200)**
- `pontos_qr` **Int**
- `ativo` **Boolean**
