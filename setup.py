from setuptools import setup, find_packages

setup(
    name="hyperSel",
    version=2.37,
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "webdriver-manager",
        "lxml",
        "requests",
        "nodriver",
        "psutil",
        "playwright",
    ],
    include_package_data=True, 
)
