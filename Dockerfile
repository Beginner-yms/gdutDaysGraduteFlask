# 将官方 Python 运行时用作父镜像
FROM python:3.7
# 工作目录
WORKDIR ./index

COPY requirements.txt ./

# 换源
# 更新
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple \
    && pip config set install.trusted-host mirrors.aliyun.com \
    && pip install -U pip \
    ## 下载依赖
    && pip3 install -r requirements.txt
# RUN /usr/local/bin/python -m pip install --upgrade pip

COPY . .

# 设置环境变量
#ENV NAME GdutDayFlask

# 设置启动命令
CMD ["python3","./index/flaskMain.py"]

