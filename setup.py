from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rdp',
    version='0.0.1',
    descripion='Research Data Product (Interface)',
    long_description=readme,
    author='Tobias Weber',
    author_email='mail@tgweber.de',
    url='https://github.com/tgweber/rdp',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
