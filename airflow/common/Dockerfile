# 基础镜像
FROM apache/airflow:2.10.4

ENV AIRFLOW_HOME=/opt/airflow

# 使用root用户安装系统依赖
USER root
RUN echo "deb http://security.debian.org/debian-security bullseye-security main contrib non-free" > /etc/apt/sources.list.d/debian-security.list && \
    apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    vim \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录
RUN mkdir -p /opt/dbt && \
    mkdir -p /opt/airflow/dags && \
    mkdir -p /opt/airflow/dags && \
    mkdir -p /opt/airflow/scripts && \
    mkdir -p /opt/airflow/configs && \
    mkdir -p /opt/airflow/google/credentials && \

    chown -R airflow:root /opt/dbt /opt/airflow/dags /opt/airflow/scripts /opt/airflow/google/credentials && \
    chmod -R g+rw /opt/dbt /opt/airflow/dags /opt/airflow/scripts /opt/airflow/google/credentials

# 安装 Google Cloud SDK
ARG CLOUD_SDK_VERSION=458.0.0
ENV GCLOUD_HOME=/opt/google-cloud-sdk
ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

# 使用root用户创建目录并设置权限
RUN mkdir -p /home/airflow/.local/lib/python3.12/site-packages && \
    chmod -R 777 /home/airflow/.local && \
    chown -R airflow:root /home/airflow/.local

# 切换到 airflow 用户安装 Python 包
USER airflow

# 升级 pip
RUN pip install --upgrade pip

# 安装 DBT 相关包
RUN pip install --no-cache-dir \
    dbt-postgres==1.7.3 \
    dbt-bigquery==1.7.3 \
    dbt-core==1.7.3 \
    pyyaml

# 复制并安装其他 Python 依赖
COPY --chown=airflow:root requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# # 复制脚本和配置文件（如果有的话）
# COPY --chown=airflow:root scripts /opt/airflow/scripts/

# 只有当目录不为空时才执行 chmod
RUN [ "$(ls -A /opt/airflow/scripts/)" ] && chmod +x /opt/airflow/scripts/* || true

WORKDIR $AIRFLOW_HOME


# 设置默认用户
USER ${AIRFLOW_UID:-50000}
