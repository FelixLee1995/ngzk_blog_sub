FROM python:3.7
RUN mkdir -p /app/
ADD ./* /app/
WORKDIR /app/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD [ "python3", "./main.py" ]