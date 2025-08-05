import os
import logging
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)

class LangGraphLogger:
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOGS_DIR / f"langgraph_{chat_id}_{self.session_id}.txt"
        
        # Setup logger
        self.logger = logging.getLogger(f"langgraph_{chat_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_node_start(self, node_name: str, input_data: Dict[str, Any]):
        """Log the start of a node execution"""
        self.logger.info(f"=== Starting Node: {node_name} ===")
        self.logger.debug(f"Input data: {json.dumps(input_data, indent=2, default=str)}")
    
    def log_node_end(self, node_name: str, output_data: Dict[str, Any]):
        """Log the end of a node execution"""
        self.logger.info(f"=== Completed Node: {node_name} ===")
        self.logger.debug(f"Output data: {json.dumps(output_data, indent=2, default=str)}")
    
    def log_intermediate_result(self, step_name: str, data: Any, details: str = ""):
        """Log intermediate results within a node"""
        self.logger.info(f"Intermediate result - {step_name}: {details}")
        if isinstance(data, (dict, list)):
            self.logger.debug(f"Data: {json.dumps(data, indent=2, default=str)}")
        else:
            self.logger.debug(f"Data: {str(data)}")
    
    def log_error(self, node_name: str, error: Exception, context: str = ""):
        """Log errors with context"""
        self.logger.error(f"Error in {node_name}: {str(error)}")
        if context:
            self.logger.error(f"Context: {context}")
    
    def log_processing_stats(self, stats: Dict[str, Any]):
        """Log processing statistics"""
        self.logger.info("=== Processing Statistics ===")
        for key, value in stats.items():
            self.logger.info(f"{key}: {value}")
    
    def close(self):
        """Close logger handlers"""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


def setup_langgraph_logger(chat_id: str) -> LangGraphLogger:
    """Setup and return a LangGraph logger for the chat session"""
    return LangGraphLogger(chat_id)
