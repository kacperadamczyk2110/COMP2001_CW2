# COMP2001_CW2

# TrailService Micro-Service

## Overview
The TrailService micro-service is part of a well-being trail application designed to encourage outdoor activities and enhance users' well-being. This micro-service manages trail data, including creating, reading, updating, and deleting trails, along with user authentication and trail ownership.

## Project Structure
The project consists of the following main components:
- `app.py`: The main Flask application file.
- `auth.py`: Handles user authentication.
- `database.py`: Manages database connections and table definitions.
- `requirements.txt`: Specifies project dependencies.
- `Dockerfile`: Defines the steps to create a Docker image.
- `templates/`: Contains HTML templates.
- `static/`: Contains static files such as Swagger YAML file.
- `README.md`: This file.

## Features
- **User Authentication:** Secure user authentication using the Authenticator API.
- **Trail Management:** CRUD operations for trails.
- **Role-Based Access Control:** Limited view for non-owners and full control for trail owners.
- **RESTful API:** Follows RESTful principles for clear and consistent API design.
- **Secure:** Implements security best practices to mitigate common vulnerabilities (OWASP Top 10).

## Installation
### Prerequisites
- Docker
- Python 3.9

### Steps
1. **Clone the repository:**
    ```bash
    git clone https://github.com/kacperadamczyk2110/COMP2001_CW2.git
    cd COMP2001_CW2
    ```

2. **Build the Docker image:**
    ```bash
    docker build -t trail-service .
    ```

3. **Run the Docker container:**
    ```bash
    docker run -d -p 8000:8000 --name trail-service-container trail-service
    ```

4. **Access the application:**
    Open your browser and navigate to `http://localhost:8000`.

## API Endpoints
- **POST /api/login:** Authenticate a user.
- **POST /api/logout:** Log out a user.
- **GET /api/trails:** Retrieve all trails.
- **POST /api/trails:** Create a new trail.
- **GET /api/trails/{trail_id}:** Retrieve a specific trail by ID.
- **PUT /api/trails/{trail_id}:** Update an existing trail.
- **DELETE /api/trails/{trail_id}:** Delete a trail.

## Environment Variables
To set up the environment variables, you can pass them when running the Docker container:
```bash
docker run -d -p 8000:8000 --name trail-service-container -e DB_HOST=your_db_host -e DB_NAME=your_db_name trail-service
