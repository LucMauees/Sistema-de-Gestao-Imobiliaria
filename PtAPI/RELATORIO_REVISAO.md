# 🔒 Relatório de Revisão Completa - PtAPI

**Data da Revisão:** 2024  
**Revisor:** Análise Automatizada de Código  
**Foco:** Segurança e Organização

---

## 📋 Sumário Executivo

Este relatório apresenta uma análise detalhada do código da API PtAPI, identificando **problemas críticos de segurança**, questões de organização e recomendações para melhorias. Foram identificados **8 problemas críticos**, **12 problemas de segurança médios** e **15 questões de organização**.

---

## 🚨 PROBLEMAS CRÍTICOS DE SEGURANÇA

### 1. **CREDENCIAIS HARDCODED NO CÓDIGO** ⚠️ CRÍTICO

**Localização:** `alembic.ini:89`

```ini
sqlalchemy.url = postgresql+psycopg2://postgres:admin@123@localhost:5432/teste
```

**Problema:**
- Credenciais do banco de dados (usuário: `postgres`, senha: `admin@123`) estão expostas em texto plano no arquivo de configuração
- Este arquivo pode ser versionado no Git, expondo credenciais publicamente
- Qualquer pessoa com acesso ao repositório pode ver as credenciais

**Impacto:** 
- Acesso não autorizado ao banco de dados
- Comprometimento de todos os dados
- Violação de LGPD/GDPR

**Solução:**
1. Remover credenciais do `alembic.ini`
2. Usar variáveis de ambiente no `alembic/env.py`:
```python
# alembic/env.py
import os
from dotenv import load_dotenv

load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
```

3. Adicionar `alembic.ini` ao `.gitignore` ou usar template sem credenciais
4. **URGENTE:** Alterar senha do banco de dados imediatamente

---

### 2. **FALTA DE AUTENTICAÇÃO E AUTORIZAÇÃO** ⚠️ CRÍTICO

**Localização:** Todas as rotas em `routes/`

**Problema:**
- Nenhuma rota possui autenticação (JWT, OAuth, etc.)
- Qualquer pessoa pode acessar todos os endpoints
- Endpoint `/auth/usuarios` lista todos os usuários sem autenticação
- Rotas de imóveis, contratos e requisições são totalmente públicas

**Impacto:**
- Acesso não autorizado a dados sensíveis (CPF, emails, endereços)
- Modificação/criação de dados por usuários não autenticados
- Violação de privacidade e LGPD

**Solução:**
1. Implementar autenticação JWT:
```python
# routes/auth.py
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def criar_token(usuario_id: int):
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": str(usuario_id), "exp": expire}, SECRET_KEY, ALGORITHM)

@auth_router.post("/login")
def login(email: str, senha: str, db=Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not pwd_context.verify(senha, usuario.senha):
        raise HTTPException(401, "Credenciais inválidas")
    return {"access_token": criar_token(usuario.id)}
```

2. Criar dependency para proteger rotas:
```python
# config/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def obter_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, ALGORITHM)
        usuario_id = int(payload.get("sub"))
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()
    except:
        raise HTTPException(401, "Token inválido")
```

3. Aplicar em todas as rotas:
```python
@imovel_router.get("/{imovel_id}")
def obter_imovel(
    imovel_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    # ...
```

---

### 3. **SENHAS EM TEXTO PLANO EM MODELOS** ⚠️ CRÍTICO

**Localização:** 
- `models/cliente.py:16` - Cliente.senha
- `models/contratos.py:20` - Contratado.senha

**Problema:**
- Modelos `Cliente` e `Contratado` armazenam senhas, mas não há hash aplicado
- Senhas podem ser armazenadas em texto plano no banco de dados
- Não há rotas de criação para esses modelos que apliquem hash

**Impacto:**
- Senhas expostas no banco de dados
- Se o banco for comprometido, todas as senhas estarão acessíveis

**Solução:**
1. Aplicar hash de senha ao criar Cliente/Contratado (usar mesma função `hash_senha` de `routes/auth.py`)
2. Criar schemas e rotas com validação e hash:
```python
# routes/cliente.py
@router.post("/clientes", status_code=201)
def criar_cliente(payload: ClienteCreate, db=Depends(get_db)):
    senha_hash = hash_senha(payload.senha)
    cliente = ClienteFisica(
        nome=payload.nome,
        senha=senha_hash,  # Hash aplicado
        # ...
    )
```

---

### 4. **RATE LIMIT DESABILITADO** ⚠️ CRÍTICO

**Localização:**
- `main.py:24,32` - Rate limiter comentado
- `routes/auth.py:37` - Decorator `@limiter.limit` comentado

