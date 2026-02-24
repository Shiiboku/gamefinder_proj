# 🎮 GameFinder API Core

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)

GameFinder is a scalable, high-performance REST API designed to power a modern video game tracking, rating, and discovery platform (similar to RAWG, Backloggd, or IGDB). Built with an enterprise-grade stack, it features complex relational data models, JWT-based authentication, and seamless third-party data integration capabilities.

## ✨ Key Features

* **Robust Authentication & Authorization:** Secure user registration, login, and JWT-based session management. Includes Role-Based Access Control (RBAC) with protected admin routes.
* **Dynamic User Profiles:** Public profile pages accessible via customizable URL routes (e.g., `/users/{username}`), keeping internal IDs secure.
* **Advanced Game Tracking:** Users can track game statuses (`planned`, `playing`, `completed`, `dropped`) and leave 0-10 scores.
* **Rich Game Metadata:** Full support for multilingual descriptions (via PostgreSQL `JSONB`), HowLongToBeat (HLTB) playtime stats, system requirements, cover images, and trailers.
* **High-Performance DB Architecture:** Optimized PostgreSQL schema utilizing SQLAlchemy 2.0 `joinedload` to eliminate N+1 query problems. 
* **Data Aggregation Ready:** Designed to work with background parsers fetching data from the IGDB API and Steam.

## 🚀 Roadmap / Upcoming Killer Features

* **Game Pulse:** Visual real-time graphs displaying the 24-hour online player count directly on the game page.
* **LLM "TL;DR" Summaries:** Automatic generation of 2-sentence game essences for titles with overwhelmingly long Steam descriptions.
* **1-Click Steam Sync:** A seamless integration button allowing users to instantly import their entire Steam library and ratings without manual data entry.
* **Party Finder (LFG):** A module to find teammates for multiplayer and MMO games based on shared interests and playtimes.

## 🛠️ Tech Stack

* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Declarative Base)
* **Migrations:** Alembic
* **Data Validation:** Pydantic v2 (`ConfigDict`, `AliasPath`)
* **Security:** Passlib (Bcrypt), PyJWT

## ⚙️ Local Setup & Installation

**1. Clone the repository and setup the virtual environment:**
```bash
git clone [https://github.com/yourusername/gamefinder_core.git](https://github.com/yourusername/gamefinder_core.git)
cd gamefinder_core
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
2. Configure Environment Variables:
Create a .env file in the root directory and add your credentials:

Ini, TOML
DATABASE_URL=postgresql://username:password@localhost/gamefinder
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=300
TWITCH_CLIENT_ID=your_igdb_client_id
TWITCH_CLIENT_SECRET=your_igdb_client_secret
3. Apply Database Migrations:
Initialize your PostgreSQL database with the required tables and constraints:

Bash
alembic upgrade head
4. Run the Application:
Start the Uvicorn development server:

Bash
uvicorn main:app --reload
5. Explore the API:
Open your browser and navigate to http://127.0.0.1:8000/docs to interact with the auto-generated Swagger UI.

📁 Project Structure
Plaintext
gamefinder_core/
├── alembic/                # Database migration scripts
├── models/                 # SQLAlchemy ORM models (User, Game, Rating, etc.)
├── routers/                # FastAPI endpoint handlers (auth, users, games, admin)
├── scripts/                # Utility scripts (e.g., IGDB API parsers)
├── alembic.ini             # Alembic configuration
├── auth.py                 # JWT token generation and password hashing
├── crud.py                 # Database operations (Create, Read, Update, Delete)
├── db.py                   # DB Engine and Session management
├── dependencies.py         # FastAPI Depends() injections (get_db, get_current_user)
├── main.py                 # FastAPI application instance and router registration
├── schemas.py              # Pydantic models for request/response validation
└── README.md