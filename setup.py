from setuptools import setup
import os.path
import re


with open(
    os.path.join(
        os.path.dirname(__file__),
        'yhttp/extensions/pony/', '__init__.py'
    )
) as v_file:
    package_version = \
        re.compile('.*__version__ = \'(.*?)\'', re.S) \
        .match(v_file.read()) \
        .group(1)


dependencies = [
    'yhttp',
    'sqlalchemy',
]


setup(
    name='yhttp-sqlalchemy',
    version=package_version,
    author='Shayan Rok Rok',
    author_email='shayan.rokrok@gmail.com',
    url='http://github.com/yhttp/yhttp-sqlalchemy',
    description='A very micro http framework.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important!
    install_requires=dependencies,
    packages=['yhttp.extensions.sqlalchemy'],
)

