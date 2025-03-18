from setuptools import setup

setup(
    name="server_manager_base_server",
    version="0.1.0",
    py_modules=['server_manager_base_server'],
    install_requires=['server_manager_client'],  # Depends on the client library
    description="A base server library for registering with server_manager",
    author="Chris Segroves",
    author_email="your.email@example.com",
)