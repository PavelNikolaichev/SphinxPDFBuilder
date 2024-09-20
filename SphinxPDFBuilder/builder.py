import utils
import os
import requests
import subprocess
from bs4 import BeautifulSoup


class SphinxPDFBuilder:
    def __init__(self, index_url, output_dir):
        self.index_url = index_url
        self.output_dir = output_dir
        self.repo_url = None
        self.repo_dir = "cloned_repo"

    def fetch_github_repo_url(self):
        response = requests.get(self.index_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch documentation from {self.index_url}")

        soup = BeautifulSoup(response.text, "html.parser")
        # Find the GitHub repo URL in the page (typically in a <a> tag)
        repo_link = soup.find("a", href=lambda href: href and "github.com" in href)
        if not repo_link:
            raise Exception("GitHub repository link not found.")

        self.repo_url = repo_link["href"]
        if self.repo_url.endswith("/"):
            self.repo_url = self.repo_url[:-1] + ".git"

        print(f"GitHub Repo URL: {self.repo_url}")

    def build_docker_container(self):
        dockerfile_content = f"""
        FROM python:3.9-slim

        # Install necessary dependencies
        RUN apt-get update && apt-get install -y \\
            git \\
            xz-utils \\
            calibre \\
            make \\
            && apt-get clean \\
            && pip install sphinx

        RUN mkdir /output_pdf

        RUN useradd -m dockeruser
        USER dockeruser

        # Clone the repository directly inside the Docker container
        WORKDIR /home/dockeruser
        RUN git clone {self.repo_url} ./docs

        WORKDIR /home/dockeruser/docs

        # Install any documentation requirements
        RUN [ -f ./docs/doc-requirements.txt ] && pip install -r ./docs/doc-requirements.txt

        # Build the EPUB using Sphinx in /docs
        # RUN cd ./docs && make epub
        RUN sphinx-build -b epub ./docs/source ./docs/build/epub
        
        RUN ls ./docs/build/epub/
        # Convert EPUB to PDF using calibre ebook-convert
        RUN ebook-convert ./docs/build/epub/*.epub ./docs/build/epub/output.pdf

        USER root
        RUN cp ./docs/build/epub/output.pdf /output_pdf/output.pdf
        CMD ["cp", "./docs/build/epub/output.pdf", "/output_pdf/output.pdf"]
        RUN ls /output_pdf
        """
        dockerfile_path = os.path.join("./", "Dockerfile")
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(dockerfile_content)

        print("Building Docker image...")
        subprocess.run(
            ["docker", "build", "-t", "sphinx_pdf_builder", "./"], check=True
        )

    def run_docker_container(self):
        print("Running Docker container to build PDF...")
        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{os.path.abspath(self.output_dir)}:/output_pdf",
                "sphinx_pdf_builder",
            ],
            check=True,
        )

    def build(self):
        # TODO: remove docker volume and images after completion
        self.fetch_github_repo_url()
        self.build_docker_container()
        self.run_docker_container()

        print(f"PDF should now be available in the output directory: {self.output_dir}")

        os.remove("Dockerfile")


# Usage
if __name__ == "__main__":
    index_url = "https://docs.jupyter.org/en/latest/"
    output_directory = "./output_pdf"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    builder = SphinxPDFBuilder(index_url, output_directory)
    builder.build()
