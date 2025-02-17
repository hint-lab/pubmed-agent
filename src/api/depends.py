from functools import lru_cache
from src.config import Config
from src.agents.pubmed_assistant import PubMedAssistant

@lru_cache()
def get_pubmed_assistant():
    config = Config(config_file="./config.yaml")
    return PubMedAssistant(name="PubMedAssistant", config=config) 