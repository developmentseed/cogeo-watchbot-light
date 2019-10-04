FROM remotepixel/amazonlinux:gdal3.0-py3.7-build

WORKDIR /tmp

ENV PACKAGE_PREFIX /tmp/python

RUN pip install --upgrade pip
RUN pip install cython==0.28

################################################################################
#                            CREATE PACKAGE                                    #
################################################################################
COPY app app
COPY setup.py setup.py
COPY README.md README.md

RUN pip3 install . git+https://github.com/developmentseed/cogeo-mosaic  --no-binary numpy,shapely,rasterio -t $PACKAGE_PREFIX -U

################################################################################
#                            REDUCE PACKAGE SIZE                               #
################################################################################
RUN rm -rdf $PACKAGE_PREFIX/boto3/ \
  && rm -rdf $PACKAGE_PREFIX/botocore/ \
  && rm -rdf $PACKAGE_PREFIX/docutils/ \
  && rm -rdf $PACKAGE_PREFIX/dateutil/ \
  && rm -rdf $PACKAGE_PREFIX/jmespath/ \
  && rm -rdf $PACKAGE_PREFIX/s3transfer/ \
  && rm -rdf $PACKAGE_PREFIX/numpy/doc/ \
  && rm -rdf $PREFIX/share/doc \
  && rm -rdf $PREFIX/share/man

# Leave module precompiles for faster Lambda startup
RUN find $PACKAGE_PREFIX -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[2-3][0-9]//'); cp $f $n; done;
RUN find $PACKAGE_PREFIX -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find $PACKAGE_PREFIX -type f -a -name '*.py' -print0 | xargs -0 rm -f

################################################################################
#                              CREATE ARCHIVE                                  #
################################################################################
RUN cd $PACKAGE_PREFIX && zip -r9q /tmp/package.zip *
RUN cd $PREFIX && zip -r9q --symlinks /tmp/package.zip lib/*.so* share

# Cleanup
RUN rm -rf $PACKAGE_PREFIX