**Problema:**
- Rate limiting está implementado mas desabilitado
- API vulnerável a ataques de força bruta e DDoS
- Cadastro de usuários pode ser abusado

**Impacto:**
- Ataques de força bruta em login
- Spam de cadastros
- Sobrecarga do servidor

**Solução:**
1. Habilitar rate limit no `main.py`:
```python
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: {"detail": "Rate limit exceeded"})
```

2. Habilitar em `routes/auth.py`:
```python
@auth_router.post("/CadastroUsuarios", status_code=201)
@limiter.limit("5/minute")
def criar_usuario(request: Request, payload: UsuarioCreate, db=Depends(get_db)):
    # ...
```

---

### 5. **EXPOSIÇÃO DE DADOS SENSÍVEIS** ⚠️ CRÍTICO

**Localização:** `routes/auth.py:101-117`

**Problema:**
- Endpoint `GET /auth/usuarios` retorna CPF de todos os usuários sem autenticação
- CPF é dado pessoal sensível (LGPD)
- Não há paginação, retornando todos os registros

**Impacto:**
- Violação de privacidade
- Violação de LGPD
- Possível uso indevido de CPFs

**Solução:**
1. Adicionar autenticação obrigatória
2. Adicionar paginação:
```python
from fastapi import Query

@auth_router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return [UsuarioResponse.from_orm(u) for u in usuarios]
```

3. Considerar mascarar CPF na resposta (apenas últimos 3 dígitos)

---

### 6. **FALTA DE VALIDAÇÃO DE CPF/CNPJ** ⚠️ CRÍTICO

**Localização:**
- `schemas/usuario_schema.py:21-25` - Valida apenas formato, não dígito verificador
- `models/cliente.py` - Não há validação de CNPJ

**Problema:**
- CPF é validado apenas por formato (11 dígitos), não por algoritmo de validação
- CNPJ não possui validação alguma
- Dados inválidos podem ser cadastrados

**Impacto:**
- Dados incorretos no banco
- Problemas com integrações externas
- Possível fraude

**Solução:**
1. Implementar validação de CPF:
```python
def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    # Algoritmo de validação de CPF
    # ...
```

2. Usar biblioteca: `pip install validate-docbr` ou `cpf-cnpj-validator`

---

### 7. **FALTA DE CORS CONFIGURADO** ⚠️ CRÍTICO

**Localização:** `main.py`

**Problema:**
- CORS não está configurado
- API pode ser acessada de qualquer origem (ou bloqueada completamente)
- Risco de ataques CSRF

**Solução:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),  # Lista de origens permitidas
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

### 8. **FALTA DE TRATAMENTO DE ERROS CONSISTENTE** ⚠️ CRÍTICO

**Localização:** Todas as rotas

**Problema:**
- Tratamento de erros inconsistente
- Mensagens de erro podem expor informações do sistema
- Stack traces podem ser expostos em produção

**Solução:**
1. Criar handler global de exceções:
```python
# main.py
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )
```

2. Não expor detalhes técnicos em produção

---

## ⚠️ PROBLEMAS DE SEGURANÇA (MÉDIO)

### 9. **FALTA DE VALIDAÇÃO DE ENTRADA EM ROTAS DE IMÓVEIS**

**Localização:** `routes/imovel.py`

**Problema:**
- Rotas não validam se `cliente_id` existe
- Não valida formato de CEP
- Não valida se usuário tem permissão para acessar o imóvel

**Solução:**
- Adicionar validação de existência de cliente
- Validar CEP com regex
- Implementar autorização (usuário só acessa seus próprios imóveis)

---

### 10. **LOGS PODEM EXPOR INFORMAÇÕES SENSÍVEIS**

**Localização:** `routes/auth.py:96`

**Problema:**
- `logger.exception()` pode logar dados sensíveis em alguns casos
- Logs não são sanitizados

**Solução:**
- Garantir que logs nunca contenham senhas, tokens ou dados pessoais completos
- Usar função `log_cadastro` em todos os lugares

---

### 11. **FALTA DE HTTPS/SSL**

**Problema:**
- API não força uso de HTTPS
- Dados trafegam em texto plano

**Solução:**
- Configurar HTTPS no servidor (nginx, traefik, etc.)
- Adicionar redirect HTTP -> HTTPS
- Usar certificados SSL válidos

---

### 12. **FALTA DE VALIDAÇÃO DE TAMANHO DE DADOS**

**Localização:** Schemas e modelos

**Problema:**
- Não há limites máximos explícitos em muitos campos
- Possível ataque de DoS com dados muito grandes

**Solução:**
- Adicionar `max_length` em todos os campos String
- Validar tamanho de uploads

---

