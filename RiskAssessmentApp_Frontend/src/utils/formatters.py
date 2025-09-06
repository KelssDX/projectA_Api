from datetime import datetime, date
import locale


def format_date(date_obj, format_type="default"):
    """
    Format date objects for display
    
    Args:
        date_obj: datetime, date, or string
        format_type: 'default', 'short', 'long', 'iso'
    
    Returns:
        Formatted date string
    """
    if not date_obj:
        return "N/A"
    
    # Convert string to datetime if needed
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except ValueError:
            return date_obj  # Return as-is if can't parse
    
    # Convert date to datetime for consistent handling
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())
    
    if format_type == "short":
        return date_obj.strftime("%m/%d/%Y")
    elif format_type == "long":
        return date_obj.strftime("%B %d, %Y")
    elif format_type == "iso":
        return date_obj.strftime("%Y-%m-%d")
    elif format_type == "datetime":
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    else:  # default
        return date_obj.strftime("%Y-%m-%d")


def format_currency(amount, currency="USD"):
    """
    Format currency amounts
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: USD)
    
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    try:
        # Try to set locale for proper currency formatting
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            pass  # Fall back to manual formatting
        
        amount = float(amount)
        
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        else:
            return f"{currency} {amount:,.2f}"
            
    except (ValueError, TypeError):
        return str(amount)


def format_percentage(value, decimal_places=1):
    """
    Format percentage values
    
    Args:
        value: Numeric value (0-1 or 0-100)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        
        # If value is between 0 and 1, assume it's a decimal percentage
        if 0 <= value <= 1:
            value *= 100
        
        return f"{value:.{decimal_places}f}%"
        
    except (ValueError, TypeError):
        return str(value)


def format_risk_score(score):
    """
    Format risk scores with appropriate styling
    
    Args:
        score: Numeric risk score
    
    Returns:
        Formatted risk score string
    """
    if score is None:
        return "N/A"
    
    try:
        score = float(score)
        return f"{score:.1f}"
    except (ValueError, TypeError):
        return str(score)


def format_file_size(size_bytes):
    """
    Format file sizes in human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted file size string
    """
    if size_bytes is None:
        return "N/A"
    
    try:
        size_bytes = int(size_bytes)
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
        
    except (ValueError, TypeError):
        return str(size_bytes)


def format_duration(start_time, end_time=None):
    """
    Format duration between two times
    
    Args:
        start_time: Start datetime
        end_time: End datetime (default: now)
    
    Returns:
        Formatted duration string
    """
    if not start_time:
        return "N/A"
    
    if isinstance(start_time, str):
        try:
            start_time = datetime.fromisoformat(start_time)
        except ValueError:
            return "Invalid date"
    
    if end_time is None:
        end_time = datetime.now()
    elif isinstance(end_time, str):
        try:
            end_time = datetime.fromisoformat(end_time)
        except ValueError:
            return "Invalid date"
    
    duration = end_time - start_time
    
    if duration.days > 0:
        return f"{duration.days} days"
    elif duration.seconds > 3600:
        hours = duration.seconds // 3600
        return f"{hours} hours"
    elif duration.seconds > 60:
        minutes = duration.seconds // 60
        return f"{minutes} minutes"
    else:
        return f"{duration.seconds} seconds"


def format_phone_number(phone):
    """
    Format phone numbers
    
    Args:
        phone: Phone number string
    
    Returns:
        Formatted phone number
    """
    if not phone:
        return "N/A"
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, str(phone)))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return as-is if can't format


def format_assessment_id(assessment_id):
    """
    Format assessment IDs with consistent prefix
    
    Args:
        assessment_id: Assessment ID (numeric or string)
    
    Returns:
        Formatted assessment ID
    """
    if not assessment_id:
        return "N/A"
    
    try:
        # If it's already formatted, return as-is
        if isinstance(assessment_id, str) and assessment_id.startswith('A-'):
            return assessment_id
        
        # Convert to number and format
        num_id = int(assessment_id)
        return f"A-{num_id:03d}"
        
    except (ValueError, TypeError):
        return str(assessment_id)


def format_status(status):
    """
    Format status strings with proper capitalization
    
    Args:
        status: Status string
    
    Returns:
        Formatted status string
    """
    if not status:
        return "Unknown"
    
    # Convert underscores to spaces and capitalize each word
    formatted = str(status).replace('_', ' ').title()
    
    # Handle special cases
    status_mapping = {
        'In Progress': 'In Progress',
        'Not Started': 'Not Started',
        'On Hold': 'On Hold',
        'Cancelled': 'Cancelled',
        'Completed': 'Completed'
    }
    
    return status_mapping.get(formatted, formatted)


def truncate_text(text, max_length=50, suffix="..."):
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_list(items, separator=", ", max_items=3):
    """
    Format a list of items for display
    
    Args:
        items: List of items
        separator: Separator between items
        max_items: Maximum items to show before truncating
    
    Returns:
        Formatted list string
    """
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return separator.join(str(item) for item in items)
    else:
        visible_items = items[:max_items]
        remaining = len(items) - max_items
        return separator.join(str(item) for item in visible_items) + f" and {remaining} more"


def format_priority(priority):
    """
    Format priority levels with appropriate styling
    
    Args:
        priority: Priority level (string or number)
    
    Returns:
        Formatted priority string
    """
    if not priority:
        return "Normal"
    
    priority_mapping = {
        1: "Low",
        2: "Normal", 
        3: "High",
        4: "Critical",
        5: "Emergency",
        "low": "Low",
        "normal": "Normal",
        "medium": "Normal",
        "high": "High",
        "critical": "Critical",
        "emergency": "Emergency"
    }
    
    if isinstance(priority, (int, float)):
        return priority_mapping.get(int(priority), "Normal")
    else:
        return priority_mapping.get(str(priority).lower(), str(priority).title())


def format_compliance_percentage(compliant_count, total_count):
    """
    Calculate and format compliance percentage
    
    Args:
        compliant_count: Number of compliant items
        total_count: Total number of items
    
    Returns:
        Formatted compliance percentage
    """
    if not total_count or total_count == 0:
        return "N/A"
    
    try:
        percentage = (compliant_count / total_count) * 100
        return f"{percentage:.1f}% ({compliant_count}/{total_count})"
    except (ValueError, TypeError, ZeroDivisionError):
        return "N/A"


def format_time_ago(timestamp):
    """
    Format timestamp as "time ago" string
    
    Args:
        timestamp: datetime object or string
    
    Returns:
        Formatted "time ago" string
    """
    if not timestamp:
        return "Unknown"
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return "Invalid date"
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now" 
