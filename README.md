# Job Portal & Application Tracker

A full-stack job portal built with **FastAPI**, **SQLAlchemy**, **MySQL**, **React** and **JWT authentication**.

## Project Structure

```
job-portal/
├── backend/          # FastAPI REST API
├── frontend/         # React SPA
├── docs/             # Documentation & SQL schemas
├── .gitignore
└── README.md
```

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database:** MySQL 8.x
- **Auth:** JWT (python-jose + passlib)
- **Frontend:** React 18, Vite, React Router v6, Axios
- **Migrations:** Alembic

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your MySQL credentials
uvicorn app.main:app --reload --port 8000
```

### Database

```bash
mysql -u root -p < docs/schema.sql
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## API Docs

Once running, visit: `http://localhost:8000/docs` (Swagger UI)

## License

MIT
