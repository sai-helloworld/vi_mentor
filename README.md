# AI-Powered Mentor Backend

## Overview
This repository contains the backend for the AI-Powered Mentor project. It is designed to provide a robust backend infrastructure to support mentoring sessions using AI, featuring LangChain and Django, with RAG (Retrieval-Augmented Generation) technologies.

## Tech Stack
- **Python**
- **Django**
- **LangChain**

### Dependencies
The project dependencies are listed in `pyproject.toml`, including:
- Django
- LangChain
- Other libraries relevant to AI and web development

## Getting Started
To set up the project locally, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/sai-helloworld/vi_mentor.git
   cd vi_mentor
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Set up the database:
   ```bash
   python manage.py migrate
   ```
4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Documentation
- **Base URL**: `/api`

### Endpoints
1. **Mentor Sessions**
   - `POST /sessions`
   - `GET /sessions/{id}`
2. **Users**
   - `POST /users`
   - `GET /users/{id}`

## Project Features
- AI-powered mentoring sessions.
- User authentication and management.
- Session scheduling and management.
- Integration with external AI models for enhanced mentoring experience.

## Repository Links
- Front end Repository: [sai-helloworld/vi_mentor_frontend](https://github.com/sai-helloworld/vi_mentor_frontend)
