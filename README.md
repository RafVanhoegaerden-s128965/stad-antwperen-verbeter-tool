# Stad Antwerpen

## Setup

1. Copy `.env.template` and rename it to `.env`
2. Fill in the values in the `.env` file

## Development

1. Clone this repository
2. Navigate to the project root
3. Run `docker-compose up --build -d`

## Development

To run the application locally for development:

1. Ensure you have Docker and Docker Compose installed on your machine
2. From the project root, run:
   `docker-compose -f docker-compose-development.yml up --build -d`

The application should now be running. Access it at the URL specified in your `.env` file

To stop the local development environment:
`docker-compose -f docker-compose-development.yml down`

## Project Structure

-   Frontend code is located in the `frontend` directory
    `antwerpen.localhost`
-   Backend code is located in the `backend/app` directory
    `antwerpen.localhost/api`

## Production

To deploy the application on a server:

1. Ensure Docker and Docker Compose are installed on your server
2. Clone the repository on your server
3. Set up your .env file with production values
4. From the project root, run:
   `docker-compose up --build -d`

The application should now be running in production mode

To stop the application on the server:
`docker-compose down`
