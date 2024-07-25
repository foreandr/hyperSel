from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=2.20,
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "webdriver-manager",
        "lxml",
        "requests",
        # "undetected-chromedriver",
        "nodriver",
    ],
    include_package_data=True, 
)
