# GitHub Copilot Instructions — IBMS

## Project Overview

IBMS (Integrated Business Management System) is a Django 5.2 corporate application for the Department of Biodiversity, Conservation and Attractions (DBCA), Western Australia. It manages financial data, GL pivot downloads, IBM code updates, data amendments, and service/finance metrics across DBCA regions.

The project has two Django apps:

- **`ibms`** — core business logic: GL pivot data, IBM data, service priorities, code updates, data amendments, Excel upload/download
- **`sfm`** — Service and Finance Metrics: cost centres, financial years, quarters, SFM metrics, measurement values

Project configuration lives in **`ibms_project/`** (settings, urls, middleware, signals, context processors).

## Tech Stack

- **Python 3.13+**, **Django 5.2**
- **PostgreSQL** via `psycopg` v3 with connection pooling (`dj-database-url`)
- **Package management**: `uv` (never use pip directly; use `uv add`/`uv sync`)
- **Forms**: `django-crispy-forms` + `crispy-bootstrap5`; all forms extend `HelperForm` or `FinancialYearFilterForm`
- **Branding/templates**: `webtemplate-dbca` base templates
- **Static files**: `whitenoise` for serving and compression
- **Model versioning**: `django-reversion` (`VersionAdmin`, `RevisionMixin`)
- **Excel**: `openpyxl` for new code; `xlrd`/`xlwt`/`xlutils` are deprecated and should not be used in new work
- **Authentication**: Django auth + DBCA SSO via `dbca_utils.middleware.SSOLoginMiddleware`
- **Linting**: `ruff` (line length 140); `djlint` for templates
- **Testing**: Django `TestCase`, `mixer` for model instances, `Faker` for fake data

## Conventions

### Models

- Field names use **camelCase** (e.g., `costCentre`, `financialYear`, `ibmIdentifier`, `budgetArea`) — this is intentional, not a mistake
- Use `DEFAULT_AUTO_FIELD = "django.db.models.AutoField"` (integer PKs, not BigAutoField)
- Audit fields (`modifier`, `modified`) use `get_current_user()` from `ibms_project.middleware`
- Use `on_delete=models.PROTECT` unless there is a specific reason to cascade
- Add `db_index=True` to fields used in filters or lookups

### Views

- All views require authentication — extend `LoginRequiredMixin` as the first base class
- Use class-based views: `TemplateView`, `FormView`, `ListView`, `CreateView`, `UpdateView`
- Set `http_method_names` explicitly on every view
- Superuser-only operations: check `request.user.is_superuser` in `dispatch()`; redirect with `messages.error()` if not authorised
- Add `page_title` and `title` to context in `get_context_data()` following the pattern `f"{settings.SITE_ACRONYM} | <Page>"`

### Forms

- Forms inherit from `HelperForm` (crispy `FormHelper` with Bootstrap 5 horizontal layout) or `FinancialYearFilterForm`
- Use `crispy_forms.layout` (`Layout`, `Div`, `Submit`, `HTML`) to define form layouts
- AJAX endpoints that return JSON for select lists use `IbmsModelFieldJSON` view pattern

### URLs

- Use `app_name` namespacing (`ibms:` and `sfm:`)
- Named URLs follow snake_case (e.g., `download_enhanced`, `data_amendment_list`)
- AJAX endpoints live under `ajax/` prefix

### Templates

- Extend `webtemplate_dbca` base or project base template `base_ibms.html`
- Use `{% load crispy_forms_tags %}` for form rendering
- Template files are in `<app>/templates/<app>/`; project-wide templates in `ibms_project/templates/`

### Settings & Environment

- All settings come from environment variables via `dbca_utils.utils.env()`
- Never hard-code secrets or environment-specific values
- Timezone is `Australia/Perth`; `USE_I18N = False`; `USE_TZ = True`
- Date formats: `DD/MM/YY` and `DD/MM/YYYY` variants

### Logging

- Use `LOGGER = logging.getLogger("ibms")` in all modules
- Log at `INFO` for significant user actions (e.g., CSV exports, uploads)
- Log at `DEBUG` for diagnostic detail

### Admin

- Inherit from `reversion.admin.VersionAdmin` for models that need change history
- Use `export_as_csv_action()` helper for CSV export admin actions
- Register with `@register(ModelName)` decorator

## Testing

- Test files: `test_models.py`, `test_views.py`, `test_forms.py`, `test_utils.py` in the `ibms` app; `tests.py` in `sfm`
- All test cases extend `IbmsTestCase` (from `ibms.tests`) which provides `self.fake`, `self.admin`, `self.user`, `self.fy`, `self.ibmdata`, and a logged-in client
- Use `mixer.blend(ModelClass, field=value)` to create test model instances
- Use `self.client.login(username=..., password="test")` when testing superuser views
- Run tests: `python manage.py test --keepdb -v2 --failfast`
- Coverage: `coverage run --source='.' manage.py test --keepdb -v2 --failfast`

## Health & Deployment

- Health endpoints: `GET /livez` (liveness) and `GET /readyz` (readiness with DB check) — handled by `HealthCheckMiddleware`, not Django URL routing
- Docker: built with `uv`, runs as `nonroot` user on port 8080 via gunicorn
- Static files collected at image build time with `collectstatic`
- Kubernetes manifests in `kustomize/`

## What Not to Do

- Do not use `pip install` — use `uv add <package>`
- Do not use `xlrd`, `xlwt`, or `xlutils` in new code — use `openpyxl`
- Do not use `BigAutoField` for new models — the project default is `AutoField`
- Do not add inline JavaScript — keep JS in static files
- Do not bypass `LoginRequiredMixin` on views
