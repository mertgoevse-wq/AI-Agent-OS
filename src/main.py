import os
from dotenv import load_dotenv
from src.utils.logger import logger
from src.router.model_router import ModelRouter

def main():
    logger.info("Initializing AI-Agent-OS (Phase 1: Foundation)")
    
    # Lade Umgebungsvariablen (.env)
    load_dotenv()
    
    router = ModelRouter()
    
    # Beispielhafter Call an den Model Router (Simulation)
    # Beachte: Da wir in der lokalen Testumgebung vermutlich keine echten API Keys haben, 
    # wird dies entweder fehlschlagen oder wir simulieren es.
    messages = [
        {"role": "system", "content": "Du bist ein hilfreicher KI-Assistent."},
        {"role": "user", "content": "Hallo, System! Bist du online?"}
    ]
    
    logger.info("Testing Model Router with dummy prompt...")
    
    # Um keine unnötigen API Kosten zu verursachen oder abzustürzen,
    # prüfen wir, ob Keys da sind, bevor wir einen echten Call absetzen.
    if os.getenv("OPENAI_API_KEY"):
        response = router.generate_response(messages, model="gpt-4o")
        logger.info(f"Response from OpenAI: {response}")
    elif os.getenv("ANTHROPIC_API_KEY"):
        response = router.generate_response(messages, model="claude-3-5-sonnet-20240620")
        logger.info(f"Response from Anthropic: {response}")
    else:
        logger.warning("No API Keys found in environment. Skipping actual model call.")
        logger.info("System interfaces and routing logic initialized successfully.")

    logger.info("AI-Agent-OS Boot Sequence Complete.")

if __name__ == "__main__":
    main()
