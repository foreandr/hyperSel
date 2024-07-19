from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=2.11,
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "webdriver-manager",
        "lxml",
        "requests",
    ],
    include_package_data=True, 
)
