import asyncio
import json
from typing import Tuple, Optional
import logging



class ServerManagerClient:
    def __init__(self, host: str = "localhost", port: int = 3000, config_path: Optional[str] = None, logger: logging.Logger = None):
        """Initialize the client with either a config file or direct host/port, and an optional logger."""
        self.logger = logger if logger else logging.getLogger(__name__)  # Use provided logger or default
        if not self.logger.handlers:  # If no handlers, add a basic one to avoid silent logging
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        if config_path:
            self.config = self._load_config(config_path)
            self.host = self.config['master_server']['host']
            self.port = self.config['master_server']['port']
        else:
            self.host = host
            self.port = port
        logger.info(f"Initialized client for {self.host}:{self.port}")

    def _load_config(self, config_path: str) -> dict:
        """Load the client configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file {config_path} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in config file {config_path}")

    async def register_server(self, server_type: str, server_name: str, ip: str, port: int) -> bool:
        """Register a server with the master server."""
        request = {
            'type': 'register',
            'target_server_type': server_type,
            'target_server_name': server_name,
            'ip': ip,
            'port': port
        }
        response = await self._send_request(request)
        return response.get('status') == 'success'

    async def discover_server(self, server_type: str, server_name: Optional[str] = None) -> Tuple[str, int] | None:
        """Discover a server from the master server."""
        request = {
            'type': 'discover',
            'target_server_type': server_type,
            'target_server_name': server_name
        }
        response = await self._send_request(request)
        if response.get('status') == 'success':
            return (response['ip'], response['port'])
        self.logger.error(f"Failed to discover server: {response.get('message', 'Unknown error')}")
        return None

    async def _send_request(self, request: dict) -> dict:
        """Send a request to the master server and return the response."""
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            self.logger.info(f"Sending request to {self.host}:{self.port}: {request}")
            writer.write(json.dumps(request).encode())
            await writer.drain()

            data = await reader.read(1024)
            response = json.loads(data.decode())
            self.logger.info(f"Received response: {response}")

            writer.close()
            await writer.wait_closed()
            return response
        except Exception as e:
            self.logger.error(f"Error communicating with master server: {e}")
            raise

# Example usage
if __name__ == "__main__":
    async def server_manager_client():
        custom_logger = logging.getLogger("test_client")
        custom_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        custom_logger.addHandler(handler)
        client = ServerManagerClient("localhost", 3000, logger=custom_logger)
        # Test registration
        success = await client.register_server("test", "server1", "192.168.1.100", 5000)
        print(f"Registration successful: {success}")
        # Test discovery
        server_info = await client.discover_server("test", "server1")
        print(f"Discovered server: {server_info}")

    asyncio.run(server_manager_client())