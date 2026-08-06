import os
import shutil
import tempfile
import pytest
import yaml
from scripts.omni_marketplace_importer import OmniMarketplaceImporter

@pytest.fixture
def temp_workspace():
    # Create a temporary workspace to test the importer without messing up real files
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_importer_scoring_and_category(temp_workspace):
    importer = OmniMarketplaceImporter(base_path=temp_workspace)
    
    # Test scoring
    small_content = "def test():\n  pass"
    score1 = importer._score_quality(small_content, ".py")
    assert score1 >= 0.5
    
    large_content = "def test():\n  pass\n" * 100
    score2 = importer._score_quality(large_content, ".py")
    assert score2 > score1
    
    # Test category determination
    assert importer._determine_category("some_mcp.py", "def start_mcp():") == "mcp_tools"
    assert importer._determine_category("agent.yaml", "role: tester") == "agents"
    assert importer._determine_category("my_workflow.md", "workflow definition") == "orchestrators"

def test_importer_duplicate_detection(temp_workspace):
    importer = OmniMarketplaceImporter(base_path=temp_workspace)
    
    # Create a dummy metadata file
    agents_dir = os.path.join(temp_workspace, "omni_library", "agents")
    os.makedirs(agents_dir, exist_ok=True)
    
    fake_catalog = {
        "agents": [
            {"content_hash": "dummyhash123"}
        ]
    }
        
    assert importer._is_duplicate("dummyhash123", fake_catalog) == True
    assert importer._is_duplicate("newhash456", fake_catalog) == False
