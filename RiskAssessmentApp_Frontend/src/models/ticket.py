from datetime import datetime


class Ticket:
    """
    Model representing a support ticket.
    """

    def __init__(self, id=None, title=None, description=None, status=None,
                 priority=None, user_id=None, user_name=None, assigned_to=None,
                 assigned_to_name=None, comments=None, created_at=None, updated_at=None):
        """
        Initialize a ticket object.

        Args:
            id: Unique identifier for the ticket
            title: Title/summary of the ticket
            description: Detailed description of the issue or request
            status: Current status (Open, In Progress, Resolved, Closed)
            priority: Priority level (Low, Medium, High, Critical)
            user_id: ID of the user who created the ticket
            user_name: Name of the user who created the ticket
            assigned_to: ID of the user assigned to the ticket
            assigned_to_name: Name of the user assigned to the ticket
            comments: List of comments on the ticket
            created_at: Timestamp when the ticket was created
            updated_at: Timestamp when the ticket was last updated
        """
        self.id = id
        self.title = title
        self.description = description
        self.status = status or "Open"
        self.priority = priority or "Medium"
        self.user_id = user_id
        self.user_name = user_name
        self.assigned_to = assigned_to
        self.assigned_to_name = assigned_to_name
        self.comments = comments or []
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_json(cls, json_data):
        """
        Create a Ticket instance from JSON data returned by API.

        Args:
            json_data: Dictionary of ticket data from API

        Returns:
            Ticket: Instance of Ticket class
        """
        # Format ID if numeric (e.g., 1 -> "T-001")
        ticket_id = json_data.get("id")
        if isinstance(ticket_id, int):
            ticket_id = f"T-{ticket_id:03d}"

        # Parse dates if they're strings
        created_at = json_data.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%d")
                except ValueError:
                    pass

        updated_at = json_data.get("updated_at")
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    updated_at = datetime.strptime(updated_at, "%Y-%m-%d")
                except ValueError:
                    pass

        # Extract comments, ensuring consistent format
        comments = json_data.get("comments", [])
        formatted_comments = []

        for comment in comments:
            # Format comment dates
            if isinstance(comment, dict):
                comment_date = comment.get("created_at")
                if isinstance(comment_date, str):
                    try:
                        comment["created_at"] = datetime.strptime(comment_date, "%Y-%m-%d %H:%M:%S").strftime(
                            "%Y-%m-%d")
                    except ValueError:
                        try:
                            comment["created_at"] = datetime.strptime(comment_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                        except ValueError:
                            pass

                formatted_comments.append(comment)

        return cls(
            id=ticket_id,
            title=json_data.get("title"),
            description=json_data.get("description"),
            status=json_data.get("status"),
            priority=json_data.get("priority"),
            user_id=json_data.get("user_id"),
            user_name=json_data.get("user_name"),
            assigned_to=json_data.get("assigned_to"),
            assigned_to_name=json_data.get("assigned_to_name"),
            comments=formatted_comments,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_json(self):
        """
        Convert ticket to JSON for API requests.

        Returns:
            dict: Ticket data as a dictionary
        """
        # Format dates as strings if they're datetime objects
        created_at = self.created_at
        if hasattr(created_at, "strftime"):
            created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

        updated_at = self.updated_at
        if hasattr(updated_at, "strftime"):
            updated_at = updated_at.strftime("%Y-%m-%d %H:%M:%S")

        # Extract numeric ID if it's in "T-001" format
        ticket_id = self.id
        if isinstance(ticket_id, str) and ticket_id.startswith("T-"):
            try:
                ticket_id = int(ticket_id[2:])
            except ValueError:
                pass

        return {
            "id": ticket_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "assigned_to": self.assigned_to,
            "assigned_to_name": self.assigned_to_name,
            "comments": self.comments,
            "created_at": created_at,
            "updated_at": updated_at
        }

    def __str__(self):
        """String representation of the ticket"""
        return f"{self.id}: {self.title} - {self.status} ({self.priority})"

    def add_comment(self, user_id, user_name, text):
        """
        Add a comment to this ticket.

        Args:
            user_id: ID of the user adding the comment
            user_name: Name of the user adding the comment
            text: Comment text

        Returns:
            dict: Created comment
        """
        # Create new comment
        comment = {
            "id": len(self.comments) + 1,  # Simple ID for now
            "user_id": user_id,
            "user": user_name,
            "text": text,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }

        # Add to comments list
        self.comments.append(comment)

        # Update ticket's updated_at timestamp
        self.updated_at = datetime.now()

        return comment

    def change_status(self, new_status):
        """
        Change the status of this ticket.

        Args:
            new_status: New status (Open, In Progress, Resolved, Closed)

        Returns:
            bool: True if status was changed, False otherwise
        """
        valid_statuses = ["Open", "In Progress", "Resolved", "Closed"]

        if new_status not in valid_statuses:
            return False

        if new_status == self.status:
            return False

        self.status = new_status
        self.updated_at = datetime.now()

        return True

    def change_priority(self, new_priority):
        """
        Change the priority of this ticket.

        Args:
            new_priority: New priority (Low, Medium, High, Critical)

        Returns:
            bool: True if priority was changed, False otherwise
        """
        valid_priorities = ["Low", "Medium", "High", "Critical"]

        if new_priority not in valid_priorities:
            return False

        if new_priority == self.priority:
            return False

        self.priority = new_priority
        self.updated_at = datetime.now()

        return True

    def assign(self, user_id, user_name):
        """
        Assign this ticket to a user.

        Args:
            user_id: ID of the user to assign to
            user_name: Name of the user to assign to

        Returns:
            bool: True if assignment was changed, False otherwise
        """
        if self.assigned_to == user_id:
            return False

        self.assigned_to = user_id
        self.assigned_to_name = user_name
        self.updated_at = datetime.now()

        return True

    def unassign(self):
        """
        Remove assignment from this ticket.

        Returns:
            bool: True if unassigned, False if it was already unassigned
        """
        if self.assigned_to is None:
            return False

        self.assigned_to = None
        self.assigned_to_name = None
        self.updated_at = datetime.now()

        return True

    @staticmethod
    async def get_all(api_client, filters=None):
        """
        Get all tickets, optionally filtered.

        Args:
            api_client: API client for making requests
            filters: Optional filters (dict)

        Returns:
            list: List of Ticket objects
        """
        from src.controllers.ticket_controller import TicketController

        controller = TicketController()
        tickets_data = await controller.get_tickets(filters)

        return [Ticket.from_json(t) for t in tickets_data]

    @staticmethod
    async def get_by_id(api_client, ticket_id):
        """
        Get a ticket by ID.

        Args:
            api_client: API client for making requests
            ticket_id: ID of the ticket to retrieve

        Returns:
            Ticket: Ticket object if found, None otherwise
        """
        from src.controllers.ticket_controller import TicketController

        controller = TicketController()
        ticket_data = await controller.get_ticket(ticket_id)

        if ticket_data:
            return Ticket.from_json(ticket_data)

        return None

    @staticmethod
    async def create(api_client, title, description, user_id, priority="Medium"):
        """
        Create a new ticket.

        Args:
            api_client: API client for making requests
            title: Title of the ticket
            description: Description of the issue
            user_id: ID of the user creating the ticket
            priority: Priority of the ticket (default: Medium)

        Returns:
            Ticket: Created Ticket object if successful, None otherwise
        """
        from src.controllers.ticket_controller import TicketController

        controller = TicketController()

        ticket_data = {
            "title": title,
            "description": description,
            "user_id": user_id,
            "priority": priority,
            "status": "Open"
        }

        created_data = await controller.create_ticket(ticket_data)

        if created_data:
            return Ticket.from_json(created_data)

        return None

    async def save(self, api_client):
        """
        Save changes to this ticket.

        Args:
            api_client: API client for making requests

        Returns:
            bool: True if successful, False otherwise
        """
        from src.controllers.ticket_controller import TicketController

        controller = TicketController()
        updated_data = await controller.update_ticket(self.id, self.to_json())

        if updated_data:
            # Update with data from API response
            updated = Ticket.from_json(updated_data)
            self.title = updated.title
            self.description = updated.description
            self.status = updated.status
            self.priority = updated.priority
            self.assigned_to = updated.assigned_to
            self.assigned_to_name = updated.assigned_to_name
            self.updated_at = updated.updated_at
            return True

        return False

    async def delete(self, api_client):
        """
        Delete this ticket.

        Args:
            api_client: API client for making requests

        Returns:
            bool: True if successful, False otherwise
        """
        from src.controllers.ticket_controller import TicketController

        controller = TicketController()
        return await controller.delete_ticket(self.id)

    async def add_comment_api(self, api_client, user_id, comment_text):
        """
        Add a comment to this ticket via API.

        Args:
            api_client: API client for making requests
            user_id: ID of the user adding the comment
            comment_text: Comment text

        Returns:
            dict: Created comment if successful, None otherwise
        """
        from src.controllers.ticket_controller import TicketController

        controller = TicketController()
        comment = await controller.add_comment(self.id, user_id, comment_text)

        if comment:
            # Add comment to our local list
            self.comments.append(comment)
            return comment

        return None

    def get_response_time(self):
        """
        Calculate response time for this ticket.

        Returns:
            dict: Response time data
        """
        if not self.comments:
            return {
                "has_response": False,
                "response_time_hours": None
            }

        # Find first comment that's not from the ticket creator
        first_response = None
        for comment in self.comments:
            if comment.get("user_id") != self.user_id:
                first_response = comment
                break

        if not first_response:
            return {
                "has_response": False,
                "response_time_hours": None
            }

        # Calculate time difference
        if not hasattr(self.created_at, "strftime") or not isinstance(first_response.get("created_at"), str):
            # Can't calculate time difference with the data we have
            return {
                "has_response": True,
                "response_time_hours": None
            }

        # Parse response date
        try:
            response_date = datetime.strptime(first_response["created_at"], "%Y-%m-%d")

            # Calculate difference in hours
            diff = response_date - self.created_at
            hours = diff.total_seconds() / 3600

            return {
                "has_response": True,
                "response_time_hours": round(hours, 1)
            }
        except (ValueError, TypeError):
            return {
                "has_response": True,
                "response_time_hours": None
            }

    def is_within_sla(self, sla_hours=24):
        """
        Check if ticket is/was responded to within the SLA.

        Args:
            sla_hours: SLA time in hours (default: 24)

        Returns:
            bool: True if within SLA, False otherwise, None if can't determine
        """
        response_data = self.get_response_time()

        if not response_data["has_response"]:
            # Check if ticket is still within SLA window
            if not hasattr(self.created_at, "strftime"):
                return None

            now = datetime.now()
            diff = now - self.created_at
            hours = diff.total_seconds() / 3600

            return hours <= sla_hours

        if response_data["response_time_hours"] is None:
            return None

        return response_data["response_time_hours"] <= sla_hours
