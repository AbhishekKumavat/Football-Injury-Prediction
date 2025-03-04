import os 
import sys 
from pathlib import Path 
 
current_dir = Path(__file__).parent.absolute() 
print(f"Current directory: {current_dir}") 
 
print("Files available:") 
for f in os.listdir(current_dir): 
    print(f"- {f}") 
 
port = os.environ.get('PORT', '8501') 
print(f"Using port: {port}") 
 
import streamlit.web.cli as stcli 
 
if __name__ == "__main__": 
    test_app = str(current_dir / "test_app.py") 
    print(f"Running: {test_app}") 
    sys.argv = ["streamlit", "run", test_app, "--server.port", port, "--server.address", "0.0.0.0"] 
    sys.exit(stcli.main()) 
