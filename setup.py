from setuptools import setup, find_packages
setup(
    name = "mturk",
    version = "0.1.0",
    packages = find_packages(),
    install_requires = ["requests>=2.9.1",
                        "xmltodict>=0.9.2"]
)

