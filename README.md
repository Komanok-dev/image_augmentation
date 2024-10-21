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
