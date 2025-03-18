import asyncio
import json
from typing import Optional
import logging
from server_manager_client import ServerManagerClient

class BaseServer:
    def __init__(
        self,
        server_type: str,
        server_name: str,
        ip: str,
        port: int,
        config_path: Optional[str] = None,
        master_host: Optional[str] = "localhost",
        master_port: Optional[int] = 3000,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the base server with registration details and an optional logger."""
        self.server_type = server_type
        self.server_name = server_name
        self.ip = ip  # This server's listening IP
        self.port = port  # This server's listening port
        
        self.logger = logger if logger else logging.getLogger(__name__)
        if not self.logger.handlers:  # Add basic config if no handlers
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Load config if provided, otherwise use provided master_host and master_port
        if config_path:
            self.config = self._load_config(config_path)
            self.master_host = self.config['server']['host']
            self.master_port = self.config['server']['port']
        else:
            self.master_host = master_host
            self.master_port = master_port

        # Initialize the client to talk to the master server
        self.client = ServerManagerClient(
            host=self.master_host,
            port=self.master_port,
            logger=self.logger
        )
        self.logger.info(f"Initialized BaseServer: {server_type}/{server_name} at {ip}:{port} "
                        f"connecting to master at {self.master_host}:{self.master_port}")

    def _load_config(self, config_path: str) -> dict:
        """Load the configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file {config_path} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in config file {config_path}")

    async def register(self):
        """Register this server with the master server."""
        self.logger.info(f"Registering {self.server_type}/{self.server_name} with master server")
        success = await self.client.register_server(
            server_type=self.server_type,
            server_name=self.server_name,
            ip=self.ip,
            port=self.port
        )
        if success:
            self.logger.info("Registration successful")
        else:
            self.logger.error("Registration failed")

    async def start(self):
        """Start the server, registering it with the master server first."""
        await self.register()
        self.logger.info(f"Starting server {self.server_name} on {self.ip}:{self.port}")
        await self.run()

    async def run(self):
        """Placeholder method for server-specific logic. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement run()")

# Example usage
if __name__ == "__main__":
    async def test_base_server():
        # Custom logger for testing
        custom_logger = logging.getLogger("test_base_server")
        custom_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        custom_logger.addHandler(handler)

        # Create and start a test server with config file
        server = BaseServer(
            server_type="test",
            server_name="test_server",
            ip="192.168.1.100",
            port=5000,
            config_path="config/server_config.json",
            logger=custom_logger
        )
        await server.start()

    asyncio.run(test_base_server())