# Weather Alert

> Projeto desenvolvido como desafio técnico para demonstrar habilidades em Django, Docker e arquitetura de software moderna para a [Tintim](https://tintim.app/).

Weather Alert é um sistema web de monitoramento de temperaturas para localidades específicas. Ele consulta dados climáticos em uma API pública e emite alertas caso a temperatura ultrapasse limites pré-configurados. A aplicação é construída com Python, Django, Django Ninja e Celery, utilizando uma arquitetura moderna e desacoplada, seguindo as boas práticas recomendadas de desenvolvimento web, orquestração de containers com Docker e processamento assíncrono.

## Descrição Técnica

O projeto possui as seguintes funcionalidades:

* Cadastro de localidades a serem monitoradas
* Consulta de dados meteorológicos em tempo real via Open-Meteo API
* Configuração de limites de temperatura para emissão de alertas
* Agendamento periódico de verificações de temperatura com Celery Beat
* Notificação de alertas via integrações externas
* Processamento assíncrono de tarefas com Celery e Redis
* Banco de dados relacional com PostgreSQL
* Interface de API construída com Django Ninja
* Testes automatizados com pytest e pytest-django

## Estrutura de Diretórios

* `weather_alert/` - Código principal do projeto Django

  * `apps/` - Módulos organizados por domínio de negócio

    * `alerts/` - Gerenciamento de alertas de temperatura
    * `location/` - Cadastro e gestão de localidades
    * `temperature/` - Lógica de coleta de temperaturas
  * `integrations/` - Integração com a API Open-Meteo
  * `api/` - Exposição de endpoints REST com Django Ninja
* `tests/` - Suite completa de testes unitários e de integração
* `entrypoint.sh` - Script de inicialização e setup automático do container
* `compose.yml` - Orquestração dos serviços Docker (Postgres, Redis, Celery, Beat, Django)
* `Dockerfile` - Build customizado da aplicação Docker

## Pré-requisitos

* Python 3.12+
* Docker e Docker Compose (opcional para ambiente local com containers)
* Redis e PostgreSQL (local ou via containers)
* Open-Meteo API (pública e gratuita)

## Como Rodar

Abaixo as instruções de execução nos três ambientes de desenvolvimento possíveis.

### 1. Rodar com uv (modo local sem docker)

[Instale](https://docs.astral.sh/uv/getting-started/installation/) o uv.

Instale as dependências:

```
uv sync
```

Ajuste as variáveis de ambiente criando um arquivo `.env` baseado no exemplo abaixo:

```
SECRET_KEY=chave-secreta
PROD=False

# only if PROD is True
POSTGRES_NAME=weather_alert
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/0

N8N_WEBHOOK_URL=http://localhost/webhook
N8N_WEBHOOK_HEADER_KEY=chave-fake
# If you don't have n8n running, you can set this to true to avoid errors
FAKE_WEBHOOK=true
```

Realize as migrações:

```
python manage.py migrate
```

Execute o servidor local:

```
task run
```

Rode o worker Celery:

```
task celery
```

Rode o Celery Beat:

```
task beat
```

Acesse a aplicação em `http://localhost:8000/api/docs/` para interagir com a API REST.

### 2. Rodar com pip (modo tradicional local)

Instale as dependências:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

A sequência de execução é idêntica ao modo uv após a instalação.

### 3. Rodar com docker-compose (modo recomendado)

Este modo executa toda a aplicação completa, incluindo:

* Django Web
* PostgreSQL
* Redis
* Celery Worker
* Celery Beat

Inicie os containers:

```
docker-compose up --build
```

Após o primeiro build, os containers cuidarão automaticamente de:

* Executar as migrações
* Coletar os arquivos estáticos
* Iniciar todos os serviços na ordem correta

Claro, aqui está a seção pura, pronta para você copiar:

---

## Execução sem dependências externas (modo simulado)

Durante o desenvolvimento local e execução de testes, é possível rodar a aplicação em modo simulado, sem necessidade de subir o N8N para envio de notificações.

Para isso, adicione no seu arquivo `.env`:

```
FAKE_WEBHOOK=true
```

Neste modo:

* Nenhuma requisição HTTP será enviada ao N8N.
* As notificações serão simuladas e os alertas serão automaticamente marcados como `notified = true`.
* Todo o restante do fluxo da aplicação continuará funcionando normalmente.

Este recurso facilita a execução da aplicação em ambiente de desenvolvimento, pipelines de CI e também para quem for revisar o projeto localmente.

## Boas práticas aplicadas

Este projeto foi construído seguindo as melhores práticas de desenvolvimento web com Django:

* Separação de módulos de negócio via `apps/`
* Processamento assíncrono desacoplado com Celery
* Agendamento de tarefas periódicas com Django Celery Beat
* Variáveis de ambiente centralizadas via `python-decouple`
* Arquitetura limpa para fácil manutenção e escalabilidade
* Orquestração completa com Docker e Docker Compose
* Integração com API de terceiros usando `httpx` e controle de retries com `stamina`
* Testes automatizados com `pytest` e `pytest-django`
* Uso de ferramentas modernas como `uv` para builds rápidos e eficientes
* Organização completa para facilitar deploy em serviços como Railway e Render

## Testes Automatizados

Execute os testes com:

```
task test
```

Os testes incluem:

* Testes de serviços de alertas
* Testes de tasks do Celery
* Testes de integração com API externa (mockadas com respx)
* Testes de API REST com Django Ninja

Perfeito, agora vamos adicionar a seção final no seu README chamada:

## Exemplos de Consumo da API

### Criar uma Localização

```bash
curl -X POST http://localhost:8000/api/locations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "São Paulo",
    "latitude": -23.55052,
    "longitude": -46.633308
  }'
```

### Listar Localizações

```bash
curl -X GET http://localhost:8000/api/locations/
```

### Obter uma Localização por ID

```bash
curl -X GET http://localhost:8000/api/locations/1/
```

### Deletar uma Localização por ID

```bash
curl -X DELETE http://localhost:8000/api/locations/1/
```

### Criar Configuração de Alerta

```bash
curl -X POST http://localhost:8000/api/alert-configs/ \
  -H "Content-Type: application/json" \
  -d '{
    "location": 1,
    "temperature_threshold": 15,
    "check_interval_minutes": 1
  }'
```

### Listar Configurações de Alerta

```bash
curl -X GET http://localhost:8000/api/alert-configs/
```

### Obter Configuração de Alerta por ID

```bash
curl -X GET http://localhost:8000/api/alert-configs/1/
```

### Atualizar Configuração de Alerta

```bash
curl -X PUT http://localhost:8000/api/alert-configs/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "temperature_threshold": 32.0,
    "check_interval_minutes": 10
  }'
```

### Deletar Configuração de Alerta

```bash
curl -X DELETE http://localhost:8000/api/alert-configs/1/
```

### Listar Alertas

```bash
curl -X GET http://localhost:8000/api/alerts/
```

### Obter Alerta por ID

```bash
curl -X GET http://localhost:8000/api/alerts/1/
```

### Marcar Alerta como Notificado

```bash
curl -X POST http://localhost:8000/api/alerts/notify/1/ \
  -H "N8N_WEBHOOK_KEY: SUA_CHAVE_N8N_AQUI"
```

### Listar Logs de Temperatura

```bash
curl -X GET http://localhost:8000/api/temperature-logs/
```

### Obter Log de Temperatura por ID

```bash
curl -X GET http://localhost:8000/api/temperature-logs/1/
```
