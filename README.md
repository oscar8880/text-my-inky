## Getting Started

### Prerequisites

* A raspberry pi
* python3
* pip3
* A Pimoroni Inky Impression 

### Installation

1. Clone the repo to your pi
2. Copy the example .env file and fill in the missing variables
```sh
cp .env.example .env
```
3. Setup a virtual env
```sh
python3 -m venv venv
```
4. Activate it
```sh
. venv/bin/activate
```
5. Install dependencies
```sh
pip install -r requirements.txt
```
6. Run the flask server
```sh
flask run
```