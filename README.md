# Backend Project

This project is a backend application built with Python FastAPI, focusing on the implementation of the Builder design pattern.

## Setup Backend

Siga os passos abaixo para rodar a aplicação localmente.

### 1. Configuração de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto e preencha as variáveis necessárias.

### 2. Setup Firebase

Após gerar a **Service Account** no console do Firebase, você terá um arquivo `.json`.
Coloque esse arquivo **no mesmo diretório onde está o `.env`** do projeto.
```
    /project-root
    ├── .env
    ├── firebase-credentials.json
    ├── app/
```

Após isso, nas variáveis de ambiente, coloque o path exato para o arquivo:
`FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json`

### 3. Ambiente Virtual e Dependências

Crie e ative o ambiente virtual, e depois instale as dependências:

```
# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows:
.\venv\Scripts\activate

# Ativar no Linux/Mac:
source venv/bin/activate

# Instalar requisitos
pip install -r requirements.txt
````

###  4. Banco de Dados (Docker)

Suba o container do banco de dados (e outros serviços) em segundo plano:

```bash
docker compose up -d
```

### 5. Rodar a Aplicação

Inicie o servidor de desenvolvimento:

```
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 6. Migrations do Banco

O schema do banco e versionado com Alembic. Antes de iniciar a aplicacao em um
banco novo ou apos receber novas migrations, execute:

```bash
alembic upgrade head
```

Para criar uma nova migration a partir de alteracoes nos models:

```bash
alembic revision --autogenerate -m "descricao da alteracao"
```

Revise a migration gerada antes de aplica-la em qualquer ambiente compartilhado
ou de producao.

### 7. Rodar ETL

O ETL roda separado do startup da API. Para carregar no banco os arquivos ja
processados em `cnes/` e `data/processed/`, execute:

```bash
python -m app.commands.run_etl
```

Para baixar/processar novos dados antes da carga:

```bash
python -m app.commands.run_etl --new-data
```

Tambem e possivel executar como job pelo Docker Compose:

```bash
docker compose --profile jobs run --rm etl
```

Com novos dados:

```bash
docker compose --profile jobs run --rm etl python -m app.commands.run_etl --new-data
```
