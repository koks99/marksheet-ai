# MSAi: Marksheet Analysis and Storage using AI

Our server:

(add link)


> Note: The server can't handle heavy traffic, its for dev purposes only.

## Table of Contents

- [Setup](#Setup)
- [Usage](#Usage)

## Setup

*The instructions below are for Linux only and have been tested on Ubuntu 20.04 or later.*

### Via Docker:

1. Build a Docker Image:

```sudo docker build -t deploy-msai .```

2. Run a Docker container:

```sudo docker run -p 8000:8000 deploy-msai```

### Without Docker:

1. Upgrade pip and install Python dependencies:

```pip install --no-cache-dir --upgrade -r requirements.txt && pip install "pymongo[srv]"```

2. Install system-wide packages:

```apt-get install -y --fix-missing tesseract-ocr```

3. Run a local server:

```uvicorn main:app --host 127.0.0.1 --port 8000```


## Usage

1. Click *Start Analysing*.
2. Upload the Marksheet (PNG/JPG).
3. Verify the data in next and Click *Store Extracted Data*.
4. Login/Register for Data privacy options.
5. Use the Search bar to fetch the stored data