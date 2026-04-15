# GitHub Copilot Instructions (Painel Municipal)

## Language
The default language for all communication, documentation, and user responses in this repository must be **English (en-US)**.

## Backend Architecture and Structure
- The backend uses **Clean Architecture**.
- The code is divided into layers:
  - **Domain**: Entities, abstract business models, and repository/service interfaces (must not have external dependencies on other modules).
  - **Application**: Use cases, action orchestration, and FastAPI router definitions.
  - **Infrastructure**: Database connections (PostgreSQL via SQLAlchemy/asyncpg), implementation of repositories and external services (PDF export using WeasyPrint).
  - **Core**: General configurations, environment variables (Pydantic Settings), and constants.

## Python Code Standards
- The target interpreter version is **Python 3.12+**.
- Always use the new Python typing syntax (`T | None`, `list[int]`, etc.) and declare *type hints* for all parameters and return types of functions/methods.
- The dependency and package manager used is **Poetry**.
- Write unit tests compatible with the `pytest` library and add them to the `tests/` folder.

## Frontend Code Standards
- The frontend is based on **Vanilla JS** (pure JavaScript, HTML5, and CSS3). Avoid proposing libraries like React, Vue, or Angular unless explicitly requested.
- Styles and scripts are maintained in dedicated `css/` and `js/` folders with clear logical separation.
