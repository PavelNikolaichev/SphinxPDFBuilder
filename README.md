# Sphinx PDF Builder

This library fetches the Sphinx documentation from a GitHub repository and builds it into a PDF using Docker container.

## Installation

1. Clone the repository
2. Make sure you have Docker installed on your machine
3. Install the python package:

```bash
pip install .
```

## Usage

Before running, make sure your docker is running.

```python
from sphinx_pdf_builder import SphinxPDFBuilder

builder = SphinxPDFBuilder(index_url, output_directory)
builder.build()
```

Actually make sure the output directory exists before running the build command. Otherwise it might throw an error.

After successful build, the PDF file will be available in the output directory.
