#!/usr/bin/env python3
import asyncio
import asyncpg
import bcrypt
import os

async def fix_password():
    # Database connection
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        host = os.getenv("POSTGRES_HOST", "postgres")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "anwalts_ai")
        user = os.getenv("POSTGRES_USER", "anwalts_user")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Generate proper bcrypt hash
    password = "admin123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_str = hashed.decode('utf-8')
    
    print(f"Generated hash: {hashed_str}")
    
    # Connect and update
    conn = await asyncpg.connect(database_url)
    
    try:
        # Update the password
        result = await conn.execute(
            "UPDATE users SET password_hash = $1 WHERE email = $2",
            hashed_str,
            "the.ai.entrepreneur.ai.hub@gmail.com"
        )
        print(f"Update result: {result}")
        
        # Verify the update
        row = await conn.fetchrow(
            "SELECT email, password_hash FROM users WHERE email = $1",
            "the.ai.entrepreneur.ai.hub@gmail.com"
        )
        print(f"Updated record: {row}")
        
        # Test verification
        stored_hash = row['password_hash']
        verify_result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"Verification test: {verify_result}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_password())
