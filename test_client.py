import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, config_path: str = "client_config.json"):
        self.config= self.load_config()
        logger.info(f"Loaded client configuration :{self.config}")
        logger.info(f"Loaded client configuration")
    
    def load_config(self):
        """Load the client configuration from a JSON file."""
        """The client_config.json should looke like this:
            {
                "master_server": {
                    "host": "localhost",
                    "port": 3000
                },
                "target_server": "test_server"
            }
        """
        try:
            path='config/client_config.json'
            with open('config/client_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file {path} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in config file {path}")
    
    async def request_server_info(self,server_name:str)->tuple:
        """Request server information from the master server."""
        master_config=self.config['master_server']
        logger.info(f"Requesting server information for {server_name} from {master_config['host']}:{master_config['port']}")

        try:
            reader, writer = await asyncio.open_connection(
                master_config['host'],
                master_config['port']
            )

            request = {'server_name': server_name}
            logger.info(f"Requesting server information for {server_name} with reader {reader} and writer {writer}")
            writer.write(json.dumps(request).encode())
            await writer.drain()

            data = await reader.read(1024)
            response = json.loads(data.decode())

            writer.close()
            await writer.wait_closed()

            if response['status']=='success':
                logger.info(f"Received server information for {server_name}: {response['ip']}: {response['port']}")
                return (response['ip'],response['port'])
            else:
                logger.error(f"Failed to get server information: {response['message']}")
                return None
        except Exception as e:
            logger.error(f"Error requesting server information: {e}")
            return None
        
    async def run(self):
        """Run the client."""
        target_server=self.config['target_server']
        logger.info(f"Running client for {target_server}")
        server_info= await self.request_server_info(target_server)
        logger.info(f"Server information for {target_server}: {server_info}")
        if server_info:
            logger.info(f"Connecting to {target_server} at {server_info[0]}:{server_info[1]}")
        else:
            logger.error(f"Failed to get server information for {target_server}")

async def main():
    client=Client()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
