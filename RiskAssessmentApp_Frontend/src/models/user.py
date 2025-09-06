class User:
    def __init__(self, id, username, name, email, role, department=None):
        self.id = id
        self.username = username
        self.name = name
        self.email = email
        self.role = role
        self.department = department
        self.token = None  # JWT token for API authentication

    @property
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.role.lower() == "admin"

    @property
    def is_auditor(self):
        """Check if user has auditor privileges"""
        return self.role.lower() in ["admin", "auditor"]

    @classmethod
    def from_json(cls, json_data):
        """Create a User instance from JSON data returned by API"""
        return cls(
            id=json_data.get("id"),
            username=json_data.get("username"),
            name=json_data.get("name"),
            email=json_data.get("email"),
            role=json_data.get("role"),
            department=json_data.get("department")
        )

    def to_json(self):
        """Convert user to JSON for API requests"""
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "department": self.department
        }
