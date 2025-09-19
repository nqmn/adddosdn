#!/usr/bin/env python3
"""
Centralized logging configuration for the AdDDoSDN Dataset Framework.

This module provides standardized logging across all components with consistent
formatting, proper log levels, and configurable output destinations.

Standard Format: YYYY-MM-DD HH:MM:SS,SSS - [COMPONENT] - LEVEL - Message
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import threading
from datetime import datetime

# Thread-local storage for logger instances
_local = threading.local()

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if hasattr(record, 'component'):
            component = f"[{record.component.upper()}]"
        else:
            component = f"[{record.name.upper()}]"
            
        # Create standardized format
        record.component_formatted = component
        
        # Apply color for console output (only if levelname is a plain string)
        if self.COLORS and record.levelname in self.COLORS:
            colored_level = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            colored_component = f"{self.COLORS[record.levelname]}{component}{self.RESET}"
            record.levelname = colored_level
            record.component_formatted = colored_component
        
        return super().format(record)

class StandardizedLogger:
    """Standardized logger factory for consistent logging across the framework."""
    
    # Standard log format
    LOG_FORMAT = "%(asctime)s - %(component_formatted)s - %(levelname)s - %(message)s"
    CONSOLE_FORMAT = "%(asctime)s - %(component_formatted)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    
    @classmethod
    def configure_logging(cls, 
                         log_dir: Optional[Path] = None,
                         console_level: int = logging.INFO,
                         file_level: int = logging.DEBUG,
                         max_file_size: int = 10 * 1024 * 1024,  # 10MB
                         backup_count: int = 5) -> None:
        """Configure global logging settings."""
        
        if cls._configured:
            return
            
        # Set default log directory
        if log_dir is None:
            log_dir = Path.cwd() / "logs"
        
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_formatter = ColoredFormatter(
            cls.CONSOLE_FORMAT,
            datefmt=cls.DATE_FORMAT
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for all logs
        all_log_file = log_dir / "framework.log"
        file_handler = logging.handlers.RotatingFileHandler(
            all_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            cls.LOG_FORMAT.replace('%(component_formatted)s', '[%(name)s]'),
            datefmt=cls.DATE_FORMAT
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, 
                   component: str,
                   log_file: Optional[str] = None,
                   log_dir: Optional[Path] = None) -> logging.Logger:
        """Get or create a standardized logger for a component."""
        
        # Ensure logging is configured
        if not cls._configured:
            cls.configure_logging(log_dir)
        
        logger_key = f"{component}_{log_file or 'default'}"
        
        if logger_key in cls._loggers:
            return cls._loggers[logger_key]
        
        # Create new logger
        logger = logging.getLogger(component)
        logger.setLevel(logging.DEBUG)
        
        # Add component attribute for formatting
        def log_with_component(original_method):
            def wrapper(msg, *args, **kwargs):
                # Create log record with component info
                if logger.isEnabledFor(original_method.__self__.level):
                    record = logger.makeRecord(
                        logger.name, original_method.__self__.level,
                        "", 0, msg, args, None
                    )
                    record.component = component
                    record.component_formatted = f"[{component.upper()}]"
                    logger.handle(record)
            return wrapper
        
        # Override logging methods to include component
        original_debug = logger.debug
        original_info = logger.info
        original_warning = logger.warning
        original_error = logger.error
        original_critical = logger.critical
        
        def debug(msg, *args, **kwargs):
            if logger.isEnabledFor(logging.DEBUG):
                extra = kwargs.get('extra', {})
                extra['component'] = component
                kwargs['extra'] = extra
                original_debug(msg, *args, **kwargs)
        
        def info(msg, *args, **kwargs):
            if logger.isEnabledFor(logging.INFO):
                extra = kwargs.get('extra', {})
                extra['component'] = component
                kwargs['extra'] = extra
                original_info(msg, *args, **kwargs)
        
        def warning(msg, *args, **kwargs):
            if logger.isEnabledFor(logging.WARNING):
                extra = kwargs.get('extra', {})
                extra['component'] = component
                kwargs['extra'] = extra
                original_warning(msg, *args, **kwargs)
        
        def error(msg, *args, **kwargs):
            if logger.isEnabledFor(logging.ERROR):
                extra = kwargs.get('extra', {})
                extra['component'] = component
                kwargs['extra'] = extra
                original_error(msg, *args, **kwargs)
        
        def critical(msg, *args, **kwargs):
            if logger.isEnabledFor(logging.CRITICAL):
                extra = kwargs.get('extra', {})
                extra['component'] = component
                kwargs['extra'] = extra
                original_critical(msg, *args, **kwargs)
        
        logger.debug = debug
        logger.info = info
        logger.warning = warning
        logger.error = error
        logger.critical = critical
        
        # Add component-specific file handler if requested
        if log_file and log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(exist_ok=True)
            
            component_handler = logging.handlers.RotatingFileHandler(
                log_dir / log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=3
            )
            component_handler.setLevel(logging.DEBUG)
            
            component_formatter = logging.Formatter(
                cls.LOG_FORMAT.replace('%(component_formatted)s', f'[{component.upper()}]'),
                datefmt=cls.DATE_FORMAT
            )
            component_handler.setFormatter(component_formatter)
            logger.addHandler(component_handler)
        
        cls._loggers[logger_key] = logger
        return logger

# Convenience functions for common components
def get_main_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Get logger for main application."""
    return StandardizedLogger.get_logger("MAIN", "main.log", log_dir)

