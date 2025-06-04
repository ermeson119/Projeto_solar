# SolarForms - Sistema de Formulários para Orçamento de Energia Solar

Um sistema completo para gerenciamento de formulários de orçamentos de energia solar, desenvolvido com Python, Flask, PostgreSQL e Docker.

## Características

- Formulário completo para coleta de informações para orçamentos de energia solar
- Sistema de autenticação para administradores
- Painel administrativo para gerenciamento de usuários e formulários
- Exportação de dados para CSV
- Upload e visualização de imagens
- Interface responsiva e amigável

## Requisitos

- Docker
- Docker Compose

## Configuração e Execução

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd Projeto_solar
```

2. Inicie os contêineres com Docker Compose:

```bash
docker-compose up --build
```

3. Acesse o sistema em seu navegador:

```
http://127.0.0.1:8080/
```

## Estrutura do Projeto

```
├── app/
│   ├── static/           # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/        # Templates HTML
│   ├── uploads/          # Diretório para uploads de arquivos
│   ├── routes.py         # Aplicação principal Flask
│   ├── config.py         # Configurações do sistema
│   ├── forms.py          # Definições de formulários WTForms
│   ├── models.py         # Modelos de dados SQLAlchemy
│ 
├── Dockerfile        # Configuração do contêiner da aplicação  
├── docker-compose.yml    # Configuração do Docker Compose
└── README.md             # Documentação
└── requirements.txt  # Dependências Python
```

## Acesso Inicial

Um usuário administrador é criado automaticamente na primeira execução:

- E-mail: admin@admin.com
- Senha: admin123

**IMPORTANTE:** Altere esta senha após o primeiro login.

### Tecnologias Utilizadas

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Banco de Dados:** PostgreSQL
- **Containerização:** Docker, Docker Compose

## Segurança

O sistema implementa as seguintes medidas de segurança:

- Autenticação de usuários com Flask-Login
- Senhas armazenadas com hash seguro
- Controle de acesso baseado em funções
- Proteção contra CSRF em formulários
- Validação de dados no lado do servidor e cliente
