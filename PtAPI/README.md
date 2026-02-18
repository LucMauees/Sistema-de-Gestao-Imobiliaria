

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



##  Como Usar

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

##  Dependências

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

