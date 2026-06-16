# Financeiro Academia

MVP em Flask para controlar alunos, mensalidades e boletos gerados manualmente.

## Stack

- Python + Flask
- SQLAlchemy ORM
- Flask-Migrate/Alembic
- PostgreSQL
- Bootstrap no front
- ViaCEP no formulario de endereco

## Por que Flask aqui?

Flask atende bem este primeiro momento porque o sistema e pequeno, fica barato de hospedar em um unico servico no Render e nao obriga separar backend e frontend. A arquitetura ja esta dividida por blueprints, servicos e modelos para crescer sem virar um arquivo unico.

Rails tambem seria uma otima escolha se voce quisesse produtividade maxima em CRUDs e conventions fortes. Node.js seria bom se o plano fosse uma API separada com front SPA desde o inicio. Para este escopo, Flask + SQLAlchemy e uma escolha equilibrada.

## Rodar localmente

1. Crie um ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Configure as variaveis:

```bash
cp .env.example .env
```

4. Crie o banco PostgreSQL local `academia_financeiro` ou ajuste `DATABASE_URL`.
5. Rode as migrations:

```bash
flask --app wsgi.py db upgrade
```

6. Suba o servidor:

```bash
flask --app wsgi.py run
```

## Deploy Render + Neon

1. Crie um projeto no Neon e copie a connection string do banco.
2. No Render, crie um Web Service conectado ao repositorio.
3. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `flask --app wsgi.py db upgrade && gunicorn wsgi:app`
4. Adicione as variaveis:
   - `DATABASE_URL`: string do Neon com `sslmode=require`
   - `SECRET_KEY`: uma chave segura
5. No deploy, o Render aplicara as migrations automaticamente antes de iniciar o app.

## Observacoes sobre free tier

Em 16/06/2026, a documentacao do Render informa que web services free podem hibernar apos 15 minutos sem trafego, usam horas mensais limitadas e nao devem ser tratados como producao. O Postgres free do Render expira em 30 dias. Por isso, este projeto esta preparado para usar Neon no banco.

Na pagina de precos do Neon consultada em 16/06/2026, o plano Free informa US$ 0, sem cartao, 100 projetos, 100 CU-hours mensais por projeto e 0,5 GB de storage por projeto.

Fontes:
- https://render.com/docs/free
- https://neon.com/pricing

## Proximos passos naturais

- Autenticacao de usuario.
- Importar alunos da planilha atual.
- Relatorios por mes e inadimplencia.
- Campos especificos da API de boletos do Banco do Brasil.
- Job para consultar baixas/pagamentos automaticamente quando a integracao existir.