### 13. **FALTA DE TIMEOUT EM QUERIES**

**Localização:** `config/db.py`

**Problema:**
- Queries podem travar indefinidamente
- Sem timeout configurado

**Solução:**
```python
db = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10}
)
```

---

### 14. **FALTA DE BACKUP E RECUPERAÇÃO**

**Problema:**
- Não há evidência de estratégia de backup
- Sem plano de recuperação de desastres

**Solução:**
- Implementar backups automáticos
- Documentar procedimento de recuperação

---

### 15. **FALTA DE MONITORAMENTO E ALERTAS**

**Problema:**
- Sem monitoramento de segurança
- Sem alertas para atividades suspeitas

**Solução:**
- Implementar logging estruturado
- Adicionar monitoramento (Sentry, DataDog, etc.)
- Alertas para múltiplas tentativas de login falhadas

---

### 16. **FALTA DE VALIDAÇÃO DE EMAIL**

**Localização:** `schemas/usuario_schema.py`

**Problema:**
- Email é validado apenas por formato (EmailStr)
- Não verifica se domínio existe
- Não verifica se email é válido

**Solução:**
- Considerar validação de domínio
- Implementar verificação por email (envio de código)

---

### 17. **FALTA DE ROTA DE LOGIN**

**Problema:**
- Existe cadastro mas não existe login
- Não há como autenticar usuários

**Solução:**
- Implementar rota `/auth/login` com JWT

---

### 18. **FALTA DE ROTA DE LOGOUT**

**Problema:**
- Sem mecanismo de logout
- Tokens JWT não podem ser invalidados

**Solução:**
- Implementar blacklist de tokens
- Ou usar refresh tokens com rotação

---

### 19. **FALTA DE RATE LIMIT EM OUTRAS ROTAS**

**Problema:**
- Rate limit só está (desabilitado) em cadastro
- Outras rotas vulneráveis a abuso

**Solução:**
- Aplicar rate limit em todas as rotas públicas
- Limites diferentes por tipo de rota

---

### 20. **FALTA DE VALIDAÇÃO DE PERMISSÕES**

**Problema:**
- Não há sistema de roles/permissões
- Todos os usuários teriam mesmo nível de acesso

**Solução:**
- Implementar sistema de roles (admin, user, etc.)
- Verificar permissões em rotas sensíveis

---

## 📁 PROBLEMAS DE ORGANIZAÇÃO

### 21. **ARQUIVO LEGACY DUPLICADO**

**Localização:** `modelo.py`

**Problema:**
- Arquivo `modelo.py` contém modelos duplicados
- Pode causar confusão e conflitos
- README menciona que pode ser deletado

**Solução:**
- **DELETAR** `modelo.py` após confirmar que não é usado
- Verificar imports antes de deletar

---

### 22. **FALTA DE ARQUIVO .gitignore**

**Problema:**
- Não há `.gitignore` visível
- Arquivos sensíveis podem ser versionados

**Solução:**
Criar `.gitignore`:
```
.env
.env.local
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.venv/
venv/
*.db
*.sqlite
.DS_Store
alembic.ini  # Se contiver credenciais
```

---

### 23. **FALTA DE REQUIREMENTS.TXT**

**Problema:**
- Não há arquivo de dependências
- Dificulta reprodução do ambiente

**Solução:**
Criar `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
passlib[argon2]==1.7.4
slowapi==0.1.9
pydantic[email]==2.5.0
alembic==1.12.1
sqlalchemy-utils==0.41.1
python-jose[cryptography]==3.3.0
reportlab==4.0.7
```

---

### 24. **FALTA DE VALIDAÇÃO CONSISTENTE**

**Problema:**
- Validação apenas em `usuario_schema.py`
- Outros schemas não têm validação robusta

**Solução:**
- Adicionar validators em todos os schemas
- Validar CEP, telefone, etc.

---

### 25. **FALTA DE PAGINAÇÃO**

**Problema:**
- Listagens retornam todos os registros
- Pode causar problemas de performance

**Solução:**
- Implementar paginação em todas as listagens
- Usar `skip` e `limit` padrão

---

### 26. **FALTA DE TRATAMENTO DE TRANSACÇÕES**

**Problema:**
- Algumas operações podem precisar de transações
- Não há tratamento explícito de rollback

**Solução:**
- Usar context managers para transações
- Garantir atomicidade de operações complexas

---

### 27. **FALTA DE DOCUMENTAÇÃO DE API**

**Problema:**
- FastAPI gera docs automaticamente, mas podem estar incompletas
- Falta documentação de exemplos

**Solução:**
- Adicionar exemplos nas rotas
- Documentar códigos de erro
- Adicionar descrições detalhadas

---

