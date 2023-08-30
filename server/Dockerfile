FROM guigolab/geneid:1.4.5 as geneid

FROM python:3.7.11

RUN apt-get update && apt-get install -y \
    tabix \
    samtools \
    genometools 

WORKDIR /server

ADD . /server

COPY --from=geneid /usr/local/bin/geneid /soft/GeneID/bin/

RUN chmod u+x  /soft/GeneID/bin/

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN chmod +x datasets

EXPOSE ${API_PORT}

CMD ["uwsgi", "app.ini"]





