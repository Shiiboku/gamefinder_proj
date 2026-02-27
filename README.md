# 🎮 GameFinder API Core

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)

GameFinder is a scalable, high-performance REST API designed to power a modern video game tracking, rating, and discovery platform (similar to RAWG, Backloggd, or IGDB). Built with an enterprise-grade stack, it features complex relational data models, JWT-based authentication, and seamless third-party data integration capabilities.

## ✨ Key Features

* **Robust Authentication & Authorization:** Secure user registration, login, and JWT-based session management. Includes Role-Based Access Control (RBAC) with protected admin routes.
* **Dynamic User Profiles & Stats:** Public profile pages accessible via customizable URL routes. Features real-time aggregated statistics (games completed, dropped, playing, etc.) while keeping sensitive data (like emails) completely secure.
* **Advanced Game Tracking:** Users can track game statuses using strict enums (`planned`, `playing`, `completed`, `dropped`) and leave 1-10 scores with dynamically computed reaction stickers.
* **Automated Release Scheduler:** Integrated `APScheduler` background task that continuously monitors upcoming releases and automatically updates game availability based on exact UTC release datetimes.
* **Smart Background Import:** Fault-tolerant background workers using FastAPI `BackgroundTasks` for parsing thousands of games from IGDB with automatic pagination, regex-based Steam ID matching, and a global kill-switch.
* **Rich Game Metadata:** Full support for multilingual descriptions (via PostgreSQL `JSONB`), HowLongToBeat (HLTB) playtime stats, system requirements, cover images, and trailers.
* **High-Performance DB Architecture:** Optimized PostgreSQL schema utilizing SQLAlchemy 2.0 `joinedload` to eliminate N+1 query problems.

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
* **Background Tasks:** APScheduler, FastAPI BackgroundTasks
* **Data Validation:** Pydantic v2 (`ConfigDict`, `@computed_field`)
* **Security:** Passlib (Bcrypt), PyJWT

## ⚙️ Local Setup & Installation

**1. Clone the repository and setup the virtual environment:**
```bash
git clone [https://github.com/yourusername/gamefinder_core.git](https://github.com/yourusername/gamefinder_core.git)
cd gamefinder_core
python -m venv .venv

# On Windows use: 
.venv\Scripts\activate
# On Linux/Mac use: 
source .venv/bin/activate

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
Start the Uvicorn development server with APScheduler active:

Bash
uvicorn main:app --reload
5. Explore the API:
Open your browser and navigate to http://127.0.0.1:8000/docs to interact with the auto-generated Swagger UI.

📁 Project Structure
Plaintext
gamefinder_core/
├── alembic/                # Database migration scripts
├── models/                 # SQLAlchemy ORM models (User, Game, UserGameStatus, etc.)
├── routers/                # FastAPI endpoint handlers (auth, users, games, admin)
├── scripts/                # Utility scripts (e.g., IGDB API parsers)
├── alembic.ini             # Alembic configuration
├── auth.py                 # JWT token generation and password hashing
├── crud.py                 # Database operations (Create, Read, Update, Delete)
├── db.py                   # DB Engine and Session management
├── dependencies.py         # FastAPI Depends() injections (get_db, get_current_user)
├── main.py                 # FastAPI app instance and lifespan events
├── schemas.py              # Pydantic models for request/response validation
├── scheduler.py            # APScheduler background tasks logic
└── README.md