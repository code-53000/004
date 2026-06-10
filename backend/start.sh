#!/bin/bash

echo "开始初始化数据..."
python init_data.py

echo "启动后端服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
