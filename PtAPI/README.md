# 📁 PtAPI - Reorganização da Estrutura

## ✅ O que foi feito

Projeto **100% reorganizado** com arquitetura profissional:

```
PtAPI/
├── config/
│   ├── __init__.py
│   └── db.py              # 🔌 Engine, SessionLocal, Base, get_db
├── models/
│   ├── __init__.py        # Imports centralizados
│   ├── usuario.py         # Usuario (simples, sem herança)
│   ├── cliente.py         # Cliente, ClienteFisica, ClienteJuridica
│   ├── socio.py           # SocioRepresentante
│   └── contratos.py       # Contratos, Imovel, Contratado
├── routes/
│   ├── __init__.py
│   ├── auth.py            # POST /CadastroUsuarios, GET /usuarios
│   └── requisicao.py      # Rotas de requisições (stubs)
├── schemas/
│   ├── __init__.py
│   └── usuario_schema.py  # UsuarioCreate, UsuarioResponse (Pydantic)
├── main.py                # FastAPI app com rotas + lifespan
├── .env                   # DATABASE_URL
└── alembic/              # (já existente)
```

## 🎯 Melhorias Implementadas

### 1. **Separação de Responsabilidades**
- ✅ Config isolado em `config/db.py`
- ✅ Modelos organizados em `models/` (um arquivo por domínio)
- ✅ Schemas Pydantic em `schemas/`
- ✅ Rotas em `routes/` (auth.py, requisicao.py)

### 2. **Segurança**
- ✅ Hash de senha com **Argon2**
- ✅ Validação forte de payload (nome, CPF, senha, email)
- ✅ Email normalizado (minúsculas + índice unique)
- ✅ **Rate limit**: 5 cadastros por minuto
- ✅ Logs seguros (sem expor dados sensíveis)

### 3. **Dados Públicos**
- ✅ Response model `UsuarioResponse` retorna apenas: `id`, `nome`, `email`, `cpf`
- ✅ Senha **NUNCA** é retornada

### 4. **Dependency Injection**
- ✅ `get_db()` em `config/db.py` para injetar sessão
- ✅ Rotas usam `Depends(get_db)` automaticamente

## 🚀 Como Usar

### 1. Criar tabelas
```bash
cd /home/luc/Projetos/Pt/PtAPI
.venv/bin/python -c "from config.db import criar_tabelas; criar_tabelas()"
```

### 2. Rodar servidor
```bash
uvicorn main:app --reload
```

### 3. Testar cadastro
```bash
curl -X POST http://127.0.0.1:8000/auth/CadastroUsuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "senha": "Senha123!",
    "email": "joao@exemplo.com",
    "cpf": "12345678900",
    "rg": "MG123456",
    "data_de_nascimento": "1990-01-15"
  }'
```

### 4. Listar usuários
```bash
curl -X GET http://127.0.0.1:8000/auth/usuarios
```

## 📦 Dependências

Instalar se ainda não tiver:
```bash
pip install passlib slowapi
```

## 📝 Estrutura de Imports

**Antes (confuso):**
```python
from modelo import SessionLocal, Cliente, ClienteFisica  # Tudo junto!
```

**Depois (claro):**
```python
from config.db import SessionLocal, get_db
from models import Cliente, ClienteFisica, Usuario
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from routes import auth_router, requisicao_router
```

## 🗑️ Arquivos Antigos

Os arquivos antigos foram preservados como legacy:
- `main_old.py` - Main original
- `modelo.py` - Definições antigas de modelos
- `autenticacao_rotas.py` - Rotas antigas
- `usuarios.py` - Modelo antigo (duplicado)
- `requisicao_rotas.py` - Rotas antigas

**Você pode deletar esses arquivos quando tiver certeza que tudo funciona.**

## ✨ Próximos Passos

1. ✅ Testar POST /CadastroUsuarios
2. ✅ Testar GET /usuarios
3. ⏳ Implementar autenticação (JWT)
4. ⏳ Rotas de Cliente (CRUD)
5. ⏳ Rotas de Contrato (CRUD)

---

**Projeto reorganizado com sucesso! 🎉**
