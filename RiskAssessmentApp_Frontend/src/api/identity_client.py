import aiohttp
import json
from src.core.config import API_CONFIG, get_identity_api_url


class IdentityAPIClient:
    """Client for interacting with the Affina.Identity.API"""
    
    def __init__(self):
        self.base_url = API_CONFIG["identity_api"]
        self.timeout = API_CONFIG["timeout"]
        self.verify_ssl = API_CONFIG["verify_ssl"]
        self.session = None
    
    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
    
    async def login(self, email, password):
        """
        Authenticate user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            dict: User data if successful
            
        Raises:
            Exception: If authentication fails
        """
        await self._ensure_session()
        
        # Build the URL with query parameters (as per the backend API)
        url = get_identity_api_url("login")
        params = {
            "email": email,
            "password": password
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return user_data
                elif response.status == 400:
                    error_message = await response.text()
                    raise Exception(f"Invalid credentials: {error_message}")
                else:
                    raise Exception(f"Authentication failed with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid response format from server")
    
    async def get_users(self):
        """
        Get all users
        
        Returns:
            list: List of user data
            
        Raises:
            Exception: If request fails
        """
        await self._ensure_session()
        url = get_identity_api_url("get_users")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    users_data = await response.json()
                    return users_data
                else:
                    raise Exception(f"Failed to get users with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_user(self, user_id):
        """
        Get a specific user by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            dict: User data if successful
            
        Raises:
            Exception: If request fails
        """
        await self._ensure_session()
        url = get_identity_api_url("get_user").replace("{id}", str(user_id))
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return user_data
                elif response.status == 404:
                    raise Exception(f"User with ID {user_id} not found")
                else:
                    raise Exception(f"Failed to get user with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def create_user(self, user_data):
        """
        Create a new user
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            dict: Created user data if successful
            
        Raises:
            Exception: If creation fails
        """
        await self._ensure_session()
        url = get_identity_api_url("create_user")
        
        try:
            async with self.session.post(url, json=user_data) as response:
                if response.status == 201:
                    created_user = await response.json()
                    return created_user
                elif response.status == 400:
                    error_message = await response.text()
                    raise Exception(f"Bad request: {error_message}")
                else:
                    raise Exception(f"Failed to create user with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def update_user(self, user_id, user_data):
        """
        Update an existing user
        
        Args:
            user_id: User's ID
            user_data: Dictionary containing updated user information
            
        Returns:
            dict: Updated user data if successful
            
        Raises:
            Exception: If update fails
        """
        await self._ensure_session()
        url = get_identity_api_url("update_user").replace("{id}", str(user_id))
        
        try:
            async with self.session.put(url, json=user_data) as response:
                if response.status == 200:
                    updated_user = await response.json()
                    return updated_user
                elif response.status == 404:
                    raise Exception(f"User with ID {user_id} not found")
                elif response.status == 400:
                    error_message = await response.text()
                    raise Exception(f"Bad request: {error_message}")
                else:
                    raise Exception(f"Failed to update user with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def delete_user(self, user_id):
        """
        Delete a user
        
        Args:
            user_id: User's ID
            
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If deletion fails
        """
        await self._ensure_session()
        url = get_identity_api_url("delete_user").replace("{id}", str(user_id))
        
        try:
            async with self.session.delete(url) as response:
                if response.status == 204:
                    return True
                elif response.status == 404:
                    raise Exception(f"User with ID {user_id} not found")
                else:
                    raise Exception(f"Failed to delete user with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def change_password(self, user_id, current_password, new_password):
        """
        Change a user's password
        
        Args:
            user_id: User's ID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If password change fails
        """
        await self._ensure_session()
        url = get_identity_api_url("change_password").replace("{id}", str(user_id))
        
        password_data = {
            "currentPassword": current_password,
            "newPassword": new_password
        }
        
        try:
            async with self.session.post(url, json=password_data) as response:
                if response.status == 200:
                    return True
                elif response.status == 404:
                    raise Exception(f"User with ID {user_id} not found")
                elif response.status == 400:
                    error_message = await response.text()
                    raise Exception(f"Password change failed: {error_message}")
                else:
                    raise Exception(f"Failed to change password with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def toggle_user_status(self, user_id):
        """
        Toggle a user's active status
        
        Args:
            user_id: User's ID
            
        Returns:
            dict: Updated user data if successful
            
        Raises:
            Exception: If status toggle fails
        """
        await self._ensure_session()
        url = get_identity_api_url("toggle_user_status").replace("{id}", str(user_id))
        
        try:
            async with self.session.post(url) as response:
                if response.status == 200:
                    updated_user = await response.json()
                    return updated_user
                elif response.status == 404:
                    raise Exception(f"User with ID {user_id} not found")
                else:
                    raise Exception(f"Failed to toggle user status with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_users_by_role(self, role):
        """
        Get users by role
        
        Args:
            role: Role name
            
        Returns:
            list: List of user data
            
        Raises:
            Exception: If request fails
        """
        await self._ensure_session()
        url = get_identity_api_url("get_users_by_role").replace("{role}", str(role))
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    users_data = await response.json()
                    return users_data
                else:
                    raise Exception(f"Failed to get users by role with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_users_by_department(self, department_id):
        """
        Get users by department
        
        Args:
            department_id: Department ID
            
        Returns:
            list: List of user data
            
        Raises:
            Exception: If request fails
        """
        await self._ensure_session()
        url = get_identity_api_url("get_users_by_department").replace("{departmentId}", str(department_id))
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    users_data = await response.json()
                    return users_data
                else:
                    raise Exception(f"Failed to get users by department with status {response.status}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close() 
