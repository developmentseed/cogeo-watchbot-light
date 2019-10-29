FROM remotepixel/amazonlinux:gdal3.0-py3.7-cogeo

ENV PYTHONUSERBASE=/var/task

################################################################################
#                            CREATE PACKAGE                                    #
################################################################################
COPY app app
COPY setup.py setup.py
COPY README.md README.md

RUN pip3 install . --user
RUN rm -rf app setup.py README.md

RUN mv ${PYTHONUSERBASE}/lib/python3.7/site-packages/* ${PYTHONUSERBASE}/
RUN rm -rf ${PYTHONUSERBASE}/lib

# Leave module precompiles for faster Lambda startup
RUN find ${PYTHONUSERBASE}/ -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[2-3][0-9]//'); cp $f $n; done;
RUN find ${PYTHONUSERBASE}/ -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find ${PYTHONUSERBASE}/ -type f -a -name '*.py' -print0 | xargs -0 rm -f

RUN cd $PYTHONUSERBASE && zip -r9q /tmp/package.zip *
