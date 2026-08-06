import os
import shutil
import tempfile
import pytest
from src.autonomous.agent_memory import AgentMemory

@pytest.fixture
def temp_workspace():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_agent_memory(temp_workspace):
    memory = AgentMemory(base_path=temp_workspace)
    
    # Check initialization
    assert os.path.exists(memory.state_file)
    
    # Test read/write
    memory.update_key("test_key", "test_value")
    assert memory.get_key("test_key") == "test_value"
    
    # Test logs
    memory.append_log("Log 1")
    memory.append_log("Log 2")
    
    logs = memory.get_key("execution_logs")
    assert len(logs) == 2
    assert logs[0] == "Log 1"
    assert logs[1] == "Log 2"
