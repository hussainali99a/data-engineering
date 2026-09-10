from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="taxi_data_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["taxi", "data-engineering"],
) as dag:

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command="cd /opt/airflow/project && python -m src.load_raw",
    )

    refresh_warehouse = BashOperator(
        task_id="refresh_warehouse",
        bash_command="cd /opt/airflow/project && python -m src.refresh_warehouse",
    )

    run_tests = BashOperator(
        task_id="run_tests",
        bash_command="cd /opt/airflow/project && python -m pytest",
    )

    load_raw >> refresh_warehouse >> run_tests