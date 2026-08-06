import chromadb
import os
import shutil
import tempfile

temp_dir = tempfile.mkdtemp()
print("Temp dir:", temp_dir)

try:
    client = chromadb.PersistentClient(path=os.path.join(temp_dir, "chroma"))
    coll = client.get_or_create_collection(name="test")
    coll.add(documents=["test"], metadatas=[{"k": "v"}], ids=["1"])
    print("Added document")
    
    # Try different close strategies
    try:
        client.close()
    except Exception as e:
        print("client.close() failed:", e)
        
    try:
        chromadb.api.client.SharedSystemClient.clear_system_cache()
    except Exception as e:
        print("SharedSystemClient.clear_system_cache() failed:", e)
        
    try:
        client._system.stop()
    except Exception as e:
        print("client._system.stop() failed:", e)
        
    del client
    del coll
    
    # Attempt delete
    shutil.rmtree(temp_dir)
    print("Deleted successfully")
except Exception as e:
    print("Failed to delete:", e)
