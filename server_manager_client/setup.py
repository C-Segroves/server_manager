from setuptools import setup

setup(
    name="server_manager_client",
    version="0.1.0",
    py_modules=['server_manager_client'],
    install_requires=['asyncpg'],  # If clients need asyncpg; remove if not
    description="A client library for interacting with the server_manager master server",
    author="Chris Segroves",
    author_email="your.email@example.com",
)