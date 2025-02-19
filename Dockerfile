# Use the official Python base image
FROM python:3.13

RUN pip install setuptools

# Set the working directory in the container
WORKDIR /app

# Download ta-lib C library from source
RUN wget https://github.com/TA-Lib/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz
RUN tar -xvf ta-lib-0.4.0-src.tar.gz
WORKDIR /app/ta-lib
RUN ./configure --prefix=/usr --build=`/bin/arch`-unknown-linux-gnu
RUN make
RUN make install
# RUN pip install --no-cache-dir TA-Lib

# Copy all files from the current directory to the working directory in the container
COPY . .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script
CMD ["python", "main.py"]