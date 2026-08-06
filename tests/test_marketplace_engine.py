import os
import shutil
import tempfile
import pytest
import json
from src.core.marketplace_catalog import MarketplaceCatalog
from scripts.omni_marketplace_importer import OmniMarketplaceImporter

@pytest.fixture
def temp_workspace():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_marketplace_quality_scoring(temp_workspace):
    importer = OmniMarketplaceImporter(base_path=temp_workspace)
    
    # Base score
    score1 = importer._score_quality("def myfunc(): pass", ".py")
    
    # Adding tests increases score
    score2 = importer._score_quality("def myfunc(): pass\n# tests here\nassert True", ".py")
    assert score2 > score1
    
    # Adding security risks decreases score
    score3 = importer._score_quality("def myfunc(): pass\nimport os\nos.system('rm -rf')", ".py")
    assert score3 < score1

def test_marketplace_catalog_search(temp_workspace):
    catalog = MarketplaceCatalog(base_path=temp_workspace)
    os.makedirs(catalog.library_path, exist_ok=True)
    
    # Create fake catalog
    fake_data = {
        "agents": [
            {
                "id": "game_dev",
                "name": "Game Developer",
                "description": "Develops games",
                "confidence_score": 0.9,
                "tags": ["game", "c#"],
                "installed": False
            },
            {
                "id": "web_dev",
                "name": "Web Developer",
                "description": "Develops web apps",
                "confidence_score": 0.8,
                "tags": ["web"],
                "installed": False
            }
        ]
    }
    catalog._save_catalog(fake_data)
    
    res = catalog.search("game")
    assert len(res["results"]) == 1
    assert res["results"][0]["id"] == "game_dev"
    
def test_marketplace_install_uninstall(temp_workspace):
    catalog = MarketplaceCatalog(base_path=temp_workspace)
    os.makedirs(catalog.library_path, exist_ok=True)
    os.makedirs(os.path.join(temp_workspace, "omni_library", "cache", "agents"), exist_ok=True)
    
    cache_file = os.path.join(temp_workspace, "omni_library", "cache", "agents", "test_agent.py")
    with open(cache_file, "w") as f:
        f.write("def agent(): pass")
        
    fake_data = {
        "agents": [
            {
                "id": "test_agent",
                "name": "Test Agent",
                "description": "A test agent",
                "cache_path": cache_file,
                "installed": False
            }
        ],
        "skills": [],
        "prompts": [],
        "orchestrators": [],
        "mcp_tools": []
    }
    catalog._save_catalog(fake_data)
    
    # Install
    assert catalog.install("agents", "test_agent") == True
    active_file = os.path.join(temp_workspace, "omni_library", "agents", "test_agent.py")
    active_meta = os.path.join(temp_workspace, "omni_library", "agents", "test_agent_metadata.yaml")
    
    assert os.path.exists(active_file)
    assert os.path.exists(active_meta)
    
    # Check catalog state
    data = catalog._load_catalog()
    assert data["agents"][0]["installed"] == True
    
    # Uninstall
    assert catalog.uninstall("agents", "test_agent") == True
    assert not os.path.exists(active_file)
    assert not os.path.exists(active_meta)
    
    # Check catalog state
    data = catalog._load_catalog()
    assert data["agents"][0]["installed"] == False
