# Backend Project - DomiData

Este projeto é uma aplicação backend construída com Python FastAPI, focada na implementação do padrão de design Builder para análise de dados de saúde.

## 🚀 Quick Start com Docker (Recomendado)

A forma mais rápida de rodar a API junto com o banco de dados:

```bash
# Subir todos os serviços (API + PostgreSQL)
docker compose up -d

# Ver logs em tempo real
docker compose logs -f

# Parar todos os serviços
docker compose down
```

A API estará disponível em: **http://localhost:8000**

O banco de dados PostgreSQL estará disponível em: **localhost:5432**

### Variáveis de Ambiente

O arquivo `.env` já está configurado. As principais variáveis são:

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `POSTGRES_USER` | Usuário do PostgreSQL | domidata |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | domidata |
| `POSTGRES_DB` | Nome do banco | domidata |
| `POPULATE_DB` | Popular banco com dados iniciais | true |
| `FRONTEND_URL` | URL do frontend para CORS | http://localhost:5173 |

---

## 🛠️ Setup Local (Desenvolvimento)

Siga os passos abaixo para rodar a aplicação localmente sem Docker.

### 1. Configuração de Ambiente (.env)
O arquivo `.env` já está configurado na raiz do projeto.

### 2. Ambiente Virtual e Dependências

Crie e ative o ambiente virtual, e depois instale as dependências:

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows:
.\venv\Scripts\activate

# Ativar no Linux/Mac:
source venv/bin/activate

# Instalar requisitos
pip install -r requirements.txt
```

### 3. Banco de Dados (Docker)

Suba apenas o container do banco de dados:

```bash
docker compose up db -d
```

### 4. Rodar a Aplicação

Inicie o servidor de desenvolvimento:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/heatmap` | Gera dados de heatmap com parâmetros estruturados |
| POST | `/heatmap/natural-search` | Busca natural usando IA para interpretar a query |

### Exemplo de uso

```bash
# Teste de saúde da API
curl http://localhost:8000/docs

# Exemplo de requisição para heatmap/natural-search
curl -X POST http://localhost:8000/heatmap/natural-search \
  -H "Content-Type: application/json" \
  -d '{"query": "casos de dengue em João Pessoa"}'
```

---

## 🐳 Comandos Docker Úteis

```bash
# Reconstruir a imagem após mudanças no código
docker compose up -d --build

# Ver status dos containers
docker compose ps

# Acessar logs de um serviço específico
docker compose logs api -f
docker compose logs db -f

# Reiniciar apenas a API
docker compose restart api

# Limpar tudo (incluindo volumes/dados)
docker compose down -v
```

