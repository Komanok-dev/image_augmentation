## Image Augmentation

Application for transforming images: rotating, reducing the size, and converting to grayscale

Make sure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

1. **Clone the Repository**
    Clone the repository to your local machine:
    ```
    git clone git@github.com:Komanok-dev/image_augmentation.git
    cd image_augmentation
    ```

2. **Create .env as the .env.example providing your settings:**

3. **Build and Run the Docker Containers:**
    ```
    docker compose up --build
    ```

4. **Apply initial migrations:**
    ```
    docker compose run app alembic revision --autogenerate -m 'Initial migration'
    docker compose run app alembic upgrade head
    ```

5. **Access the Application:**

    The application will be running on http://localhost:8000.
    Swagger UI: You can view the API documentation and test the endpoints using Swagger UI:
    ```
    http://localhost:8000/docs
    ```

6. **Test the Application:**
    ```
    docker compose run app pytest
    ```

Unit tests coverage report:

| Name                         | Stmts | Miss | Cover |
|------------------------------|-------|------|-------|
| app/__init__.py              |     0 |    0 | 100%  |
| app/auth.py                  |    57 |    0 | 100%  |
| app/celery.py                |     4 |    0 | 100%  |
| app/database.py              |    25 |    0 | 100%  |
| app/minio_client.py          |    10 |    0 | 100%  |
| app/models.py                |    34 |    0 | 100%  |
| app/schemas.py               |     7 |    0 | 100%  |
| app/settings.py              |    49 |    0 | 100%  |
| app/tasks.py                 |    51 |    0 | 100%  |
| tests/__init__.py            |     0 |    0 | 100%  |
| tests/conftest.py            |    57 |    0 | 100%  |
| tests/test_auth.py           |   148 |    0 | 100%  |
| tests/test_celery.py         |     5 |    0 | 100%  |
| tests/test_database.py       |    43 |    0 | 100%  |
| tests/test_minio_client.py   |    27 |    0 | 100%  |
| tests/test_models.py         |    39 |    0 | 100%  |
| tests/test_schemas.py        |    41 |    0 | 100%  |
| tests/test_tasks.py          |    27 |    0 | 100%  |
|------------------------------|-------|------|-------|
| **TOTAL**                    |   624 |    0 | **100%** |
