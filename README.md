MIO Legal Tech Assessment - Infrastructure Setup

Section 1 : 
    Here is a quick overview of how the backend infrastructure is set up for this project and how to get it running.

    What We Built:
    To make this truly production-ready, we containerized the entire stack using Docker. 
        - We used a multi-stage Docker build to keep the final image lightweight and secure (it runs as a restricted, non-root user).
        - The Django app runs on Gunicorn.
        - A custom entrypoint script automatically handles database migrations and static files before the app accepts traffic.
        - The `docker-compose` setup spins up PostgreSQL, Redis, Celery (Worker & Beat), and the Django web app all at once.

    How to Run It Locally:
         You do not need to install Python, Postgres, or Redis on your machine—just make sure Docker is running.

    1. Set up your environment variables by copying the example file:
        cp .env.example .env

    2. Build and start all the services:
        docker-compose up --build

    3. Access the API:
        Once the terminal shows everything is running, the API will be available at http://localhost:8000.

    To stop the application, just press Ctrl+C in your terminal. To completely tear it down and clear the containers,
        run `docker-compose down`.    
    

    hint : to add new app to the project create folder with the <app_name> ,then in Docker Application or Termminal run python manage.py startapp <app_name> apps/<app_name> , change the apps.py to add the name as : "apps.<app_name>"

Section 2 :
    Task 1 : 
        1- Architectural Decision: Custom User Model
        I opted to use `AbstractBaseUser` rather than `AbstractUser`. Modern APIs and legal tech platforms universally use email addresses for authentication. `AbstractUser` forces the inclusion of a `username` field, which requires awkward workarounds to remove or bypass. `AbstractBaseUser` provides a clean, secure slate, allowing `email` to be the true `USERNAME_FIELD` while keeping the database schema lean.
    Task 2:
        1- Architectural Decision: Shared Utilities with Common App
        To keep our codebase clean and maintainable, we introduced a dedicated `common` app for shared utilities that can be reused across different parts of the project. This includes custom permissions, exception handlers, and file validators that go beyond simple extension checks—ensuring files are not only the right type but also meet size limits, content integrity, and security standards to protect against malicious uploads.

        2- Architectural Decision: Service Layer for Business Logic Separation
        We implemented a service layer pattern to cleanly separate business logic from our views and serializers. This keeps our views thin and focused on request/response handling, while complex operations like contract creation, status transitions, and file attachments are encapsulated in dedicated service classes. This approach improves testability, reusability, and makes the codebase easier to maintain as the application grows.
    
    Task 3: 
        1- Notifications: Async Alerts via Celery
        The `notifications` app powers asynchronous message delivery using Celery. It centralizes notification rules in a service class and triggers background tasks so the API stays responsive while emails/notifications are delivered in the background.