def get_attack_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Get logger for attack modules."""
    return StandardizedLogger.get_logger("ATTACK", "attack.log", log_dir)

def get_benign_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Get logger for benign traffic generation."""
    return StandardizedLogger.get_logger("BENIGN", "benign.log", log_dir)

def get_controller_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Get logger for controller operations."""
    return StandardizedLogger.get_logger("CONTROLLER", "ryu.log", log_dir)

def get_mininet_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Get logger for Mininet operations."""
    return StandardizedLogger.get_logger("MININET", "mininet.log", log_dir)

def get_processing_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Get logger for data processing operations."""
    return StandardizedLogger.get_logger("PROCESSING", "processing.log", log_dir)

# Context manager for run-specific logging
class RunContext:
    """Context manager to add run ID to all log messages within a scope."""
    
    def __init__(self, run_id: str, logger: logging.Logger):
        self.run_id = run_id
        self.logger = logger
        self.original_methods = {}
    
    def __enter__(self):
        # Store original methods
        self.original_methods = {
            'debug': self.logger.debug,
            'info': self.logger.info, 
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }
        
        # Create wrapped methods that include run ID
        def create_wrapper(original_method):
            def wrapper(msg, *args, **kwargs):
                prefixed_msg = f"[Run ID: {self.run_id}] {msg}"
                return original_method(prefixed_msg, *args, **kwargs)
            return wrapper
        
        # Replace logger methods
        for level, method in self.original_methods.items():
            setattr(self.logger, level, create_wrapper(method))
        
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods
        for level, method in self.original_methods.items():
            setattr(self.logger, level, method)

def with_run_id(run_id: str, logger: logging.Logger) -> RunContext:
    """Create a context manager that adds run ID to log messages."""
    return RunContext(run_id, logger)

# Console output utilities
class ConsoleOutput:
    """Standardized console output utilities."""
    
    @staticmethod
    def print_header(title: str, width: int = 80) -> None:
        """Print a standardized header."""
        print("\n" + "=" * width)
        print(f" {title.center(width-2)} ")
        print("=" * width)
    
    @staticmethod
    def print_section(title: str, width: int = 60) -> None:
        """Print a section separator."""
        print(f"\n{'-' * width}")
        print(f" {title}")
        print(f"{'-' * width}")
    
    @staticmethod
    def print_status(component: str, status: str, details: str = "") -> None:
        """Print standardized status message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_msg = f"[{timestamp}] [{component.upper()}] {status}"
        if details:
            status_msg += f" - {details}"
        print(status_msg)
    
    @staticmethod
    def print_summary_table(data: Dict[str, Any], title: str = "Summary") -> None:
        """Print a formatted summary table."""
        ConsoleOutput.print_section(title)
        max_key_len = max(len(str(k)) for k in data.keys()) if data else 0
        for key, value in data.items():
            print(f"{str(key).ljust(max_key_len)} : {value}")

