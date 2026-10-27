FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-tk python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=TkAgg

WORKDIR /app
COPY viewer.py .
CMD ["python3", "viewer.py"]
