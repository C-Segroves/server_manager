import asyncio
import logging
from server_manager_base_server import BaseServer

# Configure custom logger
logger = logging.getLogger("my_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class MyServer(BaseServer):
    async def run(self):
        """Implement the specific server logic."""
        self.logger.info(f"Server {self.server_name} is now running")
        # Example: Simple echo server
        server = await asyncio.start_server(self.handle_client, self.ip, self.port)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming client connections."""
        addr = writer.get_extra_info('peername')
        self.logger.info(f"Received connection from {addr}")
        data = await reader.read(100)
        message = data.decode()
        self.logger.info(f"Received: {message}")
        writer.write(data)
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        self.logger.info(f"Connection from {addr} closed")

async def main():
    server = MyServer(
        server_type="echo",
        server_name="echo_server1",
        ip="127.0.0.1",
        port=6000,
        logger=logger
    )
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())