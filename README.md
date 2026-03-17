E-commerce Dev Scaffold
========================

This is a development-only scaffold for an e-commerce site (React + Vite frontend, Django + DRF backend).
It is intentionally minimal for local development and testing (SQLite, DEBUG=True, local media).

How to run backend (Linux/macOS):
1. cd backend
2. python -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. cp .env.example .env
6. python manage.py migrate
7. python manage.py createsuperuser
8. python manage.py loaddata fixtures/products.json
9. python manage.py runserver

How to run frontend:
1. cd frontend
2. npm install
3. npm run dev
   The Vite dev server proxies /api to the backend (see package.json proxy / vite config).

Notes:
- Stripe endpoints use test mode; replace keys in .env for your testing.
- This scaffold is for development and learning only — do NOT use these settings in production.
