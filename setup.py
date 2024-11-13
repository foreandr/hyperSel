import os
import subprocess
from setuptools import setup, find_packages

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Setup configuration
setup(
    name="hyperSel",
    version=3.15,
    author="foreandr",  # Your name or username
    author_email="foreandr@gmail.com",  # Your email
    description="A Python-based web automation and data scraping framework",  # Short description
    long_description=long_description,  # Long description from README.md
    long_description_content_type="text/markdown",  # Specifies the format of the long description (Markdown)
    packages=find_packages(),  # Automatically finds all packages in your project
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
        "screeninfo",
        "customtkinter",
        "pillow",
    ],
    include_package_data=True,  # Include additional files from MANIFEST.in or other configurations
    package_data={
        # "hypersel": ["data/*.csv"]  # Include all CSV files in the hypersel/data directory
    },
    url="https://github.com/foreandr/hyperSel",  # URL to the project (optional, but useful for PyPI)
    classifiers=[  # Optional: Classifiers to categorize your project
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version required
)
