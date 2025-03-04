import os 
import sys 
from pathlib import Path 
 
# Get the directory containing this file 
current_dir = Path(__file__).parent.absolute() 
 
# Get port from environment variable 
port = os.environ.get('PORT', '8501') 
 
import streamlit.web.cli as stcli 
 
if __name__ == "__main__": 
    app_path = str(current_dir / "app.py") 
    sys.argv = ["streamlit", "run", app_path, "--server.port", port, "--server.address", "0.0.0.0"] 
    sys.exit(stcli.main()) 
