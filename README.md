# Stad Antwerpen

## Setup

1. Copy `.env.template` and rename it to `.env`
2. Fill in the values in the `.env` file

## Development

To run the application locally for development:
`docker compose -f docker-compose-development.yml up --build -d`

Then run the scraper locally for development, do this only if you build for the first time:
`docker compose -f docker-compose-scraper.yml up --build -d`

The application should now be running. Access it at the URL specified in your `.env` file

To stop the local development environment:
`docker compose -f docker-compose-development.yml down`

### Backend

First install uvicorn:

1. Open CMD
2. Install uvicorn: `pip install uvicorn`
3. Restart terminal
4. Check installation: `uvicorn --version`

To run the backend locally with uvicorn:
`uvicorn main:app --reload`

### Scraper

Scraper Resetten
Verwijder de scraper-status door het volume te resetten:
`docker-compose -f docker-compose.scraper.yml down -v`

## Project Structure

-   Frontend code is located in the `frontend` directory:
    `antwerpen.localhost`
-   Backend code is located in the `backend/app` directory:
    `antwerpen.localhost/api`
-   Database: `elasticsearch.antwerpen.localhost`

## Production

Connect to server:

-   SSH Command: `ssh uitdovend@78.46.102.226`
-   Password: `cWshWjB5pS4J9p`

To deploy the application on a server:
`docker compose up --build -d`

Then run the scraper on the server, do this only if you build for the first time:
`docker compose -f docker-compose-scraper.yml up --build -d`

The application should now be running in production mode

To stop the application on the server:
`docker compose down`

Server domain: `https://78.46.102.226/`

-   `antwerpen.redactie`
-   `antwerpen.redactie/api`
-   `antwerpen.redactie/es`
-   `antwerpen.redactie/scraper`
