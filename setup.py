from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=2.17,
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "webdriver-manager",
        "lxml",
        "requests",
        "undetected-chromedriver",
    ],
    include_package_data=True, 
)
