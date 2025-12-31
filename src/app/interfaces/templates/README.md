# Templates Directory

This directory contains HTML templates and static assets for the FastAPI application's web interface.

## Structure

```
templates/
├── dashboard.html          # Main dashboard UI template
└── static/                 # Static assets served at /static
    └── js/                 # JavaScript modules
        ├── api/            # API client modules
        │   ├── account/    # Account-related API calls
        │   ├── market/     # Market data API calls
        │   └── trading/    # Trading API calls
        ├── dom/            # DOM manipulation utilities
        ├── pages/          # Page-specific scripts
        ├── shared/         # Shared utilities (http, errors, time)
        └── state/          # State management (store, selectors)
```

## Usage

Templates are loaded via Jinja2Templates in `src/app/interfaces/http/status.py`:

```python
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="src/app/interfaces/templates")
```

Static assets are served via FastAPI StaticFiles in `main.py`:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="src/app/interfaces/templates/static"), name="static")
```

## Routes

- `GET /` - Dashboard home page
- `GET /dashboard` - Dashboard page
- `GET /static/*` - Static assets (JS, CSS, images)

## Container Deployment

The Dockerfile automatically copies this directory as part of `COPY src/ ./src/`, ensuring all templates and static assets are available in the container image.

This location under `src/app/interfaces/` follows clean architecture principles, placing UI templates in the interface layer where they belong.
