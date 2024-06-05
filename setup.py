from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="ntt-api-management",
    version="1.0.0",
    author="threezinedine",
    author_email="threezinedine@gmail.com",
    description=description,
    packages=find_packages(),
    install_requires=[],
    keywords=["API", "Management", "ntt"],
)
