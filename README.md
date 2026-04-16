# Municipal Dashboard - AdaptaBrasil

The **Municipal Dashboard** is a robust web application developed based on **Clean Architecture** principles. The main objective of this tool is to enable detailed visualization and export of municipal adaptation plans, providing direct support for decision-making regarding public policies and climate resilience.

## 📋 Table of Contents
- [Municipal Dashboard - AdaptaBrasil](#municipal-dashboard---adaptabrasil)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗 Project Architecture](#-project-architecture)
  - [🛠 Technologies Used](#-technologies-used)
  - [⚙️ Prerequisites](#️-prerequisites)
  - [🚀 Installation \& Setup](#-installation--setup)
  - [💻 Running the Application](#-running-the-application)
    - [Starting the Backend Server (API)](#starting-the-backend-server-api)
    - [Starting the Frontend](#starting-the-frontend)
  - [📂 Directory Structure](#-directory-structure)
  - [🤝 Contributing](#-contributing)
    - [Development Process](#development-process)
    - [Code Guidelines](#code-guidelines)
  - [📋 Roadmap](#-roadmap)
    - [Version 0.1.X (Planned)](#version-01x-planned)
  - [📄 License](#-license)
  - [👥 Authors](#-authors)
  - [🔗 Useful Links](#-useful-links)

## ✨ Features
- **Interactive Data Visualization**: Intuitive interface for exploring socioclimatic indicators and municipal data.
- **Automated Reports (PDF Export)**: Native and parameterized generation of adaptation plan PDFs using HTML templates, with support for both WeasyPrint and Wkhtmltopdf services.
- **Fast RESTful API**: High-performance backend provided by the FastAPI framework and a relational database.

## 🏗 Project Architecture
The project is strictly modularized into two main parts:
- **Backend (Python)**: Uses **Clean Architecture** for complete dependency control, separating abstract business rules (Domain) from web integrations (Application/FastAPI) and concrete persistence technologies (Infrastructure).
- **Frontend (HTML/CSS/JS)**: A static web application based on Vanilla JS, aiming for simplicity, speed, and ease of deployment.

## 🛠 Technologies Used
- **Main Language**: Python 3.12+ 🐍
- **API Framework**: FastAPI
- **PDF Processing**: WeasyPrint or Wkhtmltopdf / Jinja2 (for template rendering)
- **Persistence**: PostgreSQL / SQLAlchemy
- **Graphical Interface**: HTML5, CSS3, Vanilla JavaScript ⚡️
- **Dependency Orchestration**: Poetry

## ⚙️ Prerequisites
Ensure you have the following tools installed and configured in your development environment:
- **Python 3.12** or higher
- **[Poetry](https://python-poetry.org/)** for package management and backend environment isolation
- **PostgreSQL** database running locally (or via a container)
- **PDF Generation Engine dependencies** (Install one depending on the `PDF_ENGINE` you choose to use):
  - **WeasyPrint**:
    - **GNU/Linux (Ubuntu/Debian):** `sudo apt install weasyprint`
    - **Windows:** Download the installer from the [official website](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation). To use WeasyPrint on Windows, the easiest way is to use the [executable ](https://github.com/Kozea/WeasyPrint/releases) of the latest release.


  - **Wkhtmltopdf**:
    - **GNU/Linux (Ubuntu/Debian):** `sudo apt install python3-dev wkhtmltopdf`
    - **Windows:** Download the installer from the [official website](https://wkhtmltopdf.org/downloads.html) or via Chocolatey: `choco install -y wkhtmltopdf`
  
  - **Recommended**: Use `wkhtmltopdf` for better performance and compatibility, especially on Windows. Use `WeasyPrint` if you prefer a pure Python solution or have specific rendering needs that it handles better, especially on Linux.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AdaptaBrasil/painel_municipal.git
   cd painel_municipal
   ```

2. **Virtual Environment:**
   Create and activate a local virtual environment to isolate the project's dependencies:
   ```bash
      # 1.2 Create and activate a virtual environment (optional but recommended)
      python -m venv .venv

      # 1.3 Activate the virtual environment
      source .venv/bin/activate # On Linux/MacOS
      .venv\Scripts\activate # On Windows

      # 2. Install Poetry (if needed)
      pip install poetry

      # 3. Install dependencies
      poetry install

      # 4. Activate the virtual environment
      eval $(poetry env activate)
   ```

3. **Environment Variables:**
   You should also configure the `PDF_ENGINE` variable in your `.env` file to select the PDF generation tool (`weasyprint` or `wkhtmltopdf`):
   ```dotenv
   # PDF generation engine to use: 'wkhtmltopdf' or 'weasyprint'
   PDF_ENGINE="wkhtmltopdf"
   ```
   In the project root (or inside the backend folder), create a file based on the existing template to set up your database credentials and other sensitive parameters.
   ```bash
   cp .env.example .env
   ```

4. **Backend Installation:**
   Navigate to the backend folder and instruct Poetry to install all Python dependencies. With the virtual environment activated, Poetry will use it automatically.
   ```bash
   cd backend
   poetry install
   ```

## 💻 Running the Application

### Starting the Backend Server (API)
Activate the project's virtual environment and invoke the application entry point directly (Uvicorn):
```bash
cd backend
poetry shell
uvicorn src.main:app --reload
```
This will launch the API, making it accessible at `http://localhost:8000`. The interactive REST route documentation (Swagger UI) can be tested at `http://localhost:8000/docs`.

### Starting the Frontend
Given the static nature of the provided web components, the interface can be run simply by serving the frontend folder:
```bash
# Assuming you are in the root folder of the project:
python -m http.server 8080 -d frontend
```
Through your browser, visit `http://localhost:8080/index.html` to load the portal's main page. Make sure in the `./frontend/js/app.js` file that the required endpoints properly hit port `8000` exposed by your backend.

## 📂 Directory Structure
```text
.
├── backend/                  # FastAPI Application using Clean Architecture
│   ├── src/
│   │   ├── application/      # Use Cases and Routing/Injection (FastAPI)
│   │   ├── core/             # Global configurations, Settings (Pydantic), and Constants
│   │   ├── domain/           # Vital entities and high-level interfaces (DB Contracts)
│   │   ├── infrastructure/   # DB Adapter (SQLAlchemy), PDF Services (WeasyPrint)
│   │   └── static/           # Fixed rendering templates (under \`report/report_template.html\`)
│   └── tests/                # Automated tests using pytest
└── frontend/                 # Visual interface components (Browser HTML+CSS+JS)
    ├── css/
    ├── js/
    └── index.html
```

## 🤝 Contributing

### Development Process

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a branch for your feature (`git checkout -b feature/new-feature`)
4. **Implement** your changes with tests
5. **Run** tests (`make test`)
6. **Commit** following the [guidelines](https://github.com/AdaptaBrasil/painel_municipal/blob/main/CODE_OF_CONDUCT.md)
7. **Push** to your branch (`git push origin feature/new-feature`)
8. **Open** a Pull Request

### Code Guidelines

- Follow PEP 8 standard
- Maintain test coverage >= 50%
- Use type hints
- Document public functions
- Run `make black` before commit

## 📋 Roadmap

### Version 0.1.X (Planned)
- [X] Backend API with FastAPI and PostgreSQL
- [X] Static Frontend with HTML/CSS/JS
- [X] PDF Export with WeasyPrint
- [ ] Unit and Integration Tests
- [ ] Detailed documentation (README, Wiki, etc.)
- [ ] CI/CD Configuration (GitHub Actions)
- [ ] Support for multiple municipal plans
- [ ] Performance and security optimizations

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/AdaptaBrasil/painel_municipal/blob/main/LICENSE) file for details.

## 👥 Authors
- **Pedro Andrade** - *Coordinator* - [MAIL](mailto:pedro.andrade@inpe.br) and [GitHub](https://www.github.com/pedro-andrade-inpe)
- **Mário de Araújo Carvalho** - *Contributor and Developer* - [GitHub](https://github.com/MarioCarvalhoBr)
- **Mauro Assis** - *Contributor* - [GitHub](https://www.github.com/assismauro)
- **Miguel Gastelumendi** - *Contributor* - [GitHub](https://github.com/miguelGastelumendi)

## 🔗 Useful Links

- **Homepage**: [AdaptaBrasil GitHub](https://github.com/AdaptaBrasil/)
- **Documentation**: [Docs](https://github.com/AdaptaBrasil/painel_municipal/tree/main/docs)
- **Issues**: [Bug Tracker](https://github.com/AdaptaBrasil/painel_municipal/issues)
- **Changelog**: [Version History](https://github.com/AdaptaBrasil/painel_municipal/blob/main/CHANGELOG.md) 

**Developed with ❤️ by the AdaptaBrasil team**