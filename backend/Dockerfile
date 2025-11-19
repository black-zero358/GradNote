FROM python:3.13-slim

WORKDIR /app/

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安装依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . /app/

# 更改所有权
RUN chown -R appuser:appuser /app

# 切换用户
USER appuser

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8000

# 暴露端口
EXPOSE ${PORT}

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
