from setuptools import setup, find_packages

setup(
    name="football_stats",
    version="0.1",
    description="A web application for football statistics analysis",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pandas",
        "python-multipart",
        "jinja2",
        "plotly",
        "gunicorn",
        "pytest",
        "httpx"
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: FastAPI",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
) 