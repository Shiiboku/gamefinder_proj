# GameFinder Core 🎮

This is the backend core for a video game discovery, rating, and tracking platform (similar to MyAnimeList or Letterboxd, but for video games). It provides a robust Object-Relational Mapping (ORM) layer, a secure authentication module, and a scalable set of CRUD operations.

## 🚀 Features

* **Advanced Database Architecture:** Implements complex One-to-Many (1:M) and Many-to-Many (M:M) relationships using association tables with additional metadata (e.g., `is_primary` flags for genres).
* **Entity Management:** Fully defined models for Users, Games, Genres, Platforms, Developers, Ratings, and User Game Statuses.
* **Security First:** Secure password hashing using the modern `bcrypt` library (salted hashes), ensuring protection against brute-force attacks.
* **Thin CRUD Layer:** Atomic database operations using `flush()` instead of `commit()` within CRUD functions, giving the caller full control over transactions.
* **Clean Testing:** Database testing scripts are configured to use `session.rollback()`, ensuring the database remains perfectly clean without leaving test artifacts behind.

## 🛠 Tech Stack

* **Language:** Python 3.x
* **ORM:** SQLAlchemy 2.0+
* **Database:** PostgreSQL
* **Security:** `bcrypt`

## 📂 Project Structure

* `db.py` — Database engine setup and session management.
* `models/` — Directory containing declarative SQLAlchemy models:
    * `user.py`, `game.py`, `genre.py`, `platform.py`, `developer.py` — Core entities.
    * `rating.py`, `user_game_status.py` — User-generated content and tracking states.
    * `game_genre.py`, `game_platform.py` — Association tables (M:M relationships).
* `crud.py` — Business logic layer (e.g., user creation, querying by email/username).
* `auth.py` — Security layer (password hashing and verification engines).
* `tests/test_db.py` — Testing script for database connections and CRUD operations with automatic rollback.

## ⚙️ Installation & Setup

1. **Clone the repository and navigate to the project folder:**
   ```bash
   git clone <your-repository-url>
   cd gamefinder_core
   
Create and activate a virtual environment:

Bash
# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on Linux/macOS:
source .venv/bin/activate
Install dependencies:

Bash
pip install sqlalchemy psycopg2 bcrypt
Database Configuration:
Ensure PostgreSQL is running locally (or remotely) and that you have created an empty database for the project. Update your connection string in db.py with your credentials (username, password, database name).

Run tests:
Verify that your models map correctly and CRUD operations work without leaving artifact data:

Bash
python tests/test_db.py