### 28. **FALTA DE TESTES**

**Problema:**
- Não há testes unitários ou de integração
- Mudanças podem quebrar funcionalidades

**Solução:**
- Implementar testes com pytest
- Testes de segurança (SQL injection, XSS, etc.)
- Testes de integração das rotas

---

### 29. **FALTA DE VALIDAÇÃO DE TIPOS**

**Problema:**
- Alguns tipos podem ser mais específicos
- Uso de `str` onde poderia ser `EmailStr`, etc.

**Solução:**
- Usar tipos mais específicos do Pydantic
- Adicionar type hints em todas as funções

---

### 30. **ROTAS DE REQUISIÇÃO SÃO STUBS**

**Localização:** `routes/requisicao.py`

**Problema:**
- Rotas não implementadas
- Retornam apenas mensagens mock

**Solução:**
- Implementar funcionalidades ou remover rotas
- Não expor rotas não funcionais

---

### 31. **FALTA DE CONFIGURAÇÃO DE LOGGING**

**Problema:**
- Logging não está configurado globalmente
- Apenas logger local em `auth.py`

**Solução:**
- Configurar logging no `main.py`
- Níveis diferentes para dev/prod
- Formato estruturado (JSON)

---

### 32. **FALTA DE HEALTH CHECK COMPLETO**

**Localização:** `main.py:41-44`

**Problema:**
- Health check muito simples
- Não verifica conexão com banco

**Solução:**
```python
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except:
        return {"status": "unhealthy", "database": "disconnected"}
```

---

### 33. **FALTA DE VALIDAÇÃO DE ESTADO**

**Problema:**
- Não valida se operações são permitidas no estado atual
- Ex: deletar imóvel com contratos ativos

**Solução:**
- Adicionar validações de regras de negócio
- Verificar dependências antes de operações destrutivas

---

### 34. **FALTA DE ÍNDICES NO BANCO**

**Problema:**
- Alguns campos usados em queries podem não ter índices
- Performance pode ser afetada

**Solução:**
- Revisar queries frequentes
- Adicionar índices onde necessário
- Usar migrations do Alembic

---

### 35. **FALTA DE VERSIONAMENTO DE API**

**Problema:**
- API não tem versionamento
- Mudanças podem quebrar clientes

**Solução:**
- Adicionar versionamento: `/api/v1/...`
- Manter compatibilidade com versões antigas

---

## ✅ PONTOS POSITIVOS

1. ✅ **Estrutura organizada** - Separação clara de models, routes, schemas
2. ✅ **Hash de senha** - Uso de Argon2 para hash de senhas (em Usuario)
3. ✅ **Validação Pydantic** - Uso de schemas para validação
4. ✅ **Dependency Injection** - Uso correto de `Depends(get_db)`
5. ✅ **Response models** - Separação entre dados de entrada e saída
6. ✅ **Email normalizado** - Email convertido para minúsculas
7. ✅ **Validação de senha forte** - Requisitos de complexidade
8. ✅ **Logs sanitizados** - Função `log_cadastro` não expõe dados sensíveis

---

## 🎯 PRIORIDADES DE CORREÇÃO

### 🔴 URGENTE (Fazer Imediatamente)
1. **Remover credenciais do `alembic.ini`** e usar variáveis de ambiente
2. **Alterar senha do banco de dados**
3. **Implementar autenticação JWT** em todas as rotas
4. **Habilitar rate limiting**
5. **Aplicar hash de senha** em Cliente e Contratado

### 🟡 IMPORTANTE (Próximos Passos)
6. Implementar validação de CPF/CNPJ
7. Adicionar CORS configurado
8. Implementar paginação
9. Adicionar tratamento de erros global
10. Criar `.gitignore` e `requirements.txt`

### 🟢 MELHORIAS (Futuro)
11. Implementar testes
12. Adicionar monitoramento
13. Documentação completa
14. Sistema de permissões
15. Versionamento de API

---

## 📊 RESUMO ESTATÍSTICO

- **Problemas Críticos:** 8
- **Problemas Médios:** 12
- **Problemas de Organização:** 15
- **Pontos Positivos:** 8
- **Total de Itens:** 43

---

## 📝 CONCLUSÃO

O código apresenta uma **base sólida de organização**, mas possui **vulnerabilidades críticas de segurança** que devem ser corrigidas **imediatamente** antes de qualquer deploy em produção. As principais preocupações são:

1. **Credenciais expostas** no código
2. **Falta completa de autenticação**
3. **Senhas sem hash** em alguns modelos
4. **Rate limiting desabilitado**

Recomenda-se seguir a ordem de prioridades acima e realizar uma nova revisão após as correções críticas.

---

**Fim do Relatório**
