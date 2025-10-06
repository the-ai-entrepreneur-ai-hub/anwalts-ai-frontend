import asyncpg
import os
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
        self.connection_string = self._get_connection_string()

    async def update_user_password(self, user_id: uuid.UUID, new_password_hash: str) -> bool:
        """Update password hash for a user (non-destructive)."""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    "UPDATE users SET password_hash = $1 WHERE id = $2",
                    new_password_hash, user_id
                )
                return True
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
    
    def _get_connection_string(self):
        """Build PostgreSQL connection string from environment variables"""
        host = os.getenv("POSTGRES_HOST", "postgres")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "anwalts_ai")
        user = os.getenv("POSTGRES_USER", "anwalts_user")
        password = os.getenv("POSTGRES_PASSWORD", "anwalts_password")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            raise RuntimeError("Database not connected")
        return self.pool.acquire()
    
    async def health_check(self):
        """Check database health"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            raise
    
    # User management methods
    async def get_user_by_id(self, user_id: str):
        """Get user by ID"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT id, email, name, role, password_hash, created_at FROM users WHERE id = $1",
                    uuid.UUID(user_id)
                )
                if row:
                    return UserInDB(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str):
        """Get user by email"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT id, email, name, role, password_hash, created_at FROM users WHERE email = $1",
                    email
                )
                if row:
                    return UserInDB(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def create_user(self, email: str, name: str, role: str, password_hash: str):
        """Create a new user"""
        try:
            async with self.get_connection() as conn:
                user_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO users (id, email, name, role, password_hash, created_at) 
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    user_id, email, name, role, password_hash, datetime.utcnow()
                )
                return await self.get_user_by_id(str(user_id))
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            raise
    
    async def update_user_basic(self, user_id: uuid.UUID, name: str = None, role: str = None):
        """Update user basic information"""
        try:
            async with self.get_connection() as conn:
                if name and role:
                    await conn.execute(
                        "UPDATE users SET name = $1, role = $2 WHERE id = $3",
                        name, role, user_id
                    )
                elif name:
                    await conn.execute(
                        "UPDATE users SET name = $1 WHERE id = $2",
                        name, user_id
                    )
                elif role:
                    await conn.execute(
                        "UPDATE users SET role = $1 WHERE id = $2",
                        role, user_id
                    )
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    # User profile methods
    async def get_user_profile(self, user_id: uuid.UUID):
        """Get user profile"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM user_profiles WHERE user_id = $1",
                    user_id
                )
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None
    
    async def upsert_user_profile(self, user_id: uuid.UUID, profile_data):
        """Insert or update user profile"""
        try:
            async with self.get_connection() as conn:
                profile_dict = profile_data.model_dump() if hasattr(profile_data, 'model_dump') else dict(profile_data)
                
                # Remove None values
                profile_dict = {k: v for k, v in profile_dict.items() if v is not None}
                
                if profile_dict:
                    await conn.execute(
                        """INSERT INTO user_profiles (user_id, data, updated_at) 
                           VALUES ($1, $2, $3)
                           ON CONFLICT (user_id) 
                           DO UPDATE SET data = $2, updated_at = $3""",
                        user_id, json.dumps(profile_dict), datetime.utcnow()
                    )
                return profile_dict
        except Exception as e:
            logger.error(f"Error upserting user profile {user_id}: {e}")
            raise

    async def get_dashboard_summary(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Aggregate key dashboard metrics for the given user."""
        try:
            async with self.get_connection() as conn:
                documents_row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) AS total_count,
                        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS recent_count
                    FROM documents
                    WHERE user_id = $1
                    """,
                    user_id
                )

                messages_row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) AS total_count,
                        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS recent_count
                    FROM assistant_messages
                    WHERE user_id = $1
                    """,
                    user_id
                )

                analytics_row = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM analytics_events
                    WHERE user_id = $1
                      AND created_at >= NOW() - INTERVAL '30 days'
                      AND (event_type ILIKE 'case%' OR event_type ILIKE 'matter%' OR event_type ILIKE 'mandat%')
                    """,
                    user_id
                )

                next_deadline = await conn.fetchval(
                    """
                    SELECT expires_at
                    FROM api_tokens
                    WHERE user_id = $1
                      AND revoked_at IS NULL
                      AND expires_at IS NOT NULL
                      AND expires_at > NOW()
                    ORDER BY expires_at ASC
                    LIMIT 1
                    """,
                    user_id
                )

                documents_total = int(documents_row['total_count']) if documents_row and documents_row['total_count'] is not None else 0
                documents_recent = int(documents_row['recent_count']) if documents_row and documents_row['recent_count'] is not None else 0

                emails_total = int(messages_row['total_count']) if messages_row and messages_row['total_count'] is not None else 0
                emails_recent = int(messages_row['recent_count']) if messages_row and messages_row['recent_count'] is not None else 0

                new_cases = int(analytics_row) if analytics_row is not None else 0
                if new_cases == 0:
                    new_cases = documents_recent

                return {
                    "new_cases": new_cases,
                    "documents_total": documents_total,
                    "documents_recent": documents_recent,
                    "emails_total": emails_total,
                    "emails_recent": emails_recent,
                    "next_deadline": next_deadline.isoformat() if next_deadline else None,
                    "generated_at": datetime.utcnow().isoformat() + 'Z'
                }
        except Exception as e:
            logger.error(f"Error aggregating dashboard summary for user {user_id}: {e}")
            raise

    # Template methods
    async def get_templates(self, user_id: uuid.UUID, category: str = None):
        """Get templates for user"""
        try:
            async with self.get_connection() as conn:
                if category:
                    rows = await conn.fetch(
                        "SELECT * FROM templates WHERE user_id = $1 AND category = $2 ORDER BY created_at DESC",
                        user_id, category
                    )
                else:
                    rows = await conn.fetch(
                        "SELECT * FROM templates WHERE user_id = $1 ORDER BY created_at DESC",
                        user_id
                    )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting templates for user {user_id}: {e}")
            return []

    async def create_template(self, user_id: uuid.UUID, title: str, content: str, category: str = None):
        """Create a new template"""
        try:
            async with self.get_connection() as conn:
                template_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO templates (id, user_id, title, content, category, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    template_id, user_id, title, content, category, datetime.utcnow()
                )
                return {"id": str(template_id), "title": title, "content": content, "category": category}
        except Exception as e:
            logger.error(f"Error creating template for user {user_id}: {e}")
            raise

    async def update_template(
        self,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str = None,
        content: str = None,
        category: str = None
    ):
        """Update a template"""
        try:
            async with self.get_connection() as conn:
                updates = []
                params: list[Any] = []
                param_count = 1

                if title:
                    updates.append(f"title = ${param_count}")
                    params.append(title)
                    param_count += 1

                if content:
                    updates.append(f"content = ${param_count}")
                    params.append(content)
                    param_count += 1

                if category:
                    updates.append(f"category = ${param_count}")
                    params.append(category)
                    param_count += 1

                if updates:
                    updates.append(f"updated_at = ${param_count}")
                    params.append(datetime.utcnow())
                    param_count += 1

                    params.extend([template_id, user_id])

                    query = (
                        f"UPDATE templates SET {', '.join(updates)} "
                        f"WHERE id = ${param_count} AND user_id = ${param_count + 1}"
                    )
                    await conn.execute(query, *params)

                return {"id": str(template_id), "title": title, "content": content, "category": category}
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {e}")
            raise

    async def delete_template(self, template_id: uuid.UUID, user_id: uuid.UUID):
        """Delete a template"""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "DELETE FROM templates WHERE id = $1 AND user_id = $2",
                    template_id, user_id
                )
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}")
            return False

    # Clause methods
    async def get_clauses(
        self,
        user_id: uuid.UUID,
        category: str = None,
        language: str = None
    ):
        """Get clauses for user"""
        try:
            async with self.get_connection() as conn:
                query = "SELECT * FROM clauses WHERE user_id = $1"
                params: list[Any] = [user_id]

                if category:
                    query += " AND category = $2"
                    params.append(category)
                    if language:
                        query += " AND language = $3"
                        params.append(language)
                elif language:
                    query += " AND language = $2"
                    params.append(language)

                query += " ORDER BY created_at DESC"

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting clauses for user {user_id}: {e}")
            return []

    async def create_clause(
        self,
        user_id: uuid.UUID,
        title: str,
        content: str,
        category: str = None,
        language: str = None
    ):
        """Create a new clause"""
        try:
            async with self.get_connection() as conn:
                clause_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO clauses (id, user_id, title, content, category, language, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    clause_id, user_id, title, content, category, language, datetime.utcnow()
                )
                return {
                    "id": str(clause_id),
                    "title": title,
                    "content": content,
                    "category": category,
                    "language": language,
                }
        except Exception as e:
            logger.error(f"Error creating clause for user {user_id}: {e}")
            raise

    # Clipboard methods
    async def get_clipboard_entries(self, user_id: uuid.UUID, limit: int = 50):
        """Get clipboard entries for user"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM clipboard_entries WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
                    user_id, limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting clipboard entries for user {user_id}: {e}")
            return []

    async def create_clipboard_entry(
        self,
        user_id: uuid.UUID,
        content: str,
        entry_type: str = "text"
    ):
        """Create a new clipboard entry"""
        try:
            async with self.get_connection() as conn:
                entry_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO clipboard_entries (id, user_id, content, type, created_at)
                       VALUES ($1, $2, $3, $4, $5)""",
                    entry_id, user_id, content, entry_type, datetime.utcnow()
                )
                return {"id": str(entry_id), "content": content, "type": entry_type}
        except Exception as e:
            logger.error(f"Error creating clipboard entry for user {user_id}: {e}")
            raise

    # Analytics methods
    async def create_analytics_event(
        self,
        user_id: uuid.UUID,
        event_type: str,
        data: dict = None
    ):
        """Create an analytics event"""
        try:
            async with self.get_connection() as conn:
                event_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO analytics_events (id, user_id, event_type, data, created_at)
                       VALUES ($1, $2, $3, $4, $5)""",
                    event_id, user_id, event_type, json.dumps(data) if data else None, datetime.utcnow()
                )
                return {"id": str(event_id)}
        except Exception as e:
            logger.error(f"Error creating analytics event for user {user_id}: {e}")
            raise

    # Document methods
    async def create_document(
        self,
        user_id: uuid.UUID,
        title: str,
        content: str,
        document_type: str = None
    ):
        """Create a new document"""
        try:
            async with self.get_connection() as conn:
                doc_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO documents (id, user_id, title, content, type, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    doc_id, user_id, title, content, document_type, datetime.utcnow()
                )
                return {"id": str(doc_id), "title": title, "content": content, "type": document_type}
        except Exception as e:
            logger.error(f"Error creating document for user {user_id}: {e}")
            raise

    # API Token methods
    async def list_api_tokens(self, user_id: uuid.UUID):
        """List API tokens for user"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    "SELECT id, last4, expires_at, created_at FROM api_tokens WHERE user_id = $1 AND revoked_at IS NULL ORDER BY created_at DESC",
                    user_id
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing API tokens for user {user_id}: {e}")
            return []

    async def create_api_token(
        self,
        user_id: uuid.UUID,
        token: str,
        expires_at: datetime,
        last4: str
    ):
        """Create a new API token"""
        try:
            async with self.get_connection() as conn:
                token_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO api_tokens (id, user_id, token_hash, last4, expires_at, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    token_id, user_id, token, last4, expires_at, datetime.utcnow()
                )
                return {"id": str(token_id), "last4": last4, "expires_at": expires_at}
        except Exception as e:
            logger.error(f"Error creating API token for user {user_id}: {e}")
            raise

    async def revoke_api_token(self, user_id: uuid.UUID, token_id: uuid.UUID):
        """Revoke an API token"""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "UPDATE api_tokens SET revoked_at = $1 WHERE id = $2 AND user_id = $3",
                    datetime.utcnow(), token_id, user_id
                )
                return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error revoking API token {token_id}: {e}")
            return False

    async def get_api_token_owner(self, token: str):
        """Get the owner of an API token"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """SELECT u.id, u.email, u.name, u.role
                       FROM users u
                       JOIN api_tokens t ON u.id = t.user_id
                       WHERE t.token_hash = $1 AND t.revoked_at IS NULL AND t.expires_at > $2""",
                    token, datetime.utcnow()
                )
                if row:
                    return UserInDB(**dict(row), password_hash="", created_at=datetime.utcnow(), is_active=True)
                return None
        except Exception as e:
            logger.error(f"Error getting API token owner: {e}")
            return None

    # Call request methods
    async def create_call_request(self, name: str, phone: str, email: str = None, message: str = None):
        """Create a call request"""
        try:
            async with self.get_connection() as conn:
                request_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO call_requests (id, name, phone, email, message, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    request_id, name, phone, email, message, datetime.utcnow()
                )
                return {
                    "id": str(request_id),
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "message": message,
                }
        except Exception as e:
            logger.error(f"Error creating call request: {e}")
            raise

# Simple user model class to avoid circular imports
class UserInDB:
    def __init__(
        self,
        id,
        email,
        name,
        role,
        password_hash,
        created_at,
        is_active: Optional[bool] = None
    ):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.password_hash = password_hash
        self.created_at = created_at
        self.is_active = True if is_active is None else bool(is_active)

def get_database():
    """Dependency function to get database instance"""
    # This would typically return a singleton instance
    # For now, we'll assume the database instance is available globally
    return None  # This will be replaced by the actual instance
