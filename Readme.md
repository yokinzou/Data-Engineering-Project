## DATA SOURCE
https://github.com/DataTalksClub/nyc-tlc-data

## GCP DEV ENV
* DEV BUCKET
<img src="/Images/image-1.png" width="500" height="300">

* DEV BIGQUERY
<img src="/Images/image.png" width="500" height="300">

## GCP PROD ENV
* PROD BUCKET
<img src="/Images/image-2.png" width="500" height="300">

* PROD BIGQUERY
<img src="/Images/image-3.png" width="500" height="300">

## PROJECT STRUCTURE
```
project_root/
├── .git/
├── .github/                         # GitHub Actions 配置
│   └── workflows/
│       ├── test.yml                # 测试工作流
│       └── deploy.yml              # 部署工作流
├── .gitignore
├── README.md
├── airflow/
│   ├── dags/                       # 统一的 DAG 目录
│   │   ├── __init__.py
│   │   ├── dev/           # 开发中的 DAG (dev 分支)
│   │   │   ├── __init__.py
│   │   │   └── new_etl_dag.py
│   │   ├── prod/                 # 生产 DAG (main 分支)
│   │   │   ├── __init__.py
│   │   │   ├── daily_etl_dag.py
│   │   │   └── weekly_report_dag.py
│   │   └── common/                 # 两个环境共享的 DAG
│   │       ├── __init__.py
│   │       └── dbt_dag.py
│   ├── dev/                        # 开发环境配置
│   │   ├── docker-compose.yaml
│   │   ├── .env.example
│   │   └── logs/
│   ├── prod/                       # 生产环境配置
│   │   ├── docker-compose.yaml
│   │   ├── .env.example
│   │   └── logs/
│   └── common/                     # 共享资源
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── plugins/
│       │   └── __init__.py
│       ├── scripts/
│       │   ├── __init__.py
│       │   ├── set_env.py
│       │   ├── dag_validation.py   # DAG 验证脚本
│       │   └── deploy_to_prod.py   # 部署脚本
│       └── config/
│           ├── env_config.yaml
│           ├── dev_config.py
│           └── prod_config.py
├── dbt/
│   ├── profiles.yml
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── macros/
│   ├── tests/
│   ├── analysis/
│   ├── snapshots/
│   └── seeds/
├── tests/                          # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── dags/
│   │   ├── __init__.py
│   │   └── test_dags.py
│   └── dbt/
│       └── test_models.py
├── deployment/                     # 部署配置
│   ├── ansible/                    # Ansible 部署脚本
│   │   ├── inventory/
│   │   │   ├── dev
│   │   │   └── prod
│   │   └── playbooks/
│   │       ├── deploy_dev.yml
│   │       └── deploy_prod.yml
│   └── k8s/                       # Kubernetes 配置
│       ├── dev/
│       │   └── values.yaml
│       └── prod/
│           └── values.yaml
└── docs/                          # 项目文档
    ├── architecture.md
    ├── development.md
    └── deployment.md
```

## FREQIENTLY USED COMMANDS

1. Build airflow image
docker build -t airflow-custom:latest . --no-cache

2. Create airflow user
docker compose run airflow-webserver airflow users create \
    --username admin \
    --role Admin \
    --email yokinzou@outlook.com \
    --password admin