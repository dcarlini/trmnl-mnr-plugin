from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trmnl-mnr-plugin",
    version="1.1.0b1",
    author="dcarlini",
    author_email="",
    description="Metro-North Railroad trip finder with transfer support for TRMNL e-ink displays",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcarlini/trmnl-mnr-plugin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
        "flask>=2.0.0",
        "requests>=2.25.0",
        "pytz>=2021.1",
        "protobuf>=3.19.0",
    ],
    entry_points={
        "console_scripts": [
            "mnr-trip-finder=server.mnr_trip_finder:main",
        ],
    },
)