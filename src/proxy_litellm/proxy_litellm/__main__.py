import uvicorn
from .core.app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", log_config="log_conf.yaml")
