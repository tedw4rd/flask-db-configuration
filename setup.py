"""
Flask-DB-Config
-------------

Configure your Flask application from a local SQLite database, and never have to
ship with a config file again!
"""
from setuptools import setup


setup(
    name='Flask-DB-Config',
    version='0.1',
    url='http://www.github.com/tedw4rd/flask-db-configuration',
    license='MIT',
    author='Ted Aronson',
    author_email='ted.aronson@gmail.com',
    description='Configure Flask applications from a DB',
    long_description=__doc__,
    py_modules=['flask_db_configuration'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)