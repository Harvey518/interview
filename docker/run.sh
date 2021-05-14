#!/bin/bash
pip install --upgrade pip && pip install -i https://mirrors.aliyun.com/pypi/simple/ -r /docker/requirements.txt

python /app/interview_token.py
