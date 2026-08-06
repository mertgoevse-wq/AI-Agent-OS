import os
import shutil
import tempfile
import pytest
import yaml

from src.rag.prompt_embedder import PromptEmbedder
from src.rag.prompt_indexer import PromptIndexer
from src.rag.prompt_retriever import PromptRetriever
from src.rag.prompt_ranker import PromptRanker

@pytest.fixture
def temp_workspace():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_embedder_mock():
    embedder = PromptEmbedder()
    # Force mock mode for testing
    embedder.has_chroma = False
    
    res = embedder.embed(["hello world", "hello AI"])
    assert len(res) == 2
    assert "hello" in res[0]
    assert "world" in res[0]
    assert "ai" in res[1]

def test_indexer_and_retriever(temp_workspace):
    # Setup fake prompt library
    prompts_dir = os.path.join(temp_workspace, "omni_library", "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    
    with open(os.path.join(prompts_dir, "game_dev_metadata.yaml"), "w") as f:
        yaml.dump({
            "name": "Game Developer",
            "description": "Create a AAA game with multiplayer",
            "tags": ["game", "unity", "networking"],
            "confidence_score": 0.9,
            "source": "official"
        }, f)
        
    with open(os.path.join(prompts_dir, "web_dev_metadata.yaml"), "w") as f:
        yaml.dump({
            "name": "Web Developer",
            "description": "Build a simple html page",
            "tags": ["web", "html"],
            "confidence_score": 0.5,
            "source": "community"
        }, f)
        
    indexer = PromptIndexer(base_path=temp_workspace)
    indexer.embedder.has_chroma = False # force mock
    indexer.has_chroma = False
    indexer.build_index()
    
    assert len(indexer.index) == 2
    
    retriever = PromptRetriever(indexer)
    results = retriever.retrieve("Create a game with multiplayer", top_k=1)
    
    assert len(results) == 1
    assert results[0]["id"] == "game_dev"
    assert results[0]["final_score"] > 0 # Ranker should have boosted it
    
    indexer.close()
    del indexer
    del retriever
    import gc
    gc.collect()

def test_prompt_ranker():
    ranker = PromptRanker()
    
    mock_retrieved = [
        {"id": "p1", "score": 0.8, "metadata": {"confidence_score": 0.5, "source": "community"}},
        {"id": "p2", "score": 0.8, "metadata": {"confidence_score": 0.9, "source": "official"}}
    ]
    
    ranked = ranker.rank(mock_retrieved)
    # p2 should win due to higher confidence and official source boost
    assert ranked[0]["id"] == "p2"
    assert ranked[1]["id"] == "p1"
