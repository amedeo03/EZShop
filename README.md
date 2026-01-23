# EZShop - Backend API System

## Overview

EZShop is a comprehensive backend system for managing small retail shop operations. It provides RESTful APIs for inventory management, sales processing, customer relationship management, and accounting functions. The system follows a client-server architecture and supports multiple user roles with distinct permissions.

## Key Features

- **User Management**: Role-based access control (Administrator, Shop Manager, Cashier)
- **Product Catalog**: Full CRUD operations for product types with barcode validation
- **Inventory Management**: Track stock levels, issue reorder warnings, and manage supplier orders
- **Sales Processing**: Handle sales transactions, returns, and various payment methods
- **Customer Management**: Maintain customer records and loyalty card programs
- **Accounting**: Track credits, debits, and compute balance over time periods

## Technology Stack

- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based token authentication
- **Validation**: Pydantic models
- **Testing**: pytest with async support
- **Documentation**: Swagger UI + `/doc` folder

## Quick Start

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Initialization (Administrator, Shop Manager, Cashier)
```bash
# Initialize database
python init_db.py
```

### 3. Run the Application
```bash
# Development server with auto-reload
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000/api/v1`

## Authentication

The system uses JWT tokens for authentication. 

The system comes with these default users:

| Username | Password | Role |
|----------|----------|------|
| admin | admin | Administrator |
| ShopManager | ShManager | Shop Manager |
| Cashier | Cashier | Cashier |

To access protected endpoints:

1. Login at `POST /api/v1/login` with username and password
2. Receive a JWT token in the response
3. Include the token in subsequent requests as a header:
   ```
   Authorization: Bearer <your_token>
   ```

## User Roles & Permissions

| Role | Key Permissions |
|------|----------------|
| **Administrator** | Full system access, user management |
| **Shop Manager** | Inventory, orders, accounting, customer management |
| **Cashier** | Sales transactions, returns, customer lookups |


## Testing

```bash
# Run tests with coverage report
pytest --cov=app ./tests/
```

## Project Structure

```
ezshop/
├── app/
│   ├── routes/           
│   ├── controllers/           
│   ├── repositories/           
│   ├── middleware/           
│   ├── models/        # SQLAlchemy models
│   ├── services/      # Business logic
│   └── database.py    # Database configuration
├── tests/             # Test suite
├── data/              # Data files (credit cards, etc.)
├── main.py            # Application entry point
├── init_db.py         # Database initialization
└── requirements.txt   # Python dependencies
```


## Development Notes

- The system is designed for small shops (500-2000 product types, 2+ cash registers)
- All API functions complete in < 0.5 seconds (performance requirement)
- Customer data privacy is enforced through authentication and authorization
- The system maintains ACID properties for financial transactions

## Troubleshooting

### Logs
Check the console output for detailed error messages and request logging.

## License & Credits

Developed as part of the Software Engineering course project. Based on the EZShop requirements document by Maurizio Morisio.

*For detailed API specifications, please refer to the interactive Swagger documentation at `/docs` when the server is running.*
