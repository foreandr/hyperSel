import subprocess
from setuptools import setup, find_packages, Command

class PostInstallCommand(Command):
    """Post-installation for installation mode."""
    description = 'Run post-installation tasks'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run the playwright install command
        subprocess.check_call(["playwright", "install", "--with-deps"]) # https://pypi.org/project/undetected-playwright/

# Setup configuration
setup(
    name="hyperSel",
    version=2.54,
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
        "undetected-playwright",
    ],
    include_package_data=True,
    #cmdclass={
    #    'install': PostInstallCommand,
    #},
)
