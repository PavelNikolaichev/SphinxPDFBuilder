from setuptools import setup, find_packages

setup(
    name="sphinx_pdf_builder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4==4.10.0",
    ],
    entry_points={
        "console_scripts": [
            "sphinx-pdf-build = sphinx_pdf_builder.builder:main",  # CLI command to run the main script
        ],
    },
    author="Pavel Nikolaitchev, NYU RITS",
    description="A small crappy library to fetch and build Sphinx documentation using docker containers.",
    url="https://github.com/PavelNikolaichev/SphinxPDFBuilder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
