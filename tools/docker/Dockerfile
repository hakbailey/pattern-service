FROM registry.access.redhat.com/ubi9/ubi:latest AS base

ARG USER_ID=${USER_ID:-1001}
ARG PYTHON_BIN="python3.11"

RUN useradd --uid "$USER_ID" --gid 0 --home-dir /app --create-home pattern \
    && mkdir -p /app/.local \
    && chown -R "${USER_ID}:0" /app \
    && chmod 0775 /app

RUN dnf -y install dnf-plugins-core git \
    && dnf -y install ${PYTHON_BIN} ${PYTHON_BIN}-devel ${PYTHON_BIN}-pip\
    && dnf -y clean all \
    && rm -rf /var/cache/dnf

USER "$USER_ID"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/app/.local/bin:$PATH" \
    VIRTUAL_ENV=/app/venv

RUN ${PYTHON_BIN} -m venv "$VIRTUAL_ENV"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

WORKDIR /app

COPY requirements/requirements.txt requirements.txt

RUN ${PYTHON_BIN} -m pip install -r requirements.txt

COPY . .

FROM base AS dispatcher-image

CMD ["python", "manage.py", "run_dispatcher"]

FROM base AS pattern-service-image

EXPOSE 5000

RUN ["python", "manage.py", "migrate"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
