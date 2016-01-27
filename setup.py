from setuptools import setup

setup(
    name='goodreads',
    description="Python wrapper for Goodreads API, adapted to import owned book lists to a Django project as a record attached to 
    a user",
    long_description=open("README.rst").read(),
    author='Sefa Kilic, adapted to Django by Sam Link',
    author_email='sefakilic@gmail.com',
    url='https://github.com/sefakilic/goodreads/',
    version='0.2.4',
    install_requires=['nose', 'xmltodict', 'requests', 'rauth', 'django-taggit'],
    packages=['goodreads'],
    scripts=[],
    license='MIT',
)
