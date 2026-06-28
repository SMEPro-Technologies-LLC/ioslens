from setuptools import setup, find_packages

setup(
    name="ioslens",
    version="1.0.0",
    description="iOSLENS.ai Python SDK — Governed AI Intelligence Platform",
    author="SMEPro Technologies LLC",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "httpx>=0.27.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0", "pytest-asyncio>=0.23.0"],
    },
)
