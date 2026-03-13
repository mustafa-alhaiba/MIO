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