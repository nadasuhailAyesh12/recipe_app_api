# Django Docker Recipe Project

## Table of Contents

- [Introduction](##Introduction)
- [Prerequisites](##Prerequisites)
- [deployed Application](##Deployed-URL)
- [Setup and Running the Project Locally](##Setup-and-Running-the-Project-Locally)
  - [Clone the Repository](###Clone-the-Repository)
  - [Set Up Environment Variables](#set-up-environment-variables)
  - [Build and Run the Docker Containers](###Build-and-run-docker-containers)
  - [Access the Application](###Access-the-application)
  - [Making and Running Migrations](###Making-and-Running-Migrations)
  - [Creating a Superuser](###Creating-a-Superuser)
  - [Stopping the Containers](#stopping-the-containers)
- [API Endpoints](###API-Endpoints)
- [Note on API Testing](###Note-on-API-testing)
- [Models Overview](###Models-Overview)
- [Project Structure](###Project-Structure)
- [Done by](###Done-by)

## Introduction

This project is a Django application containerized with Docker, designed to manage recipes,users, ingredients, and tags.

## Prerequisites

Make sure you have the following installed and running on your local machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Deployed URL
-  [Docs URL](http://ec2-51-20-8-74.eu-north-1.compute.amazonaws.com/api/docs/)
-  [Admin page URL](http://ec2-51-20-8-74.eu-north-1.compute.amazonaws.com/admin/login/?next=/admin/) and enter your super user email and password

## Setup and Running the Project Locally

### Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```
### Set up enviroment varaibles
 copy sample.env :```cp sample.env .env```

### Build and run docker containers
```docker-compose up --build```

### Access the application
```http://127.0.0.1:8000/api/docs```

### Making and Running Migrations
If you need to make migrations and apply database migrations, run the following commands:
```docker-compose run --rm app sh -c "python manage.py makemigrations"```
```docker-compose run --rm app sh -c "python manage.py migrate"```
### Creating a Superuser
To create a superuser for accessing the Django admin, run:
```docker-compose run --rm app sh -c "python manage.py createsuperuser"'```
after creating your user by enterign email and password you can go to ``` http://127.0.0.1:8000/admin``` to test admin page

### Stopping the Containers
To stop the running containers, use:
```docker-compose down```

### API Endpoints
The application includes endpoints for managing recipes, ingredients, and tags. There is public and private endpoints.For testing endpoints
and know how to use each one you can go to the swagger documentation below
locally by hitting:
```http://127.0.0.1:8000/api/docs/```
or by go to the aws deployed link :
```http://ec2-51-20-8-74.eu-north-1.compute.amazonaws.com/api/docs/```

### Note on API testing
 Almost all of the API endpoints are private, meaning they require the user to be authenticated. To successfully test the endpoints without getting an unauthorized 401 error when accessing the Swagger link, please follow these steps:
1- Locate the User model endpoints.
2- Go to the POST: ```/api/user/create/``` endpoint and register a user.
3- Go to the ```POST: /api/user/token``` endpoint and log in with your email and password to obtain a token.
Click on the "Authorize" button at the top of the page, and in the last option (token), enter Token "your token from the previous step".
### Models Overview
For a quick overview, here are the main models:

Recipe: Contains fields for title, description, user, ingredients,time_minutes,price,link,image and tags.
User:  Contains fields for email,name,is_active,is_staff
Ingredient: Contains fields for name and user who added that ingredient.
Tag: Contains a field for the tag name and user who added it .

### Project Structure
![Screenshot 2024-06-18 at 10.20.57 PM](https://hackmd.io/_uploads/rkoE0U1UR.png)

### Done by
[Nada Ayesh](https://github.com/nadasuhailAyesh12)