# Dataset analysis utilities
def analyze_dataset_summary(output_dir: Path, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Analyze generated dataset and return summary statistics.
    
    Args:
        output_dir: Directory containing generated files
        logger: Optional logger for logging results
    
    Returns:
        Dictionary containing dataset statistics
    """
    summary = {}
    
    try:
        # Analyze packet features CSV if it exists
        csv_file = output_dir / "packet_features.csv"
        if csv_file.exists():
            # Read CSV and count by class (using shell commands for efficiency)
            import subprocess
            
            # Count multi-class distribution
            try:
                result = subprocess.run(
                    f"tail -n +2 '{csv_file}' | cut -d',' -f31 | sort | uniq -c",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                )
                if result.returncode == 0:
                    class_counts = {}
                    total_packets = 0
                    for line in result.stdout.strip().split('\n'):
                        if not line.strip():
                            continue
                        parts = line.strip().split()
                        if len(parts) < 2:
                            # Skip malformed lines (e.g., missing class name)
                            continue
                        try:
                            count = int(parts[0])
                        except ValueError:
                            continue
                        class_name = parts[1]
                        class_counts[class_name] = count
                        total_packets += count
                    summary['multi_class'] = class_counts
                    summary['total_packets'] = total_packets
            except Exception as e:
                if logger:
                    logger.warning(f"Could not analyze multi-class distribution: {e}")
            
            # Count binary classification
            try:
                result = subprocess.run(
                    f"tail -n +2 '{csv_file}' | cut -d',' -f32 | sort | uniq -c",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                )
                if result.returncode == 0:
                    binary_counts = {}
                    for line in result.stdout.strip().split('\n'):
                        if not line.strip():
                            continue
                        parts = line.strip().split()
                        if len(parts) < 2:
                            # Skip malformed lines (e.g., missing label value)
                            continue
                        try:
                            count = int(parts[0])
                        except ValueError:
                            continue
                        label_value = parts[1]
                        label = 'benign' if label_value == '0' else 'attack'
                        binary_counts[label] = count
                    summary['binary_class'] = binary_counts
            except Exception as e:
                if logger:
                    logger.warning(f"Could not analyze binary classification: {e}")
        
        # Analyze PCAP files
        pcap_files = list(output_dir.glob("*.pcap"))
        if pcap_files:
            pcap_stats = {}
            for pcap_file in pcap_files:
                try:
                    # Use capinfos for accurate packet count
                    result = subprocess.run(
                        ["capinfos", "-c", str(pcap_file)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                    )
                    if result.returncode == 0 and "Number of packets:" in result.stdout:
                        # Extract packet count from capinfos output
                        for line in result.stdout.split('\n'):
                            if "Number of packets:" in line:
                                count = int(line.split(':')[1].strip())
                                pcap_stats[pcap_file.name] = count
                                break
                    else:
                        # Try tshark as fallback
                        result = subprocess.run(
                            ["tshark", "-r", str(pcap_file), "-q", "-z", "io,stat,0"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                        )
                        if result.returncode == 0:
                            # Parse tshark output for packet count
                            lines = result.stdout.split('\n')
                            for line in lines:
                                if 'Frames' in line and '|' in line:
                                    parts = line.split('|')
                                    if len(parts) >= 2:
                                        count = int(parts[1].strip())
                                        pcap_stats[pcap_file.name] = count
                                        break
                        else:
                            # Final fallback: use file size
                            pcap_stats[pcap_file.name] = f"{pcap_file.stat().st_size} bytes"
                            
                except Exception:
                    # Fallback: use file size as rough estimate
                    pcap_stats[pcap_file.name] = f"{pcap_file.stat().st_size} bytes"
            
            summary['pcap_files'] = pcap_stats
        
        return summary
        
    except Exception as e:
        if logger:
            logger.error(f"Error analyzing dataset: {e}")
        return {'error': str(e)}

def print_dataset_summary(output_dir: Path, logger: Optional[logging.Logger] = None) -> None:
    """
    Print comprehensive dataset summary to console and log.
    
    Args:
        output_dir: Directory containing generated files
        logger: Optional logger for logging results
    """
    summary = analyze_dataset_summary(output_dir, logger)
    
    if 'error' in summary:
        print(f"Error generating dataset summary: {summary['error']}")
        if logger:
            logger.error(f"Dataset summary generation failed: {summary['error']}")
        return
    
    # Console output
    ConsoleOutput.print_header("Dataset Generation Summary")
    
    if 'multi_class' in summary:
        ConsoleOutput.print_section("Multi-class Distribution")
        total = summary.get('total_packets', 0)
        for class_name, count in sorted(summary['multi_class'].items()):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{class_name.ljust(15)} : {count:,} packets ({percentage:.1f}%)")
        print(f"{'Total'.ljust(15)} : {total:,} packets")
    
    if 'binary_class' in summary:
        ConsoleOutput.print_section("Binary Classification")
        total_binary = sum(summary['binary_class'].values())
        for label, count in summary['binary_class'].items():
            percentage = (count / total_binary * 100) if total_binary > 0 else 0
            print(f"{label.capitalize().ljust(15)} : {count:,} packets ({percentage:.1f}%)")
    
    if 'pcap_files' in summary:
        ConsoleOutput.print_section("PCAP Files Generated")
        for filename, count in sorted(summary['pcap_files'].items()):
            if isinstance(count, int):
                print(f"{filename.ljust(20)} : {count:,} raw packets")
            else:
                print(f"{filename.ljust(20)} : {count}")
    
    # Log a simple completion message
    if logger:
        logger.info("Dataset generation summary displayed above")

# Initialize logging when module is imported
def initialize_logging(log_dir: Optional[Path] = None, 
                      console_level: int = logging.INFO) -> None:
    """Initialize the logging system with default configuration."""
    StandardizedLogger.configure_logging(
        log_dir=log_dir,
        console_level=console_level
    )

# Auto-initialize with sensible defaults
if not StandardizedLogger._configured:
    initialize_logging()
