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
├── .github/                         # GitHub Actions configuration
│   └── workflows/
│       ├── test.yml                # Test workflow
│       └── deploy.yml              # Deployment workflow
├── .gitignore
├── README.md
├── airflow/
│   ├── dags/                       # Unified DAG directory
│   │   ├── __init__.py
│   │   ├── dev/           # Development DAGs (dev branch)
│   │   │   ├── __init__.py
│   │   │   └── new_etl_dag.py
│   │   ├── prod/                 # Production DAGs (main branch)
│   │   │   ├── __init__.py
│   │   │   ├── daily_etl_dag.py
│   │   │   └── weekly_report_dag.py
│   │   └── common/                 # DAGs shared between environments
│   │       ├── __init__.py
│   │       └── dbt_dag.py
│   ├── dev/                        # Development environment configuration
│   │   ├── docker-compose.yaml
│   │   ├── .env.example
│   │   └── logs/
│   ├── prod/                       # Production environment configuration
│   │   ├── docker-compose.yaml
│   │   ├── .env.example
│   │   └── logs/
│   └── common/                     # Shared resources
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── plugins/
│       │   └── __init__.py
│       ├── scripts/
│       │   ├── __init__.py
│       │   ├── set_env.py
│       │   ├── dag_validation.py   # DAG validation script
│       │   └── deploy_to_prod.py   # Deployment script
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
├── tests/                          # Test directory
│   ├── __init__.py
│   ├── conftest.py
│   ├── dags/
│   │   ├── __init__.py
│   │   └── test_dags.py
│   └── dbt/
│       └── test_models.py
├── deployment/                     # Deployment configuration
│   ├── ansible/                    # Ansible deployment scripts
│   │   ├── inventory/
│   │   │   ├── dev
│   │   │   └── prod
│   │   └── playbooks/
│   │       ├── deploy_dev.yml
│   │       └── deploy_prod.yml
│   └── k8s/                       # Kubernetes configuration
│       ├── dev/
│       │   └── values.yaml
│       └── prod/
│           └── values.yaml
└── docs/                          # Project documentation
    ├── architecture.md
    ├── development.md
    └── deployment.md
```

## FREQUENTLY USED COMMANDS

1. Build airflow image
docker build -t airflow-custom:latest . --no-cache

2. Create airflow user
docker compose run airflow-webserver airflow users create \
    --username admin \
    --role Admin \
    --email yokinzou@outlook.com \
    --password admin

3. Connect to airflow postgres in docker 
docker exec -it <airflow-container-id> bash
psql -h postgres -U airflow -d ny_taxi

## DATA SOURCE DESCRIPTION
[Referenced Link](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
### 1. Yellow Taxi
- Operating Area:
  Primarily operates in Manhattan Central Business District (CBD)
  Can pick up and drop off passengers anywhere in the city
  The only taxi service allowed to queue at airports for passenger pickup
- Characteristics:
  The most traditional taxi service
  Can be hailed from the street (Street-hail)
  Uses metered fares
  Strictly limited in number (medallion system)
- Pricing:
  Higher base fare
  Uses standardized pricing

### 2. Green Taxi
- Operating Restrictions:
  Cannot pick up passengers in central Manhattan (below 96th Street)
  Cannot pick up at airports
  Can freely pick up passengers in other areas
- Service Area:
  Primarily serves areas outside Manhattan (Brooklyn, Queens, Bronx, etc.)
  Can pick up and drop off passengers anywhere through pre-arrangement
- Introduction Reason:
  Introduced in 2013 to improve taxi service in outer boroughs
  Addresses the concentration of yellow taxis in Manhattan

### 3. FHV (For-Hire Vehicles)
- Operating Model:
  Can only pick up pre-arranged passengers
  Cannot be hailed from the street
  Typically requires advance booking by phone or app
- Service Types:
  Includes traditional black car services
  Luxury limousine services
  Long-term car rental services
- Pricing Features:
  Price is typically determined before the trip begins
  May offer car or time-based package services

### 4. FHVHV (High-Volume For-Hire Vehicles)
- Representative Companies:
  Uber
  Lyft
  Via
- Characteristics:
  Completely dependent on app-based booking
  Dynamic pricing system
  High-frequency operations
  Flexible supply and demand matching
- Operating Method:
  Drivers can freely choose working hours
  Uses algorithms to match drivers and passengers
  Real-time tracking and rating system

### 5. Key Differences Comparison:
| Feature | Yellow Taxi | Green Taxi | FHV | FHVHV |
|---------|-------------|------------|-----|-------|
| Street Hail | ✅ | ✅ (limited areas) | ❌ | ❌ |
| Pre-arranged Service | ✅ | ✅ | ✅ | ✅ |
| Airport Pickup | ✅ | ❌ | ✅ | ✅ |
| Pricing Mechanism | Fixed meter | Fixed meter | Pre-arranged | Dynamic pricing |
| Payment Method | Cash/Card | Cash/Card | Various | App only |
| Operating Area Restrictions | None | Yes | None | None |

### DATA ANALYTICS INSIGHTS

#### 1. Area Analysis
Market share of different taxi types by area
Service coverage comparison

#### 2. Time Pattern
Peak hour service efficiency comparison
Market share changes across different time periods
Price analysis:
Price comparison for the same route across different services
Peak hour pricing strategy analysis
Service quality:
Wait time comparison
Completion rate analysis
Customer satisfaction comparison
These differences need special attention during data analysis as they affect:
Data integrity and comparability
Interpretation of service patterns
Accuracy of business insights


## DBT USAGE

1. pip install dbt-core dbt-bigquery 
2. cd dbt
3. dbt init project_name
4. dbt run
5. dbt test
6. dbt docs generate
7. dbt docs serve
