from setuptools import setup

setup(
    name='instagram-api',
    version='0.1',
    description='Unofficial Instagram API. Provides access to all Instagram features (like, follow, upload photos, upload videos, etc.)',
    url='https://github.com/LevPasha/Instagram-API-python/',
    author='Pasha Lev',
    author_email='levpasha@gmail.com',
    license='GNU',
    packages=['InstagramAPI'],
    zip_safe=False,
    install_requires=[
      "requests==2.11.1",
      "requests-toolbelt==0.7.0",
      "moviepy==0.2.3.2"
    ])
