# AGENTS.md - Justice Hack Project Guidelines

## Build/Lint/Test Commands
- **Backend (Python/FastAPI)**: `uvicorn main:app --reload` (dev), `python main.py` (run)
- **Frontend (React/Vite)**: `npm run dev` (dev), `npm run build` (build), `npm run lint` (lint), `npm run preview` (preview)
- **Single test**: No formal testing framework configured - use `python sample_testing.py` for manual testing

## Code Style Guidelines

### Python (Backend)
- **Imports**: Standard library → third-party → local modules
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Types**: Use Pydantic BaseModel for request/response models
- **Error handling**: Let FastAPI handle HTTP errors, use try/catch for external API calls
- **Environment**: Load .env with `load_dotenv()` at module start
- **Constants**: UPPER_SNAKE_CASE for module-level constants

### JavaScript/React (Frontend)
- **Imports**: ES6 modules, group by external → internal
- **Naming**: camelCase for variables/functions, PascalCase for components
- **Styling**: Tailwind CSS classes, no custom CSS unless necessary
- **Linting**: ESLint with React hooks and refresh plugins
- **File structure**: Flat structure in src/, components in same directory

### General
- **Comments**: Minimal, only when code intent isn't clear
- **Security**: Never log or commit API keys/secrets
- **Dependencies**: Check existing usage before adding new libraries