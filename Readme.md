## DATA SOURCE
https://github.com/DataTalksClub/nyc-tlc-data



## GCP DEV ENV
* DEV BUCKET
<img src="/Images/image-1.png" width="700" height="380">

* DEV BIGQUERY
<img src="/Images/image.png" width="700" height="380">

## GCP PROD ENV
* PROD BUCKET
<img src="/Images/image-2.png" width="700" height="380">

* PROD BIGQUERY
<img src="/Images/image-3.png" width="700" height="380">

## AIRFLOW DEV
<img src="/Images/image-4.png" width="700" height="380">

## AIRFLOW PROD
<img src="/Images/image-5.png" width="700" height="380">

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

3.connect to airflow postgres in docker 
docker exec -it <airflow-container-id> bash
psql -h postgres -U airflow -d ny_taxi

## DATA SOURCE DISCRIPTION
[Referenced Link](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
### 1. Yellow Taxi（黄色出租车）
- 运营区域：
主要在曼哈顿核心商业区（Manhattan Central Business District, CBD）运营
可以在全市任何地方接送客人
是唯一被允许在机场排队等候接客的出租车
- 特点：
最传统的出租车服务
可以路边扬招（Street-hail）
使用计价表计费
数量有严格限制（medallion系统）
- 价格：
起步价较高
使用统一的计价标准

### 2. Green Taxi（绿色出租车）
- 运营限制：
不能在曼哈顿中心区域（下城96街以下）接客
不能在机场接客
可以在其他区域自由接客
- 服务区域：
主要服务于曼哈顿以外的区域（布鲁克林、皇后区、布朗克斯等）
可以通过预约在任何地方接送客人
- 引入原因：
2013年引入，为了改善外围区域的出租车服务
解决黄色出租车集中在曼哈顿的问题

### 3. FHV（For-Hire Vehicles）
- 运营模式：
只能通过预约接客
不能路边扬招
通常需要提前电话或APP预约
- 服务类型：
包括传统的黑车服务
豪华轿车服务
长期租车服务
- 价格特点：
价格通常在行程开始前确定
可能提供包车或包时服务

### 4. FHVHV（High-Volume For-Hire Vehicles）
- 代表公司：
Uber
Lyft
Via
- 特点：
完全依赖APP预约
动态定价系统
高频次运营
灵活的供需匹配
- 运营方式：
司机可以自由选择工作时间
使用算法进行司机和乘客匹配
实时追踪和评价系统

### 5. 主要区别对比：
| 特征 | Yellow Taxi | Green Taxi | FHV | FHVHV |
|------|-------------|------------|-----|--------|
| 路边扬招 | ✅ | ✅（限定区域） | ❌ | ❌ |
| 预约服务 | ✅ | ✅ | ✅ | ✅ |
| 机场接客 | ✅ | ❌ | ✅ | ✅ |
| 价格机制 | 固定计价表 | 固定计价表 | 预先约定 | 动态定价 |
| 支付方式 | 现金/卡 | 现金/卡 | 多样化 | 仅APP支付 |
| 运营区域限制 | 无 | 有 | 无 | 无 |

### DATA ANALYTICS INSIGHTS

#### 1. Area Analysis
不同类型出租车在各区域的市场份额
服务覆盖率对比

#### 2. Time Pattern
高峰期服务效率对比
不同时段的市场占有率变化
价格分析：
相同路线不同服务的价格对比
高峰期定价策略分析
服务质量：
等待时间对比
完成率分析
客户满意度对比
这些差异在数据分析时需要特别注意，因为它们会影响到：
数据的完整性和可比性
服务模式的解释
商业洞察的准确性 