FROM apache/airflow:2.10.5-python3.11

USER airflow
COPY --chown=airflow:root pyproject.toml /opt/patchnote/pyproject.toml
COPY --chown=airflow:root src /opt/patchnote/src
# Project deps are installed on top of Airflow's pinned constraints set.
RUN pip install --no-cache-dir /opt/patchnote
