import asyncio
from src.api.identity_client import IdentityAPIClient
from src.models.user import User
from src.utils.db import Database


class AuthController:
    def __init__(self):
        self.identity_client = IdentityAPIClient()
        self.current_user = None

    async def login(self, email, password):
        """
        Authenticate a user with the provided credentials

        This method tries to authenticate with the Identity API first,
        and falls back to local database authentication if API is unavailable.

        Args:
            email: The user's email address
            password: The user's password

        Returns:
            User: User object if authentication successful, None otherwise
        """
        try:
            # Try Identity API authentication first
            user_data = await self.identity_client.login(email, password)

            # Enrich with full user profile (roles/department) from API/DB
            user_id = user_data.get("id") or user_data.get("Id")
            full_profile = None
            try:
                if user_id is not None:
                    full_profile = await self.identity_client.get_user(user_id)
            except Exception:
                full_profile = None

            # Resolve role using multiple candidates from API profile
            role_candidates = [
                user_data.get("role"),
                user_data.get("userType"),
                (full_profile.get("role") if isinstance(full_profile, dict) else None),
                (full_profile.get("userType") if isinstance(full_profile, dict) else None),
            ]
            # roles array support
            if isinstance(full_profile, dict) and isinstance(full_profile.get("roles"), list) and full_profile.get("roles"):
                first_role = full_profile.get("roles")[0]
                if isinstance(first_role, dict):
                    role_candidates.append(first_role.get("name") or first_role.get("Name"))
                elif isinstance(first_role, str):
                    role_candidates.append(first_role)

            resolved_role = next((r for r in role_candidates if r), "user")

            # Resolve department name/id
            department_value = None
            if isinstance(full_profile, dict):
                department_value = full_profile.get("department") or full_profile.get("department_name") \
                    or full_profile.get("Department") or full_profile.get("DepartmentName")
            if department_value is None:
                department_value = user_data.get("department")

            # Create user from API response (+ enrichment)
            self.current_user = User(
                id=user_id,
                username=user_data.get("username") or email,
                name=user_data.get("name") or email,
                email=user_data.get("email") or email,
                role=resolved_role,
                department=department_value
            )

            return self.current_user

        except Exception as e:
            # Surface API error to UI; do not fall back to DB
            raise

            # # Fall back to database authentication
            # try:
            #     # In a real app, you'd hash the password before comparing
            #     query = """
            #     SELECT id, username, name, email, role, department_id
            #     FROM users
            #     WHERE email = $1 AND password_hash = $2
            #     """

            #     user_row = await Database.fetchrow(query, email, password)

            #     if user_row:
            #         # Get department name if department_id is present
            #         department = None
            #         if user_row["department_id"]:
            #             dept_query = "SELECT name FROM departments WHERE id = $1"
            #             dept = await Database.fetchrow(dept_query, user_row["department_id"])
            #             if dept:
            #                 department = dept["name"]

            #         # Create user from database row
            #         self.current_user = User(
            #             id=user_row["id"],
            #             username=user_row["username"],
            #             name=user_row["name"],
            #             email=user_row["email"],
            #             role=user_row["role"],
            #             department=department
            #         )

            #         return self.current_user

            #     return None

            # except Exception as db_error:
            #     print(f"Database authentication failed: {str(db_error)}")

            #     # For development/demo purposes, allow a hardcoded admin user
            #     if email == "admin@example.com" and password == "admin":
            #         self.current_user = User(
            #             id=1,
            #             username="admin",
            #             name="Admin User",
            #             email="admin@example.com",
            #             role="admin"
            #         )
            #         return self.current_user

            return None

    async def logout(self):
        """
        Log out the current user

        This clears the current user and closes API connections.
        """
        # Clear current user
        self.current_user = None
        
        # Close API client connections
        try:
            await self.identity_client.close()
        except Exception as e:
            print(f"Error closing API connections: {str(e)}")

    async def register(self, username, password, name, email, role="user", department_id=None):
        """
        Register a new user

        Note: The current Identity API doesn't have a registration endpoint,
        so this falls back to database registration only.

        Args:
            username: Desired username
            password: User's password
            name: User's full name
            email: User's email
            role: User's role (default: "user")
            department_id: ID of user's department (optional)

        Returns:
            User: Newly created user object if successful, None otherwise
        """
        try:
            # Database registration (Identity API doesn't have registration endpoint)
            # TODO: Implement registration via Identity API when endpoint becomes available
            print("Registration not available - Identity API doesn't have registration endpoint")
            return None
            
            # # Check if username or email already exists
            # check_query = """
            # SELECT id FROM users WHERE username = $1 OR email = $2
            # """
            # existing = await Database.fetchrow(check_query, username, email)

            # if existing:
            #     return None  # Username or email already taken

            # # Insert new user
            # insert_query = """
            # INSERT INTO users (username, password_hash, name, email, role, department_id)
            # VALUES ($1, $2, $3, $4, $5, $6)
            # RETURNING id
            # """

            # user_id = await Database.fetchval(
            #     insert_query,
            #     username,
            #     password,  # Should be hashed in real app
            #     name,
            #     email,
            #     role,
            #     department_id
            # )

            # if user_id:
            #     # Get department name if department_id is present
            #     department = None
            #     if department_id:
            #         dept_query = "SELECT name FROM departments WHERE id = $1"
            #         dept = await Database.fetchrow(dept_query, department_id)
            #         if dept:
            #             department = dept["name"]

            #     # Create user object
            #     new_user = User(
            #         id=user_id,
            #         username=username,
            #         name=name,
            #         email=email,
            #         role=role,
            #         department=department
            #     )

            #     return new_user

            # return None

        except Exception as db_error:
            print(f"Database registration failed: {str(db_error)}")
            return None

    async def change_password(self, user_id, current_password, new_password):
        """
        Change a user's password

        Note: The current Identity API doesn't have a change password endpoint,
        so this falls back to database operation only.

        Args:
            user_id: ID of the user
            current_password: User's current password
            new_password: New password

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Database password change (Identity API doesn't have this endpoint)
            # TODO: Implement password change via Identity API when endpoint becomes available
            print("Password change not available - Identity API doesn't have password change endpoint")
            return False
            
            # # Verify current password
            # verify_query = """
            # SELECT id FROM users 
            # WHERE id = $1 AND password_hash = $2
            # """

            # user = await Database.fetchrow(
            #     verify_query,
            #     user_id,
            #     current_password  # Should be hashed in real app
            # )

            # if not user:
            #     return False  # Current password incorrect

            # # Update password
            # update_query = """
            # UPDATE users 
            # SET password_hash = $1, updated_at = CURRENT_TIMESTAMP
            # WHERE id = $2
            # """

            # await Database.execute(
            #     update_query,
            #     new_password,  # Should be hashed in real app
            #     user_id
            # )

            # return True

        except Exception as db_error:
            print(f"Database password change failed: {str(db_error)}")
            return False

    def get_current_user(self):
        """Get the currently authenticated user"""
        return self.current_user

    def is_authenticated(self):
        """Check if a user is currently authenticated"""
        return self.current_user is not None

    async def close(self):
        """Close API connections"""
        try:
            await self.identity_client.close()
        except Exception as e:
            print(f"Error closing API connections: {str(e)}")
