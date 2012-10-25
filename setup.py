"""
Flask-DBConfig
--------------

Configure your Flask application from a local SQLite database, and never have
to ship with a config file again!

Links
`````

* `documentation <http://packages.python.org/Flask-DBConfig>`_

"""
from setuptools import setup


setup(
    name='Flask-DBConfig',
    version='0.2',
    url='https://github.com/tedw4rd/flask-db-configuration/',
    license='MIT',
    author='Ted Aronson',
    author_email='ted.aronson@gmail.com',
    description='Configure Flask applications from a local DB',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
