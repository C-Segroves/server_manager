import asyncio
import json
import asyncpg
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MasterServer:
    def __init__(self):
        self.config= self.load_db_config()
        logger.info(f"Loaded server configuration")
        self.db_pool = None

    def load_db_config(self):
        """Load the database configuration from a JSON file."""
        """The server_db_config.json should looke like this:
        {
            "server": {
                "host":"localhost",
                "port": 3000
            },
            "database": {
                "dbname": "server_manager",
                "user": "postgres",
                "password": "postgres",
                "host": "192.168.1.100",
                "port": "5433" 
        }
        """

        try:
            path='config/server_db_config.json'
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file {path} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in config file {path}")
    
    async def init_db(self):
        """Initialize the PostgreSQL database connection pool."""
        db_config=self.config['database']
        
        self.db_pool= await asyncpg.create_pool(
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['dbname'],
            host=db_config['host'],
            port=db_config['port']
        )

        logger.info("Connected to Server Manager PostgreSQL database")
    
    async def get_server_info(self,server_name:str)->tuple:
        async with self.db_pool.acquire() as conn:
            logger.info(f"Querying database for server {server_name}")
            result= await conn.fetchrow("SELECT ip,port FROM servers WHERE name=$1",server_name)
            logger.info(f"Database query result: {result}")
            if result:
                return (result['ip'],result['port'])
            else:
                return None
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming client connections."""
        addr=writer.get_extra_info('peername')
        logger.info(f"Received connection from {addr}")

        try:
            data = await reader.read(1024)
            if not data:
                return
            
            request = json.loads(data.decode())
            logger.info(f"Received request: {request}")
            requested_server = request.get('server_name')

            server_info = await self.get_server_info(requested_server)
            if server_info:
                response = {
                    'status': 'success',
                    'ip': server_info[0],
                    'port': server_info[1]
                }
            else:
                response = {
                    'status': 'error',
                    'message': 'Server not found'
                    }
            
            writer.write(json.dumps(response).encode())
            await writer.drain()
        
        except Exception as e:
            logger.error(f"Error handling client request: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Connection from {addr} closed")

    async def start(self):
        "Start Master Server"
        await self.init_db()

        server_config=self.config['server']
        server = await asyncio.start_server(
            self.handle_client,
            server_config['host'],
            server_config['port']
        )

        addr = server.sockets[0].getsockname()
        logger.info(f"Master server listening on {addr}")

        async with server:
            await server.serve_forever()


async def main():
    server = MasterServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())