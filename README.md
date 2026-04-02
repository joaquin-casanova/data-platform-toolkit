# Data Platform Toolkit

A Python library providing utilities for connecting to and interacting with data platforms, currently focused on Amazon Redshift.

## Features

- **Simple & Direct**: Clean API using native `redshift-connector` without ORM overhead
- **Flexible Configuration**: Accept connection parameters directly - manage credentials your way
- **SSL Support**: SSL enabled by default with configurable security options
- **Auto-reconnection**: Automatic connection health checks and reconnection
- **Context Manager**: Automatic resource cleanup with `with` statements
- **Optional Logging**: Built-in logging support for connection monitoring

## Requirements

- Python 3.11+
- `redshift-connector >= 2.1.0`

## Installation

```bash
# Install from source (development mode)
pip install -e .

# Or install normally
pip install .
```

## Quick Start

```python
from data_platform_toolkit.connections.redshift import RedshiftConnection

# Basic usage with context manager (recommended)
with RedshiftConnection(
    host='my-cluster.us-east-1.redshift.amazonaws.com',
    database='mydb',
    user='myuser',
    password='mypassword'
) as conn:
    cursor = conn.execute_query("SELECT * FROM users LIMIT 10")
    results = cursor.fetchall()
    for row in results:
        print(row)
```

## Usage Examples

### Using Environment Variables

```python
import os
from dotenv import load_dotenv
from data_platform_toolkit.connections.redshift import RedshiftConnection

load_dotenv()

with RedshiftConnection(
    host=os.getenv('REDSHIFT_HOST'),
    database=os.getenv('REDSHIFT_DB'),
    user=os.getenv('REDSHIFT_USER'),
    password=os.getenv('REDSHIFT_PASSWORD')
) as conn:
    cursor = conn.execute_query("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Total users: {count}")
```

### With Logging

```python
import logging
from data_platform_toolkit.connections.redshift import RedshiftConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with RedshiftConnection(
    host='my-cluster.us-east-1.redshift.amazonaws.com',
    database='mydb',
    user='myuser',
    password='mypassword',
    logger=logger
) as conn:
    cursor = conn.execute_query("SELECT version()")
    version = cursor.fetchone()[0]
    print(f"Redshift version: {version}")
```

### Parameterized Queries

```python
with RedshiftConnection(
    host='my-cluster.us-east-1.redshift.amazonaws.com',
    database='mydb',
    user='myuser',
    password='mypassword'
) as conn:
    cursor = conn.execute_query(
        "SELECT * FROM users WHERE created_at > %s",
        params=('2024-01-01',)
    )
    recent_users = cursor.fetchall()
```

### Manual Connection Management

```python
# If you need to manage the connection lifecycle manually
conn = RedshiftConnection(
    host='my-cluster.us-east-1.redshift.amazonaws.com',
    database='mydb',
    user='myuser',
    password='mypassword',
    port=5439,
    ssl=True,
    timeout=15
)

try:
    cursor = conn.get_connection().cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
finally:
    conn.close()
```

### Iterating Over Large Results

```python
with RedshiftConnection(
    host='my-cluster.us-east-1.redshift.amazonaws.com',
    database='mydb',
    user='myuser',
    password='mypassword'
) as conn:
    cursor = conn.execute_query("SELECT * FROM large_table")

    # Iterate without loading everything into memory
    for row in cursor:
        process(row)
```

## API Reference

### RedshiftConnection

#### `__init__(host, database, user, password, port=5439, ssl=True, timeout=10, logger=None)`

Initialize and create connection to Redshift.

**Parameters:**
- `host` (str): Redshift cluster endpoint
- `database` (str): Database name
- `user` (str): Database user
- `password` (str): Database password
- `port` (int, optional): Database port. Defaults to 5439
- `ssl` (bool, optional): Use SSL connection. Defaults to True
- `timeout` (int, optional): Connection timeout in seconds. Defaults to 10
- `logger` (logging.Logger, optional): Logger instance for connection status messages

#### `execute_query(query, params=None)`

Execute a query and return cursor with results.

**Parameters:**
- `query` (str): SQL query to execute
- `params` (tuple, optional): Query parameters for parameterized queries

**Returns:**
- cursor: Database cursor with query results

#### `get_connection()`

Get the active Redshift connection. Automatically reconnects if connection is closed.

**Returns:**
- redshift_connector.Connection: Active connection to Redshift

#### `close()`

Explicitly close the Redshift connection.

## Configuration

The library accepts connection parameters directly. You can manage configuration using:

- **Environment variables** (recommended for production)
- **Config files** (JSON, YAML, INI, etc.)
- **AWS Secrets Manager** (for enhanced security)
- **Parameter Store**
- **Direct parameters** (for testing)

### Example .env file

```env
REDSHIFT_HOST=my-cluster.us-east-1.redshift.amazonaws.com
REDSHIFT_DB=mydb
REDSHIFT_USER=myuser
REDSHIFT_PASSWORD=mypassword
REDSHIFT_PORT=5439
```

## Security Best Practices

- Never hardcode credentials in your code
- Use environment variables or secrets management services
- Enable SSL in production (enabled by default)
- Use IAM authentication when possible
- Rotate credentials regularly
- Use least-privilege database users

## Development

### Project Structure

```
data_platform_toolkit/
├── connections/          # Database connection modules
│   └── redshift.py      # Redshift connection implementation
└── __init__.py
```

### Contributing

This is currently a personal project. Feel free to fork and adapt to your needs.

## License

MIT License - See pyproject.toml for details

## Author

Joaquín C. (joaquin.casanova.c@gmail.com)
