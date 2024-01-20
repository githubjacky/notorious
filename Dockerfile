FROM python:3.11.4-bookworm

ARG UID
ARG GID
ARG USER

# Update the package list, install sudo, create a non-root user, and grant password-less sudo permissions
RUN groupadd --gid $GID $USER \
    && useradd --uid $UID --gid $GID -m $USER \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USER ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER \
    && chmod 0440 /etc/sudoers.d/$USER

# no need to create virtual environment since the docker containr is already is
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

# dependencies to install poetry and set up ODBC
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential

RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.6.0
COPY pyproject.toml ./
RUN poetry install
EXPOSE 8891

USER $USER
WORKDIR /home/$USER/notorious_cls

CMD ["bash"]
