# Backend Project

This project is a backend application built with Python FastAPI, focusing on the implementation of the Builder design pattern.

## Setup Backend

Siga os passos abaixo para rodar a aplicação localmente.

### 1. Configuração de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto e preencha as variáveis necessárias.

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
````

### 3\. Banco de Dados (Docker)

Suba o container do banco de dados (e outros serviços) em segundo plano:

```bash
docker compose up -d
```

### 4\. Rodar a Aplicação

Inicie o servidor de desenvolvimento:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

