from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xidian-zfw",
    version="0.2.0",
    author="NanCunChild",
    author_email="nancunchild@gmail.com",
    description="API for Xidian ZFW network system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NanCunChild/xidian-zfw-pypi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL version 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "requests>=2.20.0",
        "pandas>=2.1.0",
        "beautifulsoup4>=4.8.0",
        "pycryptodome>=3.16.0",
        "Pillow>=11.1.0",
        "ddddocr>=1.0.5",
        "onnxruntime>=1.18.0",
        "urllib3>=2.2.0",
        "python-dotenv>=1.1.0"
    ],
)