import logging
import os

def setup_logger(name: str = "ai_agent_os") -> logging.Logger:
    """
    Konfiguriert und liefert den Basis-Logger für das System.
    Später kann dies durch OpenTelemetry oder strukturiertes JSON-Logging ersetzt werden.
    """
    logger = logging.getLogger(name)
    
    # Vermeide doppelte Handler, falls mehrmals aufgerufen
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if os.getenv("DEBUG") else logging.INFO)
        
        # Konsole-Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if os.getenv("DEBUG") else logging.INFO)
        
        # Format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        
    return logger

# Globaler Logger Instanz
logger = setup_logger()
