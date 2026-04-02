import redshift_connector


class RedshiftConnection:
    """
    Manages connection to Amazon Redshift data warehouse.

    This class handles connection creation and management using the
    redshift-connector library.
    """

    def __init__(self, host, database, user, password, port=5439, ssl=True, timeout=10, logger=None):
        """
        Initialize and create the connection to Redshift.

        Parameters:
            host (str): Redshift cluster endpoint
            database (str): Database name
            user (str): Database user
            password (str): Database password
            port (int, optional): Database port. Defaults to 5439
            ssl (bool, optional): Use SSL connection. Defaults to True
            timeout (int, optional): Connection timeout in seconds. Defaults to 10
            logger (logging.Logger, optional): Logger instance for connection status messages

        Returns:
            None
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.ssl = ssl
        self.timeout = timeout
        self.logger = logger
        self.connection = None
        self._connect()

    def _connect(self):
        """
        Establish connection to Redshift DWH.

        Creates a connection with SSL enabled and appropriate timeout settings.
        """
        if self.logger:
            self.logger.info("Connecting to Redshift...")

        self.connection = redshift_connector.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=int(self.port),
            ssl=self.ssl,
            sslmode='require' if self.ssl else 'prefer',
            timeout=self.timeout,
        )

        if self.logger:
            self.logger.info("Successfully connected to Redshift")

    def get_connection(self):
        """
        Get the active Redshift connection.

        Returns:
            redshift_connector.Connection: Active connection to Redshift
        """
        if self.connection is None:
            self._connect()
        return self.connection

    def execute_query(self, query, params=None):
        """
        Execute a query and return results.

        Parameters:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters for parameterized queries

        Returns:
            cursor: Database cursor with query results
        """
        cursor = self.get_connection().cursor()
        cursor.execute(query, params)
        return cursor

    def close(self):
        """
        Close the Redshift connection.
        """
        if self.connection:
            try:
                self.connection.close()
                if self.logger:
                    self.logger.info("Connection to Redshift closed")
            except Exception:
                pass  # Connection already closed

    def __enter__(self):
        """
        Context manager entry.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - ensures connection is closed.
        """
        self.close()
