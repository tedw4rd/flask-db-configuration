# -*- coding: utf-8 -*-
"""
    flaskext.dbconfig
    ~~~~~~~~~~~~~~~~~

    Description of the module goes here...

    :copyright: (c) 2012 by Ted Aronson.
    :license: MIT, see LICENSE for more details.
"""
import sqlite3
import os.path

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from flask import Blueprint, render_template, request


class DBConfigurator():

    def __init__(self, tracked_config_vars, app=None, url_ext="/config"):
        self.tracked_config_vars = tracked_config_vars
        if app is not None:
            self.app = app
            self.url_ext = url_ext
            self.init_app(self.app, self.url_ext, self.tracked_config_vars)
        else:
            self.app = None

    def init_app(self, app, url_ext, tracked_config_vars):
        app.config['CONFIG_DATABASE'] = "/tmp/" + app.name + ".db"
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

        self.config_blueprint = Blueprint("flask-dbconfig", __name__,
                                          static_folder="static",
                                          template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                                          url_prefix=self.url_ext)

        self.config_blueprint.add_url_rule("/", "display_configuration_page", view_func=self.display_configuration_page, methods=["GET"])
        self.config_blueprint.add_url_rule("/", "configure_variables_from_post", view_func=self.configure_variables_from_post, methods=["POST"])
        app.register_blueprint(self.config_blueprint)
        self.conditionally_create_config_table()

    def connect(self):
        return sqlite3.connect(self.app.config['CONFIG_DATABASE'])

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'configuration_db'):
            ctx.configuration_db.close()

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'configuration_db'):
                ctx.configuration_db = self.connect()
            return ctx.configuration_db
        else:
            return self.connect()

    def conditionally_create_config_table(self):
        if not self.config_table_exists():
            self.setup_config_table()

    def config_table_exists(self):
        query = "SELECT * FROM configuration_data"
        self.app.logger.debug("Checking for existing configuration data...")
        try:
            self.connection.cursor().execute(query)
            results = self.connection.cursor().fetchall()
        except sqlite3.OperationalError as e:
            self.app.logger.debug("Nope.")
            return False
        self.app.logger.debug("Found!")
        return True

    def fully_configured(self):
        if self.config_table_exists():
            query = "SELECT * FROM configuration_data"
            self.connection.cursor().execute(query)
            results = self.connection.cursor().fetchall()
            print results
            return True
        else:
            return False

    def setup_config_table(self):
        query = "CREATE TABLE configuration_data (var_name TEXT PRIMARY KEY, value TEXT)"
        self.app.logger.debug("Setting up configuration table...")
        try:
            self.connection.cursor().execute(query)
            results = self.connection.cursor().fetchall()
            self.connection.commit()
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
            for row in self.connection.cursor().execute(query):
                config[row[0]] = row[1]
        except sqlite3.OperationalError:
            self.app.logger.error("A DB error occured while loading configuration.")
            return

        print(str(config))
        for k, v in config.iteritems():
            self.app.config[k] = v

        self.app.logger.debug("Loaded %s configuration variables." % len(config))

    def set_configuration_data(self, var_name, value):
        insert_query = "INSERT OR REPLACE INTO configuration_data VALUES ('%s', '%s')" % (var_name, value)
        self.app.logger.debug("Setting app configuration from table...")
        try:
            rows = self.connection.cursor().execute(insert_query).fetchall()
            self.connection.commit()
        except sqlite3.OperationalError:
            self.app.logger.error("A DB error occured while setting configuration.")
            return

        self.app.logger.debug("Configuration set successfully: %s=%s" % (var_name, value))

    def display_configuration_page(self):
        config = []
        for tracked_var in self.tracked_config_vars:
            if tracked_var in self.app.config:
                config.append({"name": tracked_var, "value": self.app.config[tracked_var]})
            else:
                config.append({"name": tracked_var, "value": ""})

        return render_template("config.html", current_config=config, appname=self.app.name, extension=self.url_ext)

    def configure_variables_from_post(self):
        print request.form
        for tracked_var in self.tracked_config_vars:
            self.set_configuration_data(tracked_var, request.form[tracked_var])

        return make_response(jsonify({'success': True}), 201)
