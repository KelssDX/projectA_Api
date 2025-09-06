import asyncio
from src.api.client import APIClient, APIError
from src.models.user import User
from src.utils.db import Database


class UserController:
    def __init__(self):
        self.api_client = APIClient()

    async def get_users(self, filters=None):
        """
        Get list of users with optional filtering

        Args:
            filters: Dictionary of filter criteria (optional)

        Returns:
            List of user objects
        """
        try:
            # Try API first
            endpoint = "users"

            # Add query parameters for filters if provided
            if filters:
                query_params = []
                for key, value in filters.items():
                    if value is not None:
                        query_params.append(f"{key}={value}")

                if query_params:
                    endpoint = f"{endpoint}?{'&'.join(query_params)}"

            response = await self.api_client.get(endpoint)

            # Convert API response to User objects
            users = []
            for user_data in response.get("users", []):
                users.append(User.from_json(user_data))

            return users

        except APIError as e:
            print(f"API get users failed: {str(e)}")

            # Fall back to database
            try:
                query = """
                SELECT 
                    u.id,
                    u.username,
                    u.name,
                    u.email,
                    u.role,
                    u.department_id,
                    d.name AS department
                FROM 
                    users u
                LEFT JOIN 
                    departments d ON u.department_id = d.id
                """

                # Build WHERE clause for filters
                where_clauses = []
                params = []
                param_idx = 1

                if filters:
                    if filters.get("role"):
                        where_clauses.append(f"u.role = ${param_idx}")
                        params.append(filters["role"])
                        param_idx += 1

                    if filters.get("department_id"):
                        where_clauses.append(f"u.department_id = ${param_idx}")
                        params.append(filters["department_id"])
                        param_idx += 1

                    if filters.get("search"):
                        where_clauses.append(
                            f"(u.username ILIKE ${param_idx} OR u.name ILIKE ${param_idx} OR u.email ILIKE ${param_idx})")
                        params.append(f"%{filters['search']}%")
                        param_idx += 1

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY u.name ASC"

                # Execute query
                rows = await Database.fetch(query, *params)

                # Convert rows to User objects
                users = []
                for row in rows:
                    user_dict = dict(row)
                    users.append(User(
                        id=user_dict["id"],
                        username=user_dict["username"],
                        name=user_dict["name"],
                        email=user_dict["email"],
                        role=user_dict["role"],
                        department=user_dict["department"]
                    ))

                return users

            except Exception as db_error:
                print(f"Database get users failed: {str(db_error)}")

                # For development/demo purposes, return some dummy users
                return [
                    User(1, "admin", "Admin User", "admin@example.com", "admin"),
                    User(2, "jsmith", "John Smith", "john.smith@example.com", "auditor", "Information Technology"),
                    User(3, "sjohnson", "Sarah Johnson", "sarah.johnson@example.com", "auditor", "Finance"),
                    User(4, "mbrown", "Mike Brown", "mike.brown@example.com", "user", "Human Resources"),
                ]

    async def get_user(self, user_id):
        """
        Get a single user by ID

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User object if found, None otherwise
        """
        try:
            # Try Identity API first
            user_data = await self.identity_client.get_user(user_id)
            return User(
                id=user_data.get("id"),
                username=user_data.get("username"),
                name=user_data.get("name"),
                email=user_data.get("email"),
                role=user_data.get("role"),
                department=user_data.get("department")
            )

        except Exception as api_error:
            print(f"Identity API get user failed: {str(api_error)}")

            # Fall back to database
            try:
                query = """
                SELECT 
                    id, username, name, email, role, department, is_active
                FROM user_view
                WHERE id = $1
                """

                row = await Database.fetchrow(query, user_id)

                if row:
                    user_dict = dict(row)
                    return User(
                        id=user_dict["id"],
                        username=user_dict["username"],
                        name=user_dict["name"],
                        email=user_dict["email"],
                        role=user_dict["role"],
                        department=user_dict["department"]
                    )

                return None

            except Exception as db_error:
                print(f"Database get user failed: {str(db_error)}")

                # For development/demo purposes
                if user_id == 1:
                    return User(1, "admin", "Admin User", "admin@example.com", "admin")

                return None

    async def create_user(self, user_data):
        """
        Create a new user

        Args:
            user_data: Dictionary containing user data

        Returns:
            Created User object if successful, None otherwise
        """
        try:
            # Try Identity API first
            # Convert frontend format to backend format
            create_request = {
                "username": user_data["username"],
                "password": user_data["password"],
                "firstname": user_data.get("firstname", user_data.get("name", "").split(" ")[0]),
                "lastname": user_data.get("lastname", " ".join(user_data.get("name", "").split(" ")[1:])),
                "email": user_data["email"],
                "roleId": user_data.get("role_id"),
                "departmentId": user_data.get("department_id")
            }
            
            created_user_data = await self.identity_client.create_user(create_request)
            return User(
                id=created_user_data.get("id"),
                username=created_user_data.get("username"),
                name=created_user_data.get("name"),
                email=created_user_data.get("email"),
                role=created_user_data.get("role"),
                department=created_user_data.get("department")
            )

        except Exception as api_error:
            print(f"Identity API create user failed: {str(api_error)}")

            # Fall back to database
            try:
                # Check if username or email already exists
                check_query = """
                SELECT user_id FROM accounts WHERE username = $1 OR email = $2
                """

                existing = await Database.fetchrow(
                    check_query,
                    user_data["username"],
                    user_data["email"]
                )

                if existing:
                    return None  # Username or email already taken

                # Insert new user
                insert_query = """
                INSERT INTO accounts (
                    username, password, firstname, lastname, email, role_id, department_id
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING user_id
                """

                user_id = await Database.fetchval(
                    insert_query,
                    user_data["username"],
                    user_data["password"],  # Should be hashed in real app
                    user_data.get("firstname", user_data.get("name", "").split(" ")[0]),
                    user_data.get("lastname", " ".join(user_data.get("name", "").split(" ")[1:])),
                    user_data["email"],
                    user_data.get("role_id", 3),  # Default to user role
                    user_data.get("department_id")
                )

                if user_id:
                    # Get the created user from view
                    return await self.get_user(user_id)

                return None

            except Exception as db_error:
                print(f"Database create user failed: {str(db_error)}")
                return None

    async def update_user(self, user_id, user_data):
        """
        Update an existing user

        Args:
            user_id: ID of the user to update
            user_data: Dictionary containing updated user data

        Returns:
            Updated User object if successful, None otherwise
        """
        try:
            # Try Identity API first
            # Convert frontend format to backend format
            update_request = {}
            
            if "firstname" in user_data:
                update_request["firstname"] = user_data["firstname"]
            elif "name" in user_data:
                update_request["firstname"] = user_data["name"].split(" ")[0]
                
            if "lastname" in user_data:
                update_request["lastname"] = user_data["lastname"]
            elif "name" in user_data:
                update_request["lastname"] = " ".join(user_data["name"].split(" ")[1:])
                
            if "email" in user_data:
                update_request["email"] = user_data["email"]
            if "role_id" in user_data:
                update_request["roleId"] = user_data["role_id"]
            if "department_id" in user_data:
                update_request["departmentId"] = user_data["department_id"]
            if "is_active" in user_data:
                update_request["isActive"] = user_data["is_active"]
            
            updated_user_data = await self.identity_client.update_user(user_id, update_request)
            return User(
                id=updated_user_data.get("id"),
                username=updated_user_data.get("username"),
                name=updated_user_data.get("name"),
                email=updated_user_data.get("email"),
                role=updated_user_data.get("role"),
                department=updated_user_data.get("department")
            )

        except Exception as api_error:
            print(f"Identity API update user failed: {str(api_error)}")

            # Fall back to database
            try:
                # Check if email is already taken by another user
                if "email" in user_data:
                    check_query = """
                    SELECT user_id FROM accounts WHERE email = $1 AND user_id != $2
                    """

                    existing = await Database.fetchrow(
                        check_query,
                        user_data["email"],
                        user_id
                    )

                    if existing:
                        return None  # Email already taken by another user

                # Build update query dynamically based on provided fields
                update_fields = []
                params = []
                param_idx = 1

                if "firstname" in user_data:
                    update_fields.append(f"firstname = ${param_idx}")
                    params.append(user_data["firstname"])
                    param_idx += 1

                if "lastname" in user_data:
                    update_fields.append(f"lastname = ${param_idx}")
                    params.append(user_data["lastname"])
                    param_idx += 1

                if "email" in user_data:
                    update_fields.append(f"email = ${param_idx}")
                    params.append(user_data["email"])
                    param_idx += 1

                if "role_id" in user_data:
                    update_fields.append(f"role_id = ${param_idx}")
                    params.append(user_data["role_id"])
                    param_idx += 1

                if "department_id" in user_data:
                    update_fields.append(f"department_id = ${param_idx}")
                    params.append(user_data["department_id"])
                    param_idx += 1

                if "password" in user_data:
                    update_fields.append(f"password = ${param_idx}")
                    params.append(user_data["password"])  # Should be hashed in real app
                    param_idx += 1

                if "is_active" in user_data:
                    update_fields.append(f"is_active = ${param_idx}")
                    params.append(user_data["is_active"])
                    param_idx += 1

                # Add timestamp and user ID
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                params.append(user_id)

                if not update_fields:
                    return await self.get_user(user_id)  # Nothing to update

                # Execute update
                update_query = f"""
                UPDATE accounts 
                SET {", ".join(update_fields[:-1])}
                WHERE user_id = ${param_idx}
                """

                await Database.execute(update_query, *params)

                # Return updated user
                return await self.get_user(user_id)

            except Exception as db_error:
                print(f"Database update user failed: {str(db_error)}")
                return None

    async def delete_user(self, user_id):
        """
        Delete a user

        Args:
            user_id: ID of the user to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try Identity API first
            await self.identity_client.delete_user(user_id)
            return True

        except Exception as api_error:
            print(f"Identity API delete user failed: {str(api_error)}")

            # Fall back to database
            try:
                # Check for related records (assessments, etc.)
                # This is a simplified check - in a real app you'd handle
                # more dependencies or implement cascading delete
                check_query = """
                SELECT 
                    (SELECT COUNT(*) FROM riskassessment WHERE auditor_id = $1) AS assessment_count
                """

                counts = await Database.fetchrow(check_query, user_id)

                # If user has related records, don't allow deletion
                if counts and counts["assessment_count"] > 0:
                    return False

                # Delete user
                delete_query = "DELETE FROM accounts WHERE user_id = $1"
                await Database.execute(delete_query, user_id)

                return True

            except Exception as db_error:
                print(f"Database delete user failed: {str(db_error)}")
                return False

    async def change_password(self, user_id, current_password, new_password):
        """
        Change a user's password

        Args:
            user_id: ID of the user
            current_password: Current password
            new_password: New password

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try Identity API first
            await self.identity_client.change_password(user_id, current_password, new_password)
            return True

        except Exception as api_error:
            print(f"Identity API change password failed: {str(api_error)}")

            # Fall back to database
            try:
                # Verify current password
                verify_query = """
                SELECT user_id FROM accounts 
                WHERE user_id = $1 AND password = $2
                """

                user = await Database.fetchrow(
                    verify_query,
                    user_id,
                    current_password  # Should be hashed in real app
                )

                if not user:
                    return False  # Current password incorrect

                # Update password
                update_query = """
                UPDATE accounts 
                SET password = $1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $2
                """

                await Database.execute(
                    update_query,
                    new_password,  # Should be hashed in real app
                    user_id
                )

                return True

            except Exception as db_error:
                print(f"Database password change failed: {str(db_error)}")
                return False

    async def toggle_user_status(self, user_id):
        """
        Toggle a user's active status

        Args:
            user_id: ID of the user

        Returns:
            Updated User object if successful, None otherwise
        """
        try:
            # Try Identity API first
            updated_user_data = await self.identity_client.toggle_user_status(user_id)
            return User(
                id=updated_user_data.get("id"),
                username=updated_user_data.get("username"),
                name=updated_user_data.get("name"),
                email=updated_user_data.get("email"),
                role=updated_user_data.get("role"),
                department=updated_user_data.get("department")
            )

        except Exception as api_error:
            print(f"Identity API toggle status failed: {str(api_error)}")

            # Fall back to database
            try:
                # Get current status
                current_user = await self.get_user(user_id)
                if not current_user:
                    return None

                # Toggle status
                new_status = not getattr(current_user, 'is_active', True)

                # Update status
                update_query = """
                UPDATE accounts 
                SET is_active = $1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $2
                """

                await Database.execute(update_query, new_status, user_id)

                # Return updated user
                return await self.get_user(user_id)

            except Exception as db_error:
                print(f"Database toggle status failed: {str(db_error)}")
                return None

    async def close(self):
        """Close API connections"""
        try:
            await self.identity_client.close()
        except Exception as e:
            print(f"Error closing API connections: {str(e)}")

    async def get_departments(self):
        """
        Get list of all departments

        Returns:
            List of department objects
        """
        try:
            # Try API first
            response = await self.api_client.get("departments")
            return response.get("departments", [])

        except APIError as e:
            print(f"API get departments failed: {str(e)}")

            # Fall back to database
            try:
                query = """
                SELECT id, name, description
                FROM departments
                ORDER BY name ASC
                """

                rows = await Database.fetch(query)
                return [dict(row) for row in rows]

            except Exception as db_error:
                print(f"Database get departments failed: {str(db_error)}")

                # For development/demo purposes
                return [
                    {"id": 1, "name": "Information Technology", "description": "IT department"},
                    {"id": 2, "name": "Finance", "description": "Finance department"},
                    {"id": 3, "name": "Human Resources", "description": "HR department"},
                    {"id": 4, "name": "Operations", "description": "Operations department"},
                    {"id": 5, "name": "Marketing", "description": "Marketing department"},
                ]
