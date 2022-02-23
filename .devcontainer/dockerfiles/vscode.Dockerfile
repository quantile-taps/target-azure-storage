FROM quantiledevelopment/vscode-python:3.9

# Install the Azure cli
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Copy the requirements file
COPY ./requirements.txt /requirements.txt

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

RUN pipx install meltano