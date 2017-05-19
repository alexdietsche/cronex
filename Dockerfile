FROM python:3

# Set working directory
WORKDIR /

# Add files
COPY /App/main.py /App/
COPY /res/ticker.txt /res/

# install libraries
RUN pip install --no-cache-dir quandl
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir datetime

# run script
CMD ["python", "/App/main.py"]
