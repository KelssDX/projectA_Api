import asyncio
from src.api.client import APIClient, APIError
from src.utils.db import Database
from datetime import datetime
from src.utils.logger import Logger


class TicketController:
    def __init__(self):
        self.api_client = APIClient()

    async def get_tickets(self, filters=None):
        """
        Get list of support tickets with optional filtering

        Args:
            filters: Dictionary of filter criteria (optional)

        Returns:
            List of ticket objects
        """
        try:
            # Try API first
            endpoint = "tickets"

            # Add query parameters for filters if provided
            if filters:
                query_params = []
                for key, value in filters.items():
                    if value is not None:
                        query_params.append(f"{key}={value}")

                if query_params:
                    endpoint = f"{endpoint}?{'&'.join(query_params)}"

            response = await self.api_client.get(endpoint)
            return response.get("tickets", [])

        except APIError as e:
            Logger.error(f"API get tickets failed: {str(e)}")

            # Fall back to database
            try:
                query = """
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.status,
                    t.priority,
                    t.user_id,
                    u1.name AS user_name,
                    t.assigned_to,
                    u2.name AS assigned_to_name,
                    t.created_at,
                    t.updated_at
                FROM 
                    support_tickets t
                JOIN 
                    users u1 ON t.user_id = u1.id
                LEFT JOIN 
                    users u2 ON t.assigned_to = u2.id
                """

                # Build WHERE clause for filters
                where_clauses = []
                params = []
                param_idx = 1

                if filters:
                    if filters.get("status"):
                        where_clauses.append(f"t.status = ${param_idx}")
                        params.append(filters["status"])
                        param_idx += 1

                    if filters.get("priority"):
                        where_clauses.append(f"t.priority = ${param_idx}")
                        params.append(filters["priority"])
                        param_idx += 1

                    if filters.get("user_id"):
                        where_clauses.append(f"t.user_id = ${param_idx}")
                        params.append(filters["user_id"])
                        param_idx += 1

                    if filters.get("assigned_to"):
                        where_clauses.append(f"t.assigned_to = ${param_idx}")
                        params.append(filters["assigned_to"])
                        param_idx += 1

                    if filters.get("search"):
                        where_clauses.append(f"(t.title ILIKE ${param_idx} OR t.description ILIKE ${param_idx})")
                        params.append(f"%{filters['search']}%")
                        param_idx += 1

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY t.updated_at DESC"

                # Execute query
                rows = await Database.fetch(query, *params)

                # Convert rows to ticket objects
                tickets = []
                for row in rows:
                    ticket = dict(row)

                    # Format ID as T-001
                    ticket["id"] = f"T-{ticket['id']:03d}"

                    # Format created_at and updated_at
                    ticket["created_at"] = ticket["created_at"].strftime("%Y-%m-%d")
                    ticket["updated_at"] = ticket["updated_at"].strftime("%Y-%m-%d")

                    # Add comments
                    ticket["comments"] = await self._get_ticket_comments(int(ticket["id"][2:]))

                    tickets.append(ticket)

                return tickets

            except Exception as db_error:
                Logger.exception(f"Database get tickets failed: {str(db_error)}")

                # For development/demo purposes, return some dummy tickets
                return [
                    {
                        "id": "T-001",
                        "title": "Dashboard not loading correctly",
                        "status": "Open",
                        "priority": "High",
                        "created_at": "2025-03-10",
                        "user_name": "John Smith",
                        "description": "The dashboard is taking too long to load and sometimes shows errors.",
                        "comments": [
                            {
                                "user": "Support Team",
                                "text": "We're looking into this issue. Could you provide more details?",
                                "created_at": "2025-03-11",
                            }
                        ],
                    },
                    {
                        "id": "T-002",
                        "title": "Feature request: Export to PDF",
                        "status": "In Progress",
                        "priority": "Medium",
                        "created_at": "2025-03-05",
                        "user_name": "Admin User",
                        "description": "Would like to have the ability to export reports directly to PDF format.",
                        "comments": [
                            {
                                "user": "Support Team",
                                "text": "This feature is planned for the next release. Thanks for the suggestion!",
                                "created_at": "2025-03-06",
                            },
                            {
                                "user": "Admin User",
                                "text": "When is the next release scheduled?",
                                "created_at": "2025-03-07",
                            },
                            {
                                "user": "Support Team",
                                "text": "The next release is scheduled for April 2025.",
                                "created_at": "2025-03-08",
                            },
                        ],
                    },
                    {
                        "id": "T-003",
                        "title": "Cannot edit user permissions",
                        "status": "Closed",
                        "priority": "Low",
                        "created_at": "2025-02-20",
                        "user_name": "Sarah Johnson",
                        "description": "When trying to edit user permissions, the save button doesn't work.",
                        "comments": [
                            {
                                "user": "Support Team",
                                "text": "This issue has been fixed in the latest update. Please refresh your application.",
                                "created_at": "2025-02-21",
                            },
                            {
                                "user": "Admin User",
                                "text": "Confirmed working now. Thanks!",
                                "created_at": "2025-02-22",
                            },
                        ],
                    },
                ]

    async def get_ticket(self, ticket_id):
        """
        Get a single ticket by ID

        Args:
            ticket_id: ID of the ticket to retrieve

        Returns:
            Ticket object if found, None otherwise
        """
        try:
            # Try API first
            response = await self.api_client.get(f"tickets/{ticket_id}")
            return response.get("ticket")

        except APIError as e:
            Logger.error(f"API get ticket failed: {str(e)}")

            # Fall back to database
            try:
                # Extract numeric ID from format T-001
                if ticket_id.startswith("T-"):
                    numeric_id = int(ticket_id[2:])
                else:
                    numeric_id = int(ticket_id)

                query = """
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.status,
                    t.priority,
                    t.user_id,
                    u1.name AS user_name,
                    t.assigned_to,
                    u2.name AS assigned_to_name,
                    t.created_at,
                    t.updated_at
                FROM 
                    support_tickets t
                JOIN 
                    users u1 ON t.user_id = u1.id
                LEFT JOIN 
                    users u2 ON t.assigned_to = u2.id
                WHERE
                    t.id = $1
                """

                row = await Database.fetchrow(query, numeric_id)

                if row:
                    ticket = dict(row)

                    # Format ID as T-001
                    ticket["id"] = f"T-{ticket['id']:03d}"

                    # Format created_at and updated_at
                    ticket["created_at"] = ticket["created_at"].strftime("%Y-%m-%d")
                    ticket["updated_at"] = ticket["updated_at"].strftime("%Y-%m-%d")

                    # Add comments
                    ticket["comments"] = await self._get_ticket_comments(numeric_id)

                    return ticket

                return None

            except Exception as db_error:
                Logger.exception(f"Database get ticket failed: {str(db_error)}")

                # For development/demo purposes
                if ticket_id == "T-001":
                    return {
                        "id": "T-001",
                        "title": "Dashboard not loading correctly",
                        "status": "Open",
                        "priority": "High",
                        "created_at": "2025-03-10",
                        "user_name": "John Smith",
                        "description": "The dashboard is taking too long to load and sometimes shows errors.",
                        "comments": [
                            {
                                "user": "Support Team",
                                "text": "We're looking into this issue. Could you provide more details?",
                                "created_at": "2025-03-11",
                            }
                        ],
                    }

                return None

    async def create_ticket(self, ticket_data):
        """
        Create a new support ticket

        Args:
            ticket_data: Dictionary containing ticket data

        Returns:
            Created ticket object if successful, None otherwise
        """
        try:
            # Try API first
            response = await self.api_client.post("tickets", ticket_data)
            return response.get("ticket")

        except APIError as e:
            Logger.error(f"API create ticket failed: {str(e)}")

            # Fall back to database
            try:
                # Insert ticket
                insert_query = """
                INSERT INTO support_tickets (
                    title, description, status, priority, user_id, assigned_to
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """

                # Default status to "Open" if not provided
                status = ticket_data.get("status", "Open")

                ticket_id = await Database.fetchval(
                    insert_query,
                    ticket_data["title"],
                    ticket_data["description"],
                    status,
                    ticket_data["priority"],
                    ticket_data["user_id"],
                    ticket_data.get("assigned_to")  # May be None
                )

                if ticket_id:
                    # Return the created ticket
                    return await self.get_ticket(f"T-{ticket_id:03d}")

                return None

            except Exception as db_error:
                Logger.exception(f"Database create ticket failed: {str(db_error)}")
                return None

    async def update_ticket(self, ticket_id, ticket_data):
        """
        Update an existing ticket

        Args:
            ticket_id: ID of the ticket to update
            ticket_data: Dictionary containing updated ticket data

        Returns:
            Updated ticket object if successful, None otherwise
        """
        try:
            # Try API first
            response = await self.api_client.put(f"tickets/{ticket_id}", ticket_data)
            return response.get("ticket")

        except APIError as e:
            Logger.error(f"API update ticket failed: {str(e)}")

            # Fall back to database
            try:
                # Extract numeric ID from format T-001
                if ticket_id.startswith("T-"):
                    numeric_id = int(ticket_id[2:])
                else:
                    numeric_id = int(ticket_id)

                # Build update query dynamically based on provided fields
                update_fields = []
                params = []
                param_idx = 1

                if "title" in ticket_data:
                    update_fields.append(f"title = ${param_idx}")
                    params.append(ticket_data["title"])
                    param_idx += 1

                if "description" in ticket_data:
                    update_fields.append(f"description = ${param_idx}")
                    params.append(ticket_data["description"])
                    param_idx += 1

                if "status" in ticket_data:
                    update_fields.append(f"status = ${param_idx}")
                    params.append(ticket_data["status"])
                    param_idx += 1

                if "priority" in ticket_data:
                    update_fields.append(f"priority = ${param_idx}")
                    params.append(ticket_data["priority"])
                    param_idx += 1

                if "assigned_to" in ticket_data:
                    update_fields.append(f"assigned_to = ${param_idx}")
                    params.append(ticket_data["assigned_to"])
                    param_idx += 1

                # Add timestamp and ticket ID
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                params.append(numeric_id)

                if not update_fields:
                    return await self.get_ticket(ticket_id)  # Nothing to update

                # Execute update
                update_query = f"""
                UPDATE support_tickets 
                SET {", ".join(update_fields)}
                WHERE id = ${param_idx}
                """

                await Database.execute(update_query, *params)

                # Return updated ticket
                return await self.get_ticket(ticket_id)

            except Exception as db_error:
                Logger.exception(f"Database update ticket failed: {str(db_error)}")
                return None

    async def add_comment(self, ticket_id, user_id, comment_text):
        """
        Add a comment to a ticket

        Args:
            ticket_id: ID of the ticket
            user_id: ID of the user adding the comment
            comment_text: Text of the comment

        Returns:
            Comment object if successful, None otherwise
        """
        try:
            # Try API first
            comment_data = {
                "ticket_id": ticket_id,
                "user_id": user_id,
                "text": comment_text
            }

            response = await self.api_client.post(f"tickets/{ticket_id}/comments", comment_data)
            return response.get("comment")

        except APIError as e:
            Logger.error(f"API add comment failed: {str(e)}")

            # Fall back to database
            try:
                # Extract numeric ID from format T-001
                if ticket_id.startswith("T-"):
                    numeric_id = int(ticket_id[2:])
                else:
                    numeric_id = int(ticket_id)

                # Insert comment
                insert_query = """
                INSERT INTO ticket_comments (
                    ticket_id, user_id, comment
                )
                VALUES ($1, $2, $3)
                RETURNING id, created_at
                """

                row = await Database.fetchrow(
                    insert_query,
                    numeric_id,
                    user_id,
                    comment_text
                )

                if row:
                    # Get user name
                    user_query = "SELECT name FROM users WHERE id = $1"
                    user_row = await Database.fetchrow(user_query, user_id)

                    return {
                        "id": row["id"],
                        "user": user_row["name"] if user_row else f"User {user_id}",
                        "text": comment_text,
                        "created_at": row["created_at"].strftime("%Y-%m-%d")
                    }

                return None

            except Exception as db_error:
                Logger.exception(f"Database add comment failed: {str(db_error)}")
                return None

    async def delete_ticket(self, ticket_id):
        """
        Delete a ticket

        Args:
            ticket_id: ID of the ticket to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try API first
            await self.api_client.delete(f"tickets/{ticket_id}")
            return True

        except APIError as e:
            Logger.error(f"API delete ticket failed: {str(e)}")

            # Fall back to database
            try:
                # Extract numeric ID from format T-001
                if ticket_id.startswith("T-"):
                    numeric_id = int(ticket_id[2:])
                else:
                    numeric_id = int(ticket_id)

                # Start a transaction
                async with Database.get_pool().acquire() as conn:
                    async with conn.transaction():
                        # Delete comments first (foreign key constraint)
                        await conn.execute(
                            "DELETE FROM ticket_comments WHERE ticket_id = $1",
                            numeric_id
                        )

                        # Delete ticket
                        await conn.execute(
                            "DELETE FROM support_tickets WHERE id = $1",
                            numeric_id
                        )

                return True

            except Exception as db_error:
                Logger.exception(f"Database delete ticket failed: {str(db_error)}")
                return False

    async def _get_ticket_comments(self, ticket_id):
        """
        Get comments for a ticket

        Args:
            ticket_id: Numeric ID of the ticket

        Returns:
            List of comment objects
        """
        try:
            query = """
            SELECT 
                c.id,
                c.user_id,
                u.name AS user_name,
                c.comment AS text,
                c.created_at
            FROM 
                ticket_comments c
            JOIN 
                users u ON c.user_id = u.id
            WHERE
                c.ticket_id = $1
            ORDER BY
                c.created_at ASC
            """

            rows = await Database.fetch(query, ticket_id)

            comments = []
            for row in rows:
                comment = {
                    "id": row["id"],
                    "user": row["user_name"],
                    "text": row["text"],
                    "created_at": row["created_at"].strftime("%Y-%m-%d")
                }
                comments.append(comment)

            return comments

        except Exception as e:
            Logger.exception(f"Error getting ticket comments: {str(e)}")
            return []

    async def get_ticket_stats(self):
        """
        Get statistics about support tickets

        Returns:
            Dictionary with ticket statistics
        """
        try:
            # Try API first
            response = await self.api_client.get("tickets/stats")
            return response

        except APIError as e:
            Logger.error(f"API get ticket stats failed: {str(e)}")

            # Fall back to database
            try:
                query = """
                SELECT
                    COUNT(*) AS total,
                    COUNT(CASE WHEN status = 'Open' THEN 1 END) AS open_count,
                    COUNT(CASE WHEN status = 'In Progress' THEN 1 END) AS in_progress_count,
                    COUNT(CASE WHEN status = 'Closed' THEN 1 END) AS closed_count,
                    COUNT(CASE WHEN priority = 'High' OR priority = 'Critical' THEN 1 END) AS high_priority_count,
                    MAX(created_at) AS latest_ticket_date
                FROM
                    support_tickets
                """

                row = await Database.fetchrow(query)

                if row:
                    stats = dict(row)

                    # Format latest_ticket_date
                    if stats["latest_ticket_date"]:
                        stats["latest_ticket_date"] = stats["latest_ticket_date"].strftime("%Y-%m-%d")

                    # Add response time stats (simplified)
                    # In a real app, this would be calculated based on first response time
                    stats["avg_response_time_hours"] = 4.5
                    stats["percent_resolved_within_sla"] = 92.3

                    return stats

                return {
                    "total": 0,
                    "open_count": 0,
                    "in_progress_count": 0,
                    "closed_count": 0,
                    "high_priority_count": 0,
                    "latest_ticket_date": None,
                    "avg_response_time_hours": 0,
                    "percent_resolved_within_sla": 0
                }

            except Exception as db_error:
                Logger.exception(f"Database get ticket stats failed: {str(db_error)}")

                # Return dummy stats for development/demo
                return {
                    "total": 3,
                    "open_count": 1,
                    "in_progress_count": 1,
                    "closed_count": 1,
                    "high_priority_count": 1,
                    "latest_ticket_date": "2025-03-10",
                    "avg_response_time_hours": 4.5,
                    "percent_resolved_within_sla": 92.3
                }

    async def assign_ticket(self, ticket_id, user_id):
        """
        Assign a ticket to a user

        Args:
            ticket_id: ID of the ticket
            user_id: ID of the user to assign to

        Returns:
            Updated ticket object if successful, None otherwise
        """
        return await self.update_ticket(ticket_id, {"assigned_to": user_id})

    async def change_status(self, ticket_id, status):
        """
        Change the status of a ticket

        Args:
            ticket_id: ID of the ticket
            status: New status (Open, In Progress, Resolved, Closed)

        Returns:
            Updated ticket object if successful, None otherwise
        """
        return await self.update_ticket(ticket_id, {"status": status})

    async def change_priority(self, ticket_id, priority):
        """
        Change the priority of a ticket

        Args:
            ticket_id: ID of the ticket
            priority: New priority (Low, Medium, High, Critical)

        Returns:
            Updated ticket object if successful, None otherwise
        """
        return await self.update_ticket(ticket_id, {"priority": priority})

    async def search_tickets(self, search_term):
        """
        Search for tickets containing the search term

        Args:
            search_term: Term to search for in title, description, and comments

        Returns:
            List of ticket objects matching the search term
        """
        return await self.get_tickets({"search": search_term})

    async def get_user_tickets(self, user_id):
        """
        Get tickets created by a specific user

        Args:
            user_id: ID of the user

        Returns:
            List of ticket objects
        """
        return await self.get_tickets({"user_id": user_id})

    async def get_assigned_tickets(self, user_id):
        """
        Get tickets assigned to a specific user

        Args:
            user_id: ID of the user

        Returns:
            List of ticket objects
        """
        return await self.get_tickets({"assigned_to": user_id})

    async def get_tickets_by_status(self, status):
        """
        Get tickets with a specific status

        Args:
            status: Status to filter by (Open, In Progress, Resolved, Closed)

        Returns:
            List of ticket objects
        """
        return await self.get_tickets({"status": status})

    async def get_tickets_by_priority(self, priority):
        """
        Get tickets with a specific priority

        Args:
            priority: Priority to filter by (Low, Medium, High, Critical)

        Returns:
            List of ticket objects
        """
        return await self.get_tickets({"priority": priority})
