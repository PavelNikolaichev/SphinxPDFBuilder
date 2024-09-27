import os
import requests
import subprocess
from bs4 import BeautifulSoup


class SphinxPDFBuilder:
    def __init__(self, index_url, output_dir):
        """
        SphinxPDFBuilder class to fetch Sphinx documentation and build it into a PDF using Docker.

        :param index_url: The URL of the Sphinx documentation index page.
        :param output_dir: The directory where the PDF will be saved.
        """

        self.index_url = index_url
        self.output_dir = output_dir
        self.repo_url = None
        self.repo_dir = "cloned_repo"

    def fetch_github_repo_url(self):
        """
        A function to fetch the GitHub repository URL from the documentation index page.
        """
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
        """
        A function to generate a Dockerfile and build a Docker container to build the PDF.
        """
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

        RUN git clone {self.repo_url} ./docs --depth 1

        WORKDIR /home/dockeruser/docs

        # Install any requirements if they exist
        RUN [-f ./pre-requirements.txt ] && pip install -r ./pre-requirements.txt || echo "No requirements file found"
        RUN [ -f ./requirements.txt ] && pip install -r ./requirements.txt || echo "No requirements file found"
        
        # Build the EPUB using Sphinx in /docs
        # TODO: use LLM to choose the correct folder or stop the build if there are none

        ARG FOLDER
        RUN if test -d "/home/dockeruser/docs/docs"; then \
                FOLDER="/home/dockeruser/docs/docs"; \
            elif test -d "/home/dockeruser/docs/doc"; then \
                FOLDER="/home/dockeruser/docs/doc"; \
            else \
                echo "Neither 'docs' nor 'doc' exists!" && exit 1; \
            fi && \
                ([ -f $FOLDER/doc-requirements.txt ] && pip install -r $FOLDER/doc-requirements.txt) || \
                ([ -f $FOLDER/requirements.txt ] && pip install -r $FOLDER/requirements.txt) && \
                test -d $FOLDER && cd $FOLDER && make epub BUILDDIR=./_build && \
                ebook-convert $FOLDER/_build/epub/*.epub $FOLDER/_build/epub/output.pdf && \
                cp $FOLDER/_build/epub/output.pdf /home/dockeruser/output.pdf

        USER root
        CMD ["cp", "/home/dockeruser/output.pdf", "/output_pdf/output.pdf"]
        """
        dockerfile_path = os.path.join("./", "Dockerfile")
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(dockerfile_content)

        print("Building Docker image...")
        subprocess.run(
            ["docker", "build", "-t", "sphinx_pdf_builder", "./"], check=True
        )

    def run_docker_container(self):
        """
        A function to run the Docker container to build the PDF.
        """

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
        """
        Fetches the GitHub repository URL, builds the Docker container, and runs it to build the PDF.
        """

        self.fetch_github_repo_url()
        self.build_docker_container()
        self.run_docker_container()

        print(f"PDF should now be available in the output directory: {self.output_dir}")

        os.remove("Dockerfile")

        subprocess.run(["docker", "rmi", "sphinx_pdf_builder"], check=True)


if __name__ == "__main__":
    index_url = "https://docs.djangoproject.com/en/5.1/"
    output_directory = "./output_pdf"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    builder = SphinxPDFBuilder(index_url, output_directory)
    builder.build()
