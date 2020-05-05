FROM lambgeo/lambda:gdal2.4-py3.7-geolayer

WORKDIR /tmp

ENV PYTHONUSERBASE=/var/task

COPY app app
COPY setup.py setup.py

RUN pip install . --user
RUN rm -rf app setup.py README.md

ENV TMPPATH=${PYTHONUSERBASE}/lib/python3.7/site-packages/

# Leave module precompiles for faster Lambda startup
RUN find ${TMPPATH} -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[2-3][0-9]//'); cp $f $n; done;
RUN find ${TMPPATH} -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find ${TMPPATH} -type f -a -name '*.py' -print0 | xargs -0 rm -f

RUN cd ${TMPPATH} && zip -r9q /tmp/package.zip *
