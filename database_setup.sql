--These are not meant to be run all at once,  butas a reminder of how to set up infor about a test server the test_client.py wants to know about.

Drop Database If Exists server_manager;
Create Database server_manager;

CREATE TABLE IF NOT EXISTS servers (
                    name VARCHAR(50) PRIMARY KEY,
                    ip VARCHAR(15) NOT NULL,
                    port INTEGER NOT NULL
                );

INSERT INTO servers (name, ip, port)
VALUES ('test_server', '192.168.1.108', 7777)
ON CONFLICT (name) DO NOTHING;