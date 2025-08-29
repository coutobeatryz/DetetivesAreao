# 📌 Modelo de Entidades e Atributos

### 👤 Pessoa
- `id_pessoa` **INT** (PK)
- `nome` **VARCHAR(50)**
- `sobrenome` **VARCHAR(100)**
- `apelido` **VARCHAR(100)** (UNIQUE)
- `email` **VARCHAR(100)** (UNIQUE)
- `senha_hash` **VARCHAR(255)**
- `data_nascimento` **DATE**
- `tipo_pessoa` **ENUM('aluno', 'professor')**

---

### 🎓 Aluno
- `id_pessoa` **INT** (PK, FK → Pessoa)
- `pontuacao_total` **INT**
- `avatar_url` **VARCHAR(200)**
- `id_escola` **INT** (FK → Escola)

---

### 👨‍🏫 Professor
- `id_pessoa` **INT** (PK, FK → Pessoa)

---

### 🏫 Escola
- `id_escola` **INT** (PK)
- `nome_escola` **VARCHAR(200)**
- `cidade` **VARCHAR(200)**
- `estado` **VARCHAR(200)**

---

### 📚 Professor_Escolas
- `id_pessoa` **INT** (PK, FK → Professor)
- `id_escola` **INT** (PK, FK → Escola)

---

### 🏷️ Turma
*(Criada pelo professor)*  
- `id_turma` **INT** (PK)
- `id_professor` **INT** (FK → Professor)
- `nome_turma` **VARCHAR(30)**
- `codigo_convite` **VARCHAR(10)** (UNIQUE)
- `data_criacao` **TIMESTAMP**
- `id_escola` **INT** (FK → Escola)

---

### 📍 Local
- `id_local` **INT** (PK)
- `nome_local` **VARCHAR(50)**
- `descricao_local` **VARCHAR(200)**
- `url_midia_local` **VARCHAR(200)**

---

### 🔲 QRCode
- `id_qrcode` **INT** (PK)
- `codigo_qr` **VARCHAR(200)**
- `id_local` **INT** (FK → Local)
- `url_midia_qrcode` **VARCHAR(200)**
- `pontos_qr` **INT**
- `ativo` **BOOLEAN**
