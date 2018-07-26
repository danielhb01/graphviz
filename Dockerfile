FROM python:3.5-alpine

RUN apk add --no-cache graphviz
RUN apk add --update curl gcc g++ && rm -rf /var/cache/apk/*
RUN apk add --no-cache xdg-utils
RUN apk --no-cache add msttcorefonts-installer fontconfig && \
	update-ms-fonts && \ 
	fc-cache -f

WORKDIR /home/graphviz

RUN mkdir static

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY background.jpg ./static/

EXPOSE 5000

CMD ["python3","-u","app.py"]
