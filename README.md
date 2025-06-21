# goit-pythonweb-hw-12

# Contact Management API

A modern REST API for managing contacts built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- **CRUD Operations**: Create, read, update, and delete contacts
- **Search Functionality**: Search contacts by first name, last name, or email
- **Birthday Reminders**: Get contacts with upcoming birthdays (next 7 days)
- **Async Support**: Built with async/await for high performance
- **Database Migrations**: Alembic integration for schema management
- **Type Safety**: Pydantic models for request/response validation

## Project Structure

```
├── src/
│   ├── api/
│   │   └── contacts.py          # Contact endpoints
│   ├── conf/
│   │   └── config.py           # Configuration settings
│   ├── database/
│   │   ├── db.py               # Database session management
│   │   └── models.py           # SQLAlchemy models
│   ├── repository/
│   │   └── contacts.py         # Data access layer
│   ├── services/
│   │   └── contacts.py         # Business logic layer
│   └── schemas.py              # Pydantic schemas
├── migrations/                 # Alembic migration files
├── main.py                     # FastAPI application entry point
├── docker-compose.yml          # PostgreSQL container setup
└── requirements.txt            # Python dependencies
```

## Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for PostgreSQL)

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd goit-pythonweb-hw-08
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

5. **Start PostgreSQL database**

   ```bash
   docker-compose up -d
   ```

6. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   python3 main.py
   ```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once the application is running, you can access:

- **Interactive API docs**: http://127.0.0.1:8000/docs
- **ReDoc documentation**: http://127.0.0.1:8000/redoc

## API Endpoints

### Contacts

- `GET /api/contacts/` - Get all contacts (with pagination)
- `POST /api/contacts/` - Create a new contact
- `GET /api/contacts/{contact_id}` - Get contact by ID
- `PUT /api/contacts/{contact_id}` - Update contact
- `DELETE /api/contacts/{contact_id}` - Delete contact
- `GET /api/contacts/search/` - Search contacts by name or email
- `GET /api/contacts/birthdays/` - Get contacts with upcoming birthdays

### Example Request

**Create a contact:**

```bash
curl -X POST "http://127.0.0.1:8000/api/contacts/" \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "John",
       "last_name": "Doe",
       "email": "john.doe@example.com",
       "phone_number": "+1234567890",
       "birth_date": "1990-01-15",
       "additional_data": "Some notes"
     }'
```

## Database Schema

The [`Contact`](src/database/models.py) model includes:

- `id`: Primary key
- `first_name`: Contact's first name (max 50 chars)
- `last_name`: Contact's last name (max 50 chars)
- `email`: Unique email address (max 100 chars)
- `phone_number`: Phone number (max 20 chars)
- `birth_date`: Date of birth
- `additional_data`: Optional additional information

## Configuration

Database configuration is managed through environment variables in [`.env`](.env):

```env
DATABASE_URL=postgresql+asyncpg://postgres:htchtc26@localhost:5432/contacts_db
```

The configuration is loaded in [`src/conf/config.py`](src/conf/config.py).

## Development

### Database Migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

### Project Architecture

The project follows a layered architecture:

1. **API Layer** ([`src/api/contacts.py`](src/api/contacts.py)): FastAPI endpoints
2. **Service Layer** ([`src/services/contacts.py`](src/services/contacts.py)): Business logic
3. **Repository Layer** ([`src/repository/contacts.py`](src/repository/contacts.py)): Data access
4. **Database Layer** ([`src/database/`](src/database/)): Models and session management

### Key Components

- **Models**: SQLAlchemy models in [`src/database/models.py`](src/database/models.py)
- **Schemas**: Pydantic models in [`src/schemas.py`](src/schemas.py)
- **Database Session**: Async session management in [`src/database/db.py`](src/database/db.py)

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **asyncpg**: PostgreSQL adapter for async operations
- **PostgreSQL**: Relational database

## License

This project is for educational purposes as part of the GoIT Python Web Development course.
