# Folha Municipal - AdaptaBrasil

The **Folha Municipal** is a robust web application developed based on **Clean Architecture** principles. The main objective of this tool is to enable detailed visualization and export of municipal adaptation plans, providing direct support for decision-making regarding public policies and climate resilience.

## 📋 Table of Contents
- [Folha Municipal - AdaptaBrasil](#folha-municipal---adaptabrasil)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗 Project Architecture](#-project-architecture)
  - [🛠 Technologies Used](#-technologies-used)
  - [⚙️ Prerequisites](#️-prerequisites)
  - [🚀 Quick Start (Docker - Recommended)](#-quick-start-docker---recommended)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Configure Environment Variables](#2-configure-environment-variables)
    - [3. Start the Application](#3-start-the-application)
  - [💻 Running the Application](#-running-the-application)
    - [Docker Commands (Recommended)](#docker-commands-recommended)
    - [Common Workflows](#common-workflows)
    - [Starting Locally Without Docker](#starting-locally-without-docker)
      - [Prerequisites](#prerequisites)
      - [Backend Setup](#backend-setup)
      - [Frontend Setup](#frontend-setup)
  - [📂 Directory Structure](#-directory-structure)
  - [PDF Generation Architecture](#pdf-generation-architecture)
  - [🤝 Contributing](#-contributing)
    - [Development Process](#development-process)
    - [Code Guidelines](#code-guidelines)
    - [Backend Standards (Python)](#backend-standards-python)
    - [Frontend Standards (JavaScript)](#frontend-standards-javascript)
  - [📋 Roadmap](#-roadmap)
    - [Version 0.1.X (Current)](#version-01x-current)
    - [Version 0.2.X (Planned)](#version-02x-planned)
  - [📄 License](#-license)
  - [👥 Authors](#-authors)
  - [🔗 Useful Links](#-useful-links)
  - [🚀 Getting Help](#-getting-help)

## ✨ Features
- **Interactive Data Visualization**: Intuitive interface for exploring socioclimatic indicators and municipal data.
- **Automated Reports (PDF Export)**: Advanced PDF generation with multi-page support. Each report page is generated independently and merged seamlessly into a single PDF file, allowing complete design flexibility and configuration per page.
- **Multi-Engine PDF Support**: Choose between Playwright (default), Puppeteer, WeasyPrint, or WkHtmlToPdf for PDF rendering based on your deployment needs.
- **Fast RESTful API**: High-performance backend provided by the FastAPI framework and a PostgreSQL database.
- **Clean Architecture**: Well-organized codebase with clear separation of concerns (Domain, Application, Infrastructure layers).

## 🏗 Project Architecture
The project is strictly modularized into two main parts:

- **Backend (Python)**: Uses **Clean Architecture** with domain-driven design principles:
  - **Domain Layer**: Entities and repository interfaces (no external dependencies)
  - **Application Layer**: Use cases, routers, and dependency injection (FastAPI)
  - **Infrastructure Layer**: Database adapters (SQLAlchemy), PDF services, and external integrations
  - **Core Layer**: Global configurations, environment settings (Pydantic), and application constants

- **Frontend (HTML/CSS/JS)**: A static web application based on Vanilla JavaScript, focusing on simplicity and performance without framework overhead.

## 🛠 Technologies Used
- **Main Language**: Python 3.12+ 🐍
- **API Framework**: FastAPI
- **PDF Processing**: Playwright (default) / Puppeteer / WeasyPrint / WkHtmlToPdf with Jinja2 templates
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript ⚡️
- **Package Management**: Poetry
- **Containerization**: Docker & Docker Compose
- **Rate Limiting**: SlowAPI

## ⚙️ Prerequisites
Ensure you have the following tools installed on your system:
- **Docker** and **Docker Compose** (for the recommended containerized setup)
- **Make** (for using the provided Makefile commands)
- **Git** (for version control)

**For Local Development (Without Docker):**
- Python 3.12 or higher
- Poetry (Python package manager)
- PostgreSQL 15 or higher
- A supported PDF engine (Playwright requires Chromium, others as listed below)

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/AdaptaBrasil/painel_municipal.git
cd painel_municipal
```

### 2. Configure Environment Variables
Copy the provided environment template and update with your settings:
```bash
cp .env.example .env
```

Edit the `.env` file to set your database credentials and preferred PDF engine:
```dotenv
# PDF generation engine: 'playwright' (default), 'puppeteer', 'wkhtmltopdf', or 'weasyprint'
PDF_ENGINE=playwright

# PostgreSQL database connection settings
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=adaptabrasil
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_USE_SSL=False

# Service ports (localhost binding for security)
FRONTEND_SECRET_PORT=5530
BACKEND_SECRET_PORT=8000
DATABASE_SECRET_PORT=5432
```

### 3. Start the Application
Build and start all services with a single command:
```bash
make run
```

This will:
- Build Docker images for backend, frontend, and database
- Start all containers in the background
- Initialize the PostgreSQL database
- Launch the API server with Uvicorn
- Serve the frontend via Nginx

The application will be available at:
- **Frontend**: `http://localhost:5530`
- **Backend API**: `http://localhost:8000`
- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`

## 💻 Running the Application

### Docker Commands (Recommended)

All docker operations are managed via the Makefile. Below are the available commands:

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make build` | Build Docker images without starting containers |
| `make run` | Build and start all containers in the background (full stack) |
| `make start` | Start existing containers without rebuilding images |
| `make stop` | Stop and remove all containers |
| `make restart` | Restart all containers (equivalent to `make stop start`) |
| `make down` | Alias for `make stop` |
| `make logs` | Stream logs from all running containers |
| `make logs-backend` | Stream logs from the backend container only |
| `make logs-frontend` | Stream logs from the frontend container only |
| `make ps` | List all running containers and their status |
| `make shell-backend` | Open an interactive shell inside the backend container |
| `make shell-frontend` | Open an interactive shell inside the frontend container |
| `make shell-db` | Open an interactive shell inside the database container |

### Common Workflows

**Start the full stack:**
```bash
make run
```

**Monitor application logs in real-time:**
```bash
make logs
```

**Check which services are running:**
```bash
make ps
```

**Stop all services:**
```bash
make stop
```

**Access the backend container for debugging:**
```bash
make shell-backend
```

### Starting Locally Without Docker

If you prefer to run the application locally without Docker, follow these steps:

#### Prerequisites
- Python 3.12+
- PostgreSQL 15+ running and accessible
- Poetry installed (`pip install poetry`)
- One of the PDF engines:
  - **Playwright** (recommended): Installed via Poetry
  - **WeasyPrint**: `sudo apt install weasyprint` (Ubuntu/Debian)
  - **WkHtmlToPdf**: `sudo apt install wkhtmltopdf` (Ubuntu/Debian)

#### Backend Setup

1. **Navigate to the backend directory and create a virtual environment:**
   ```bash
   cd backend
   poetry env use 3.12  # or your Python 3.12 installation
   eval $(poetry env activate)
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Create a `.env` file in the backend root** with your database credentials:
   ```bash
   cp ../.env .env.local
   # Edit .env.local with your database connection details
   ```

4. **Run the backend server:**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

#### Frontend Setup

In a new terminal, serve the frontend:
```bash
# From the project root directory
python -m http.server 8080 -d frontend
```

Visit `http://localhost:8080/index.html` in your browser.

**Note:** Ensure that the API endpoints in `frontend/js/app.js` are correctly configured to point to your backend URL (e.g., `http://localhost:8000`).

## 📂 Directory Structure

```text
painel_municipal/
├── .env                          # Environment variables (credentials, ports, settings)
├── .env.example                  # Template for environment configuration
├── docker-compose.yml            # Docker Compose configuration for all services
├── Makefile                       # Convenient commands for Docker operations
├── backend/                       # FastAPI Backend (Clean Architecture)
│   ├── Dockerfile                # Backend container configuration
│   ├── pyproject.toml            # Python dependencies (Poetry)
│   ├── poetry.lock               # Locked dependency versions
│   ├── src/
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── application/          # Application/Presentation Layer
│   │   │   ├── router.py         # API route definitions
│   │   │   └── dependencies.py   # FastAPI dependency injection
│   │   ├── core/                 # Core configurations
│   │   │   ├── config.py         # Pydantic settings (environment variables)
│   │   │   └── constants.py      # Application constants
│   │   ├── domain/               # Domain Layer (Business Logic)
│   │   │   ├── entities.py       # Data models and entities
│   │   │   └── interfaces.py     # Repository and service contracts
│   │   ├── infrastructure/       # Infrastructure Layer
│   │   │   ├── database.py       # Database connection
│   │   │   ├── repository.py     # Data access implementations
│   │   │   └── pdf_service.py    # Multi-engine PDF generation service
│   │   ├── helpers/              # Utility functions
│   │   │   └── common/
│   │   │       └── formatting/
│   │   │           └── number_formatting_processing.py
│   │   └── static/               # Static assets and templates
│   │       └── report/           # PDF report templates
│   │           ├── page_01/      # First report page
│   │           │   ├── report_template.html
│   │           │   ├── css/
│   │           │   │   └── style.css
│   │           │   └── logos/
│   │           └── page_02/      # Second report page
│   │               ├── report_template.html
│   │               ├── css/
│   │               │   └── style.css
│   │               └── logos/
│   └── tests/                    # Unit and integration tests (pytest)
├── frontend/                     # Static Frontend (Vanilla JS)
│   ├── Dockerfile                # Frontend container configuration (Nginx)
│   ├── nginx.conf                # Nginx web server configuration
│   ├── index.html                # Main HTML entry point
│   ├── css/
│   │   └── style.css             # Global stylesheets
│   └── js/
│       └── app.js                # Application logic and API communication
├── README.md                     # This file
├── LICENSE                       # MIT License
└── CODE_OF_CONDUCT.md            # Community guidelines
```

## PDF Generation Architecture

The PDF generation system uses a **multi-page merge strategy**:

1. **Independent Page Definition**: Each report page (e.g., `page_01/`, `page_02/`) has its own:
   - HTML template with custom Jinja2 variables
   - CSS stylesheet for styling
   - Configuration (format, margins, orientation)

2. **Isolated Rendering**: Each page is rendered independently using the selected PDF engine (Playwright by default).

3. **Automatic Merge**: All generated PDFs are merged in memory using PyPDF into a single document.

4. **Single Download**: The final merged PDF is returned to the client for download.

This approach provides maximum flexibility, allowing each page to have completely different designs, styles, and layouts without conflicts.

## 🤝 Contributing

### Development Process

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/painel_municipal.git
   cd painel_municipal
   ```
3. **Create** a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Implement** your changes with tests
5. **Commit** following conventional commits
   ```bash
   git commit -m "feat: add new feature" -m "Description of changes"
   ```
6. **Push** to your branch
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open** a Pull Request to the main repository

### Code Guidelines

- Follow **PEP 8** standard for Python code
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Maintain **test coverage >= 50%** for backend code
- Use **Vanilla JavaScript** without frameworks for frontend (unless explicitly approved)
- Document your changes in commit messages

### Backend Standards (Python)
- Target Python 3.12+
- Use new typing syntax: `T | None`, `list[int]` instead of `Optional[T]`, `List[int]`
- Organize code following Clean Architecture principles
- Use Poetry for dependency management
- Run tests with `pytest` before submitting

### Frontend Standards (JavaScript)
- Write vanilla JavaScript, HTML5, and CSS3
- Avoid frameworks (React, Vue, Angular) unless explicitly requested
- Keep CSS organized in dedicated folders
- Document API calls and their expected responses

## 📋 Roadmap

### Version 0.1.X (Current)
- [x] Backend API with FastAPI and PostgreSQL
- [x] Static Frontend with Vanilla JS/HTML/CSS
- [x] Multi-page PDF export with merge functionality
- [x] Support for Playwright, Puppeteer, WeasyPrint, WkHtmlToPdf PDF engines
- [x] Clean Architecture backend structure
- [x] Docker containerization
- [ ] Unit and Integration Tests suite
- [ ] Comprehensive API documentation
- [ ] CI/CD Pipeline (GitHub Actions)
- [ ] Performance benchmarks and optimizations
- [ ] Security audit and hardening
- [ ] Multi-language support (i18n)

### Version 0.2.X (Planned)
- [ ] Advanced data filtering and analytics
- [ ] Real-time data updates
- [ ] Enhanced PDF export templates
- [ ] User authentication and authorization
- [ ] Audit logging

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Pedro Andrade** - *Coordinator* - [Email](mailto:pedro.andrade@inpe.br) | [GitHub](https://github.com/pedro-andrade-inpe)
- **Mário de Araújo Carvalho** - *Contributor & Developer* - [GitHub](https://github.com/MarioCarvalhoBr)
- **Mauro Assis** - *Contributor* - [GitHub](https://github.com/assismauro)
- **Miguel Gastelumendi** - *Contributor* - [GitHub](https://github.com/miguelGastelumendi)

## 🔗 Useful Links

- **Organization**: [AdaptaBrasil GitHub](https://github.com/AdaptaBrasil/)
- **Repository**: [painel_municipal](https://github.com/AdaptaBrasil/painel_municipal)
- **Issues & Bug Reports**: [Issue Tracker](https://github.com/AdaptaBrasil/painel_municipal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AdaptaBrasil/painel_municipal/discussions)

---

## 🚀 Getting Help

- **Documentation**: Check the inline code comments and docstrings
- **API Reference**: Visit `http://localhost:8000/docs` (Swagger UI) when the application is running
- **Issues**: Search existing GitHub issues or create a new one
- **Discussions**: Join community discussions on GitHub

---

**Developed with ❤️ by the AdaptaBrasil team**