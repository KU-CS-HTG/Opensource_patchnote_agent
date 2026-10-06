FROM apache/airflow:2.10.5-python3.11
USER airflow
COPY --chown=airflow:root pyproject.toml /opt/opsgraph/pyproject.toml
COPY --chown=airflow:root src /opt/opsgraph/src
RUN pip install --no-cache-dir /opt/opsgraph
