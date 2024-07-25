from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=2.21,
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "webdriver-manager",
        "lxml",
        "requests",
        "nodriver",
    ],
    include_package_data=True, 
)
