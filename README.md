# Glove Project

## This project has been developed with the following objectives:
- evaluating abilities in large language models, vector databases, and API development
- creating a RESTful API service which can extract information from PDF documents and be able to answer questions




### Starting the application

In the project folder :

```
copy .env.example file to .env file because of this project is a demo project I directly added configurations to .env.example file.
```

#### If you added docker to user group
```sh
cd devops
docker-compose up -d  (for never docker versions use docker compose instead of docker-compose)
```
#### If you you did not
```sh
cd devops
sudo docker-compose up -d (for never docker versions use docker compose instead of docker-compose)
```

After this step go to /backend/.env file. And change enviroment values with these ips
(you can use portainer or docker inscept <container name> for learn ips)


DEV_POSTGRES_URL with ip from this command
```sh
cd devops
sudo docker inspect glove-postgres
```

DEV_MINIO_ENDPOINT with ip from this command
```sh
cd devops
sudo docker inspect minio
```

Fastapi service created for production enviroment thus you have to restart it with these command after previous steps completed
```sh
docker restart glove-fastapi
```

#### Notes
```
During these 'Starting the Application' steps the necessary ports assumed available/free
```

### Project Idea

During the project all of idea is asking questions to pdf files. System download pdf files for asking questions to these pdfs and return top 5 related answers I thought adding file management could be more beneficial for application cost

User may would ask multiple questions to same pdf or ask questions to previous downloaded pdf

Calculating embeddings every time then find vector similarity adds extra cost to system

Because of these reasons I added 3 new endpoints

#### These are:
 - Ask question to previously downloaded pdf with filename and question
 - List all downloaded pdfs
 - Delete selected pdf by name

### Additional Notes:
- Pytorch models are not releasing memories thus I used custom garbage collector
- I added Makefile to the system for possible future CI/CD processes. I thought about manage virtual env from another command but I could not be sure about am I using the same package management system with another user.
- You can create your virtual env and command 'make test' for testing
- It was my first time for creating tests for embedding model/S3-Like system Minio thus I got help from ChatGpt (I learned the logic)
- I have added authentication to /docs both username and password are : glov
- If you want to connect minio interface both username and password are : minioadmin



