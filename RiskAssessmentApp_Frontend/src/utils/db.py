import asyncio
import asyncpg
from src.core.config import DB_CONFIG


class Database:
    _pool = None

    @classmethod
    async def get_pool(cls):
        """Get or create a connection pool"""
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                min_size=5,
                max_size=20
            )
        return cls._pool

    @classmethod
    async def execute(cls, query, *args):
        """Execute a query that doesn't return rows"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    @classmethod
    async def fetch(cls, query, *args):
        """Execute a query that returns rows"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    @classmethod
    async def fetchrow(cls, query, *args):
        """Execute a query that returns a single row"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    @classmethod
    async def fetchval(cls, query, *args):
        """Execute a query that returns a single value"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @classmethod
    async def close(cls):
        """Close the connection pool"""
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None


# SQL Scripts for database initialization
INIT_TABLES = """
-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    department_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Departments table
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id INTEGER REFERENCES departments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, department_id)
);

-- Create Assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    project_id INTEGER REFERENCES projects(id),
    auditor_id INTEGER REFERENCES users(id),
    assessment_date DATE NOT NULL,
    risk_score NUMERIC(5,2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    scope TEXT,
    findings TEXT,
    recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create RiskFactors table
CREATE TABLE IF NOT EXISTS risk_factors (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    factor_name VARCHAR(100) NOT NULL,
    factor_value INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create SupportTickets table
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create TicketComments table
CREATE TABLE IF NOT EXISTS ticket_comments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES support_tickets(id),
    user_id INTEGER REFERENCES users(id),
    comment TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key to users table
ALTER TABLE users ADD CONSTRAINT fk_department 
    FOREIGN KEY (department_id) REFERENCES departments(id);
"""


async def initialize_database():
    """Initialize the database with required tables"""
    try:
        await Database.execute(INIT_TABLES)
        print("Database initialized successfully")

        # Check if admin user exists, create if not
        admin_exists = await Database.fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = 'admin')"
        )

        if not admin_exists:
            # In a real app, you would hash the password
            await Database.execute(
                """
                INSERT INTO users (username, password_hash, name, email, role)
                VALUES ($1, $2, $3, $4, $5)
                """,
                "admin",
                "admin",  # This would be hashed in production
                "Admin User",
                "admin@example.com",
                "admin"
            )
            print("Admin user created")

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
