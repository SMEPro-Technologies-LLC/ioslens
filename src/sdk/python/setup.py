"""iOSLENS Python SDK setup."""

from setuptools import setup, find_packages

setup(
    name="ioslens",
    version="1.0.0",
    description="iOSLENS Governed AI Middleware Platform — Python SDK",
    author="SMEPro Technologies LLC",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "pytest-asyncio>=0.23",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
