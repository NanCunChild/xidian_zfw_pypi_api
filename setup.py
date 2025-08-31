from setuptools import setup, find_packages
import os

version_str = os.environ.get("GITHUB_REF_NAME")

if version_str and version_str.startswith('v'):
    version = version_str.lstrip("v")
else:
    version = "0.0.0.dev0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xidian-zfw",
    version=version,
    author="NanCunChild",
    author_email="nancunchild@gmail.com",
    description="API for Xidian ZFW network system",
    license="GPL-3.0-or-later",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NanCunChild/xidian_zfw_pypi_api",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "requests>=2.20.0",
        "pandas>=2.1.0",
        "beautifulsoup4>=4.8.0",
        "pycryptodome>=3.16.0",
        "Pillow>=11.1.0",
        "onnxruntime>=1.18.0",
        "numpy>=2.3.0",
        "urllib3>=2.2.0",
        "python-dotenv>=1.1.0"
    ],
)