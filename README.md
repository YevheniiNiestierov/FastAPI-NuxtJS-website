This project is a web application developed using the **FastAPI** framework for the backend and **NuxtJS** for the frontend. The application leverages **DynamoDB** and **S3** for storage. 

## Features

- **Backend**: Built with FastAPI.
- **Frontend**: Developed using NuxtJS.
- **Storage**: Utilizes DynamoDB and S3.
- **Cart and Order Logic**: Implemented with Redis for storing session IDs of anonymous users. Future plans include migrating this logic to DynamoDB.
- **User Management and Authentication**: Currently using SQLite and SQLalchemy. There are plans to rewrite these components to utilize DynamoDB.

## Current state details

- **Authentication**: Implemented at the API level as a demonstration of skillset. The current authentication setup is for API demonstration purposes only.


## Future Enhancements

- **Migration to DynamoDB**: User management, authentication, and cart logic will be migrated from SQLite and Redis to DynamoDB.
- **Extended Authentication**: Enhancements to the authentication system to cover more use cases and integration.
