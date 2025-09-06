import os
import logging
import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    """Logging utility for the risk assessment application."""

    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __init__(self, log_dir="logs", log_level="INFO", max_size_mb=5, backup_count=3):
        """Initialize the logger.

        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_size_mb: Maximum size of log file in MB before rotation
            backup_count: Number of backup log files to keep
        """
        self.log_dir = log_dir
        self.log_level = self.LOG_LEVELS.get(log_level.upper(), logging.INFO)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count

        # Create the logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set up logging
        self.setup_logging()

    def setup_logging(self):
        """Set up the logging configuration."""
        # Create the main application logger
        self.app_logger = logging.getLogger('risk_assessment')
        self.app_logger.setLevel(self.log_level)
        self.app_logger.propagate = False

        # Clear any existing handlers
        if self.app_logger.handlers:
            self.app_logger.handlers.clear()

        # Create app log file name with current date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        app_log_file = os.path.join(self.log_dir, f"app_{today}.log")

        # Create a rotating file handler for the app log
        app_handler = RotatingFileHandler(
            app_log_file,
            maxBytes=self.max_size_bytes,
            backupCount=self.backup_count
        )

        # Create console handler
        console_handler = logging.StreamHandler()

        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set formatter for handlers
        app_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.app_logger.addHandler(app_handler)
        self.app_logger.addHandler(console_handler)

        # Create error logger
        self.error_logger = logging.getLogger('risk_assessment.error')
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.propagate = False

        # Create error log file
        error_log_file = os.path.join(self.log_dir, "error.log")

        # Create a rotating file handler for the error log
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_size_bytes,
            backupCount=self.backup_count
        )
        error_handler.setFormatter(formatter)

        # Add handler to error logger
        self.error_logger.addHandler(error_handler)

        # Create audit logger
        self.audit_logger = logging.getLogger('risk_assessment.audit')
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.propagate = False

        # Create audit log file
        audit_log_file = os.path.join(self.log_dir, "audit.log")

        # Create a rotating file handler for the audit log
        audit_handler = RotatingFileHandler(
            audit_log_file,
            maxBytes=self.max_size_bytes,
            backupCount=self.backup_count
        )

        # Create audit formatter with more information
        audit_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(user)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        audit_handler.setFormatter(audit_formatter)

        # Add handler to audit logger
        self.audit_logger.addHandler(audit_handler)

        # Log that logging has been initialized
        self.info("Logging initialized")

    def debug(self, message):
        """Log a debug message.

        Args:
            message: Message to log
        """
        self.app_logger.debug(message)

    def info(self, message):
        """Log an info message.

        Args:
            message: Message to log
        """
        self.app_logger.info(message)

    def warning(self, message):
        """Log a warning message.

        Args:
            message: Message to log
        """
        self.app_logger.warning(message)

    def error(self, message, exc_info=False):
        """Log an error message.

        Args:
            message: Message to log
            exc_info: Whether to include exception info
        """
        self.app_logger.error(message, exc_info=exc_info)
        self.error_logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=True):
        """Log a critical message.

        Args:
            message: Message to log
            exc_info: Whether to include exception info
        """
        self.app_logger.critical(message, exc_info=exc_info)
        self.error_logger.critical(message, exc_info=exc_info)

    def audit(self, message, user="System"):
        """Log an audit message.

        Args:
            message: Message to log
            user: User who performed the action
        """
        # Create a dictionary with extra fields
        extra = {'user': user}

        # Get the logger
        logger = logging.LoggerAdapter(self.audit_logger, extra)

        # Log the message
        logger.info(message)

    def log_user_activity(self, user, action, details=None):
        """Log user activity for audit purposes.

        Args:
            user: User who performed the action
            action: Description of the action
            details: Additional details (optional)
        """
        if details:
            message = f"{action} - {details}"
        else:
            message = action

        self.audit(message, user=user)

    def log_assessment_activity(self, user, action, assessment_id, details=None):
        """Log assessment activity.

        Args:
            user: User who performed the action
            action: Description of the action
            assessment_id: ID of the assessment
            details: Additional details (optional)
        """
        message = f"Assessment {assessment_id}: {action}"
        if details:
            message += f" - {details}"

        self.audit(message, user=user)

    def log_error(self, error_message, exception=None):
        """Log an error.

        Args:
            error_message: Description of the error
            exception: Exception object (optional)
        """
        if exception:
            self.error(f"{error_message}: {str(exception)}", exc_info=True)
        else:
            self.error(error_message)

    def log_api_call(self, method, endpoint, status_code, user=None):
        """Log API calls.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            status_code: HTTP status code
            user: User who made the request (optional)
        """
        message = f"API {method} {endpoint} - Status {status_code}"

        if user:
            self.audit(message, user=user)
        else:
            self.info(message)


# Create singleton instance
logger = Logger()


# Function to get the logger instance
def get_logger():
    return logger
