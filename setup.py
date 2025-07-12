"""
Setup configuration for the Splinterlands Bot Python application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="splinterlands-bot-python",
    version="2.0.0",
    author="Splinterlands Bot Team",
    description="A Python bot for automated Splinterlands gameplay",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dexterpante/splinterlands-bot2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=0.19.0",
        "requests>=2.28.0",
        "colorama>=0.4.4",
        "rich>=12.0.0",
        "pydantic>=1.10.0",
        "asyncio-throttle>=1.0.0",
        "selenium>=4.8.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "click>=8.0.0",
        "schedule>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pylint>=2.15.0",
            "flake8>=5.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
        "database": [
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.9.0",
        ],
        "playwright": [
            "playwright>=1.30.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "splinterlands-bot=main:main",
        ],
    },
)