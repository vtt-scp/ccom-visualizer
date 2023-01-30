# ========== Python builder ==========
FROM python:3.11-slim AS python

ENV PIP_NO_CACHE_DIR=1

# Setup virtual environment and upgrade pip
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip

# Install requirements
COPY requirements/app.txt requirements.txt
RUN /opt/venv/bin/pip install -r requirements.txt

# ========== Final image ==========
FROM python:3.11-slim AS final

WORKDIR /code

# Copy Python venv with requirements installed
COPY --from=python /opt /opt
# Set virtualenv path as Python path
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy required project files
COPY main.py .

# Set environment variables so that Python prints are visible
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Run service
CMD python main.py