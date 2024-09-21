# Library Manager APIs

This project is a library management system built with FastAPI. It includes two main components:
- **Admin API**: For managing library resources.
- **Frontend API**: For user interactions with the library.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.10 or later.

### Installation

- **Clone the repository**:
    ```sh
    git clone https://github.com/therealosy/library-manager.git
    cd library-manager
    ```

#### The Following Steps apply for the Admin and Frontend APIs:

- **Navigate to the API directory**
    ```sh
    cd admin-api # For the Admin API
    #OR
    cd frontend-api # For the Frontend API
    ```

- **Create and activate a virtual environment** (optional but recommended):
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

- **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

- **Set environment variables as required**
    ```sh
    APP_ENVIRONMENT="DEVELOPMENT" # Defaults to PRODUCTION
    DATABASE_URL="postgresql://user:password@host:port/db"
    KAFKA_BOOTSTRAP_SERVERS="host:port"
    KAFKA_BORROW_BOOK_TOPIC="borrow-topic"
    KAFKA_RETURN_BOOK_TOPIC="return-topic"
    KAFKA_REMOVE_BOOK_TOPIC="remove-topic"
    KAFKA_ADD_BOOK_TOPIC="add-topic"
    KAFKA_CREATE_USER_TOPIC="create-topic"
    KAFKA_UPDATE_USER_TOPIC="update-topic"
    POLL_ADMIN_INTERVAL_SECS="30" # Only required for frontend api
    POLL_FRONTEND_INTERVAL_SECS="30" # Only required for admin api
    UPDATE_RETURNED_BOOKS_CRONTAB="0 0 * * *" # Only required for admin api
    ```

    **OR alternatively create a `.env` file containing these variables**

    **Note:**
    The Swagger UI for each API is disabled when the environment variable `APP_ENVIRONMENT` is set to `PRODUCTION`. If set to anything else, the UI is available at `/docs`

- **Run tests**:
    ```sh
    python -m unittest -v
    ```

- **Run database migrations**:
    ```sh
    alembic upgrade head
    ```

- **Run application**:
    ```sh
    uvicorn main:app --host host --port port # Use --reload for live reloads
    ```

## Running the Project Using Docker Compose

**The following steps should be carried out in the project root directory**

- **Update the environment variables in `.build.env` as neccessary**

- **Build and run the containers**:
    ```sh
    docker compose --env-file .build.env up --build
    ```

    **Note**
    The Frontend API is exposed on port `8000` and the Admin API is exposed on port `8001`

## Accessing the APIs

### Accessing the Admin API:

The following endpoints are exposed:

***Book Management***
- `POST/api/books/` - Adds a book to the catalogue
- `GET/api/books/` - Gets all books in the catalogue
- `GET/api/books/borrowed` - Gets all books currently borrowed
- `GET/api/books/{id}` - Gets a book by it's id
- `DELETE/api/books/{id}` - Deletes a book from the catalogue

***User Management***
- `GET/api/users/` - Gets all registered users
- `GET/api/users/books` - Gets all registered users that have borrowed books
- `GET/api/users/{id}` - Gets a user by their id

***Health Check***
- `GET/health/status` - Gets Health status of the application

### Accessing the Frontend API:

The following endpoints are exposed:

***Book Management***
- `GET/api/books/` - Gets all books in the catalogue that can be borrowed
- `GET/api/books/search` - Gets all books that are similar to the search criteria
- `GET/api/books/{id}` - Gets a book by it's id
- `POST/api/books/{id}/borrow` - Borrows a book by it's id

***User Management***
- `POST/api/users/` - Registers a user
- `GET/api/users/{id}` - Gets a user by their id

***Health Check***
- `GET/health/status` - Gets Health status of the application

More information can be found in the Swagger UI documentation available at `/docs` for each API