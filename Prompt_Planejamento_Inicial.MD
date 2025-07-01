“Você é um engenheiro de software sênior, especialista em back-end, front-end e aplicações de Data Science/IA. Sua missão é ajudar a construir um MVP de um aplicativo web de gestão de finanças pessoais com dashboards analíticos e sugestões inteligentes." 

Siga este escopo:

Contexto:

• Usuário final: pessoa física querendo controlar receitas e despesas.

• Objetivo: registrar transações, categorizar gastos/receitas, gerar insights e recomendações de economia/investimento.

Requisitos funcionais :

• Autenticação e autorização (JWT + refresh tokens).

• CRUD de transações, contas e categorias customizáveis.

• Dashboards com gráficos de gasto por categoria, evolução mensal e heatmap diário.

• Forecast de saldo futuro (usando Prophet ou modelo similar).

• Detecção de anomalias (gastos fora de padrão).

• Sugestões personalizadas (ex.: reduzir gastos em categorias X, alocar percentual em reserva de emergência).


Requisitos não funcionais :

• API RESTful documentada (Swagger/OpenAPI).

• Front-end responsivo e acessível.

• Containerização com Docker e orquestração mínima (docker-compose).

• CI/CD básico (GitHub Actions ou similar).

• Testes automatizados (unitários + integração).

Tech stack sugerida


Back-end :

– Python 3.10+, Django Rest Framework

– PostgreSQL

– Redis (cache e fila opcional para retraining)

– Bibliotecas IA: Prophet, scikit-learn, PyCaret


Front-end :

– React (create-react-app ou Vite)

– TypeScript

– Recharts ou Chart.js para gráficos

– Tailwind CSS ou Material-UI


Infra & DevOps :

– Docker & docker-compose

– GitHub Actions para CI

– Deploy em AWS (Elastic Beanstalk / ECS Fargate) ou DigitalOcean App Platform

Entregáveis iniciais (MVP em 3–4 semanas)

Estrutura de pastas do projeto (backend + frontend).

Configuração de ambiente (Dockerfiles, docker-compose.yml, variáveis de ambiente).

Modelos de domínio no Django (User, Account, Transaction, Category).

Serializers e ViewSets para CRUD básico.

Autenticação JWT (endpoints de login, refresh e logout).

Skeleton do front (login, dashboard em branco, roteamento).

Template de dashboard com mock de dados.


Fluxo de trabalho:

a. Gere a estrutura de pastas e arquivos iniciais.

b. Implemente modelo de dados e endpoints CRUD.

c. Conecte o front-end ao back-end (axios/fetch).

d. Adicione componentes de gráfico com dados dinâmicos.

e. Incorpore o módulo de forecasting e retorne previsões num endpoint.

f. Crie serviço no front para exibir previsões e anomalias.

g. Adicione sugestões de economia com base em regras + modelo de ML.

h. Escreva testes de unidade e integração.