import logging
import logging.handlers
import os
from datetime import datetime


class ProductionLogger:
    """Structured logging for production environment"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logging()
        return cls._instance
    
    def _init_logging(self):
        """Initialize logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Define log format
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, datefmt=date_format)
        
        # Set up file handler
        log_file = os.path.join(log_dir, f"nda_analyzer_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Store handlers
        self.file_handler = file_handler
        self.console_handler = console_handler
    
    def get_logger(self, name):
        """Get or create a logger with the given name"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            
            # Add handlers if not already present
            if not logger.handlers:
                logger.addHandler(self.file_handler)
                logger.addHandler(self.console_handler)
            
            self._loggers[name] = logger
        
        return self._loggers[name]


# Singleton instance
_logger_instance = ProductionLogger()


def get_logger(module_name):
    """Get a logger instance for a specific module"""
    return _logger_instance.get_logger(module_name)
