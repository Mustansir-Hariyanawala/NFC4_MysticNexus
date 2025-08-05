# FastAPI Server

A FastAPI conversion of the original Node.js/Express server with MongoDB integration.

## Features

- **User Management**: Complete CRUD operations for users
- **Authentication**: Login and signup functionality with password hashing
- **MongoDB Integration**: Async MongoDB operations using Motor
- **Type Safety**: Full Pydantic model validation and typing
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Update the values with your MongoDB configuration

3. **Run the server**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration

### User Management
- `GET /api/users/` - Get all users
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/username/{username}` - Get user by username
- `POST /api/users/` - Create new user
- `PUT /api/users/change-password` - Change user password
- `DELETE /api/users/{user_id}` - Delete user

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
FastAPI_Server/
├── config/
│   └── mongodb.py          # MongoDB connection configuration
├── controllers/
│   ├── auth.py             # Authentication controller
│   └── users.py            # User management controller
├── models/
│   └── user.py             # Pydantic models for user data
├── routes/
│   ├── auth_apis.py        # Authentication routes
│   └── user_apis.py        # User management routes
├── utils/
│   └── password_utils.py   # Password hashing utilities
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Key Differences from Node.js Version

1. **Async/Await**: All database operations are asynchronous using Motor
2. **Type Safety**: Pydantic models provide request/response validation
3. **Auto Documentation**: FastAPI automatically generates API documentation
4. **Dependency Injection**: Clean separation using FastAPI's dependency system
5. **Error Handling**: Structured HTTP exceptions with proper status codes

## Environment Variables

- `DB_USERNAME`: MongoDB username
- `DB_PASSWORD`: MongoDB password
- `DB_CLUSTER_NAME`: MongoDB cluster name
- `DB_CLUSTER_ID`: MongoDB cluster ID
- `DB_NAME`: Database name
- `PORT`: Server port (default: 8000)
