FROM python:3.9.1

WORKDIR ./ssp
# This helps no save packages in cache and don't install every time code changed (COPY . .)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "run.py"]
EXPOSE 5000

