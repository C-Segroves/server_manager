import asyncio
import json
import logging
from server_manager_client import ServerManagerClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Client:
    def __init__(self):
        self.config = self.load_config()
        logger.info(f"Loaded client configuration: {self.config}")

    def load_config(self):
        """Load the client configuration from a JSON file."""
        """
        The client_config.json should look like this:
        {
            "master_server": {
                "host": "localhost",
                "port": 3000
            },
            "target_server_name": "target_server_name : if this won't be handled by the client.",
            "target_server_type": "target_server_type : if this won't be handled by the client."
        }
        """
        try:
            path = 'config/client_config.json'
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file {path} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in config file {path}")

    async def run(self):
        """Run the client and discover a server."""
        client = ServerManagerClient(
            host=self.config['master_server']['host'],
            port=self.config['master_server']['port'],
            logger=logger  # Pass the logger to ServerManagerClient
        )
        target_server_type = self.config['target_server_type']
        target_server_name = self.config['target_server_name']
        server_info = await client.discover_server(target_server_type, target_server_name)
        if server_info:
            logger.info(f"Connect to server at {server_info[0]}:{server_info[1]}")
        else:
            logger.warning("No server found")

async def main():
    client = Client()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())