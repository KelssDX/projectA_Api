import json
import aiohttp
import asyncio
from src.core.config import API_BASE_URL


class APIError(Exception):
    """Exception raised for API errors"""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error ({status_code}): {message}")


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
        self.session = None

    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

    async def _get_headers(self):
        """Get headers with authentication token if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    async def login(self, username, password):
        """Authenticate with the API and get token"""
        await self._ensure_session()

        try:
            async with self.session.post(
                    f"{self.base_url}/auth/login",
                    json={"username": username, "password": password},
                    headers=await self._get_headers()
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise APIError(response.status, data.get("message", "Authentication failed"))

                # Store the token for future requests
                self.token = data.get("token")
                return data

        except aiohttp.ClientError as e:
            raise APIError(500, f"Connection error: {str(e)}")

    async def get(self, endpoint, params=None):
        """Make GET request to API"""
        await self._ensure_session()

        try:
            async with self.session.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    headers=await self._get_headers()
            ) as response:
                data = await response.json()

                if response.status >= 400:
                    raise APIError(response.status, data.get("message", "API request failed"))

                return data

        except aiohttp.ClientError as e:
            raise APIError(500, f"Connection error: {str(e)}")

    async def post(self, endpoint, data=None):
        """Make POST request to API"""
        await self._ensure_session()

        try:
            async with self.session.post(
                    f"{self.base_url}/{endpoint}",
                    json=data,
                    headers=await self._get_headers()
            ) as response:
                result = await response.json()

                if response.status >= 400:
                    raise APIError(response.status, result.get("message", "API request failed"))

                return result

        except aiohttp.ClientError as e:
            raise APIError(500, f"Connection error: {str(e)}")

    async def put(self, endpoint, data=None):
        """Make PUT request to API"""
        await self._ensure_session()

        try:
            async with self.session.put(
                    f"{self.base_url}/{endpoint}",
                    json=data,
                    headers=await self._get_headers()
            ) as response:
                result = await response.json()

                if response.status >= 400:
                    raise APIError(response.status, result.get("message", "API request failed"))

                return result

        except aiohttp.ClientError as e:
            raise APIError(500, f"Connection error: {str(e)}")

    async def delete(self, endpoint):
        """Make DELETE request to API"""
        await self._ensure_session()

        try:
            async with self.session.delete(
                    f"{self.base_url}/{endpoint}",
                    headers=await self._get_headers()
            ) as response:
                if response.status == 204:  # No content
                    return True

                result = await response.json()

                if response.status >= 400:
                    raise APIError(response.status, result.get("message", "API request failed"))

                return result

        except aiohttp.ClientError as e:
            raise APIError(500, f"Connection error: {str(e)}")

    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
