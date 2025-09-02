# Django & Next.js Authentication Fullstack Application

## Overview
This is a full-stack authentication application built with Django and Django Rest Framework (DRF) on the backend, and Next.js with Tailwind CSS on the frontend. The application uses Djoser for authentication and Wretch for API calls.

## Tech Stack
- **Backend**: Django, Django Rest Framework (DRF), Djoser
- **Frontend**: Next.js, Tailwind CSS, Wretch
- **Containerization**: Docker and Docker Compose (optional)

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) (optional)
- [Python 3.x](https://www.python.org/)
- [Node.js and npm](https://nodejs.org/)

## Setup

### Option 1: Setup with Docker (Recommended)

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/kiasamouie/admin.git && cd admin
    ```

2. **Run Docker Compose**:
    ```bash
    docker-compose up -d --build
    ```

    This will build and run the backend and frontend containers. By default:
    - The **Django backend** will run on [http://localhost:8000](http://localhost:8000)
    - The **Next.js frontend** will run on [http://localhost:3000](http://localhost:3000)

### Option 2: Manual Setup

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/kiasamouie/admin.git && cd admin
    ```

2. **Backend Setup**:
    - Run the `setup.sh` script to install dependencies and set up the virtual environment.
      ```bash
      chmod +x setup.sh
      ./setup.sh
      ```

    - Activate the Python virtual environment and start the Django server:
      ```bash
      source venv/bin/activate
      python manage.py runserver
      ```

    The Django backend will now be running at [http://localhost:8000](http://localhost:8000).

3. **Frontend Setup**:
    - Navigate to the frontend directory:
      ```bash
      cd frontend
      ```

    - Install frontend dependencies:
      ```bash
      npm install
      ```

    - Start the Next.js development server:
      ```bash
      npm run dev
      ```

    The Next.js frontend will now be running at [http://localhost:3000](http://localhost:3000).

## Contributing
Feel free to submit issues, fork the repository, and send pull requests.

## License
This project is licensed under the MIT License.
