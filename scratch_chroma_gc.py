import chromadb
import os
import shutil
import tempfile
import gc

temp_dir = tempfile.mkdtemp()
print("Temp dir:", temp_dir)

try:
    client = chromadb.PersistentClient(path=os.path.join(temp_dir, "chroma"))
    coll = client.get_or_create_collection(name="test")
    coll.add(documents=["test"], metadatas=[{"k": "v"}], ids=["1"])
    print("Added document")
    
    # Try different close strategies
    try:
        chromadb.api.client.SharedSystemClient.clear_system_cache()
    except Exception as e:
        print("SharedSystemClient.clear_system_cache() failed:", e)
        
    del client
    del coll
    gc.collect()
    
    # Attempt delete
    shutil.rmtree(temp_dir, ignore_errors=False)
    print("Deleted successfully")
except Exception as e:
    print("Failed to delete:", e)
