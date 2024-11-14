# Stad Antwerpen

## Setup

1. Copy `.env.template` and rename it to `.env`
2. Fill in the values in the `.env` file

## Development

To run the application locally for development:
`docker-compose -f docker-compose-development.yml up --build -d`

The application should now be running. Access it at the URL specified in your `.env` file

To stop the local development environment:
`docker-compose -f docker-compose-development.yml down`

### Backend

First install uvicorn:

1. Open CMD
2. Install uvicorn: `pip install uvicorn`
3. Restart terminal
4. Check installation: `uvicorn --version`

To run the backend locally with uvicorn:
`uvicorn main:app --reload`

## Project Structure

-   Frontend code is located in the `frontend` directory:
    `antwerpen.localhost`
-   Backend code is located in the `backend/app` directory:
    `antwerpen.localhost/api`
-   Database: `elasticsearch.antwerpen.localhost`

## Production

To deploy the application on a server:
`docker-compose up --build -d`

The application should now be running in production mode

To stop the application on the server:
`docker-compose down`
