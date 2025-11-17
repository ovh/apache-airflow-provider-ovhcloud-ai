# SPDX-License-Identifier: Apache-2.0
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="apache-airflow-provider-ovhcloud-ai",
    version="1.0.0",
    author="Elias TOURNEUX",
    author_email="elias.tourneux.ext@ovhcloud.com",
    description="Apache Airflow Provider for OVHcloud AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ovh/apache-airflow-provider-ovhcloud-ai",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Apache Airflow",
        "Framework :: Apache Airflow :: Provider",
    ],
    python_requires=">=3.8",
    install_requires=[
        "apache-airflow>=2.3.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "apache_airflow_provider": [
            "provider_info=apache_airflow_provider_ovhcloud_ai:get_provider_info"
        ]
    },
)