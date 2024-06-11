from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=1.2,
    packages=find_packages(),
    install_requires=[
        "selenium==4.21.0",
        "beautifulsoup4==4.12.3",
        "webdriver-manager==4.0.1"
    ]
)
