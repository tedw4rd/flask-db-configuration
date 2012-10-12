import sqlite3

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class DBConfigurator():

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.config['CONFIG_DATABASE'] = "/tmp/" + app.name + ".db"
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def connect(self):
        return sqlite3.connect(self.app.config['CONFIG_DATABASE'])

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'configuration_db'):
                ctx.configuration_db = self.connect()
            return ctx.configuration_db

    def configuration_available(self):
        query = "SELECT * FROM configuration_data"
        self.app.logger.debug("Checking for existing configuration data...")
        try:
            connection.cursor().execute(query)
            results = connection.cursor().fetchall()
            connection.cursor().close()
        except sqlite3.OperationalError:
            self.app.logger.debug("Nope.")
            return False

        self.app.logger.debug("Found!")
        return True

    def setup_config_table(self):
        query = "CREATE TABLE configuration_data (var_name text, value text)"
        self.app.logger.debug("Setting up configuration table...")
        try:
            connection.cursor().execute(query)
            results = connection.cursor().fetchall()
            connection.cursor().close()
            connection.commit()
        except sqlite3.OperationalError as e:
            self.app.logger.error("An error occured while setting up configuration table: " + str(e))
            return False

        self.app.logger.debug("Configuration table setup successfully!")
        return True

    def configure_from_db(self):
        query = "SELECT * FROM configuration_data"
        config = {}
        self.app.logger.debug("Loading app configuration from table...")
        try:
            for row in connection.cursor().execute(query):
                config[row[0]] = row[1]
            connection.cursor().close()
        except sqlite3.OperationalError:
            self.app.logger.error("A DB error occured while loading configuration.")
            return

        for k, v in config.iteritems():
            self.app.config[k] = v

        self.app.logger.debug("Loaded %s configuration variables." % len(config))

    def set_configuration_data(self, var_name, value):
        find_query = "SELECT * FROM configuration_data WHERE var_name = '%s'" % (var_name)
        insert_query = "INSERT INTO configuration_data VALUES ('%s', '%s')" % (var_name, value)
        update_query = "UPDATE configuration_data SET value='%s' WHERE var_name='%s'" % (value, var_name)
        self.app.logger.debug("Setting app configuration from table...")
        try:
            rows = connection.cursor().execute(find_query).fetchall()
            if len(rows) == 0:
                connection.cursor().execute(insert_query)
            else:
                connection.cursor().execute(update_query)
            connection.cursor().close()
        except sqlite3.OperationalError:
            self.app.logger.error("A DB error occured while setting configuration.")
            return

        self.app.logger.debug("Configuration set successfully: %s=%s" % (var_name, value))
