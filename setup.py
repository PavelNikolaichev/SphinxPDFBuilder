from setuptools import setup, find_packages

setup(
    name="sphinx_pdf_builder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        # Add other dependencies like docker-py if needed
    ],
    entry_points={
        "console_scripts": [
            "sphinx-pdf-build = sphinx_pdf_builder.builder:main",  # CLI command to run the main script
        ],
    },
    author="Pavel Nikolaitchev, NYU RITS",
    description="A library for fetching Sphinx documentation and building it into a PDF using Docker.",
    # url="https://github.com/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
