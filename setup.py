from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=2.0,
    packages=find_packages(),
    install_requires=[
        "selenium==4.21.0",
        "beautifulsoup4==4.12.3",
        "webdriver-manager==4.0.1",
        "lxml==5.2.2",
    ]
)
