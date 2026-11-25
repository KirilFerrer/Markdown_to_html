import os
from datetime import datetime


LOG_FILE_HANDLE = None
CURRENT_LOG_FILE = None

# Determine project root (parent of src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_directories_exist():
    """Create the output and log directories if they do not exist."""
    directories = [
        os.path.join(PROJECT_ROOT, "AST_GEN"),
        os.path.join(PROJECT_ROOT, "HTML_GEN"),
        os.path.join(PROJECT_ROOT, "logs")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


def get_log_timestamp():
    """Return a timestamp for log file entries."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_short_timestamp():
    """Return a short timestamp for console messages."""
    return datetime.now().strftime("%H:%M:%S")


def create_log_file(log_dir=None):
    """Return the path to the daily log file."""
    if log_dir is None:
        log_dir = os.path.join(PROJECT_ROOT, "logs")
        
    ensure_directories_exist()
    
    date_str = datetime.now().strftime("%Y%m%d")
    log_filename = f"conversion_{date_str}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    return log_filepath


def initialize_logging_system(log_dir=None):
    """Open the log file and return its path."""
    global LOG_FILE_HANDLE, CURRENT_LOG_FILE

    if LOG_FILE_HANDLE and not LOG_FILE_HANDLE.closed:
        return CURRENT_LOG_FILE

    if log_dir is None:
        log_dir = os.path.join(PROJECT_ROOT, "logs")
        
    ensure_directories_exist()
    CURRENT_LOG_FILE = create_log_file(log_dir)
    
    LOG_FILE_HANDLE = open(CURRENT_LOG_FILE, "a", encoding="utf-8")
    
    # Start a new log session.
    separator = "\n" + "="*80 + "\n"
    session_start = f"SESSION STARTED: {get_log_timestamp()}\n"
    LOG_FILE_HANDLE.write(separator)
    LOG_FILE_HANDLE.write(session_start)
    LOG_FILE_HANDLE.write("="*80 + "\n\n")
    LOG_FILE_HANDLE.flush()
    
    return CURRENT_LOG_FILE


def close_logging_system():
    """Close the active log file."""
    global LOG_FILE_HANDLE
    
    if LOG_FILE_HANDLE:
        separator = "\n" + "="*80 + "\n"
        session_end = f"SESSION ENDED: {get_log_timestamp()}\n"
        LOG_FILE_HANDLE.write(separator)
        LOG_FILE_HANDLE.write(session_end)
        LOG_FILE_HANDLE.write("="*80 + "\n\n")
        LOG_FILE_HANDLE.flush()
        LOG_FILE_HANDLE.close()
        LOG_FILE_HANDLE = None


def write_log_to_file(level, stage, message, function_name=None, line_number=None):
    """Write a log entry to the active file.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        stage: Pipeline stage, such as LEXER, PARSER, VALIDATOR or RENDERER.
        message: Log message.
        function_name: Name of the calling function, if supplied.
        line_number: Source line number, if supplied.
    """
    global LOG_FILE_HANDLE
    
    if not LOG_FILE_HANDLE:
        initialize_logging_system()
    
    timestamp = get_log_timestamp()
    
    log_parts = [timestamp, level.ljust(8), stage.ljust(12)]
    
    if function_name:
        log_parts.append(f"{function_name}:")
    
    if line_number:
        log_parts.append(f"L{line_number}")
    
    log_parts.append(message)
    
    log_line = " | ".join(log_parts) + "\n"
    
    LOG_FILE_HANDLE.write(log_line)
    LOG_FILE_HANDLE.flush()


def format_console_log(level, stage, message):
    """Format a short log message for the UI console.
    
    Args:
        level: Log level.
        stage: Pipeline stage.
        message: Message to display.
    
    Returns:
        str: Formatted console message.
    """
    timestamp = get_short_timestamp()
    
    if level == "ERROR" or level == "CRITICAL":
        return f"[{timestamp}] [{stage}] ERROR: {message}"
    elif level == "WARNING":
        return f"[{timestamp}] [{stage}] WARNING: {message}"
    else:
        return f"[{timestamp}] [{stage}] {message}"


def log_info(stage, message, function_name=None, line_number=None):
    """Log an informational message."""
    write_log_to_file("INFO", stage, message, function_name, line_number)
    return format_console_log("INFO", stage, message)


def log_debug(stage, message, function_name=None, line_number=None):
    """Log a debug message."""
    write_log_to_file("DEBUG", stage, message, function_name, line_number)
    return format_console_log("DEBUG", stage, message)


def log_warning(stage, message, function_name=None, line_number=None):
    """Log a warning."""
    write_log_to_file("WARNING", stage, message, function_name, line_number)
    return format_console_log("WARNING", stage, message)


def log_error(stage, message, function_name=None, line_number=None):
    """Log an error."""
    write_log_to_file("ERROR", stage, message, function_name, line_number)
    return format_console_log("ERROR", stage, message)


def log_critical(stage, message, function_name=None, line_number=None):
    """Log a critical error."""
    write_log_to_file("CRITICAL", stage, message, function_name, line_number)
    return format_console_log("CRITICAL", stage, message)


def log_pipeline_start(filename):
    """Log the start of a conversion."""
    message = f"Starting conversion pipeline for file: {filename}"
    write_log_to_file("INFO", "PIPELINE", message)
    return format_console_log("INFO", "PIPELINE", f"Starting conversion: {os.path.basename(filename)}")


def log_pipeline_end(success=True):
    """Log the result of a conversion."""
    if success:
        message = "Conversion pipeline completed successfully"
        write_log_to_file("INFO", "PIPELINE", message)
        return format_console_log("INFO", "PIPELINE", "Conversion completed successfully")
    else:
        message = "Conversion pipeline failed"
        write_log_to_file("ERROR", "PIPELINE", message)
        return format_console_log("ERROR", "PIPELINE", "Conversion failed")
