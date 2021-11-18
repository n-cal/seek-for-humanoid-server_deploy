# Seek For Humanoid - server (deploy)

This is the deploy version of Seek For Humanoid server. 

## Run and Testing

### Prerequisites

To run the app locally you need these tools:

- Python 3.9.5 installed
- Poetry 1.1.11 installed
- a fakeJSON token
- a PostgreSQL database configured
- an AWS S3 account

## Run

After you have cloned the project cd into the created folder and install the dependencies:

```
$ poetry install
```

Create a .env file like the following:

```
export DJANGO_SECRET_KEY=<YOUR_DJANGO_APP_SECRET_KEY>

export FAKE_JSON_TOKEN=<YOUR_FAKE_JSON_TOKEN>

export DB_NAME=<YOUR_DATABASE_NAME>
export DB_HOST=<YOUR_DATABASE_HOST>
export DB_PORT=<YOUR_DATABASE_PORT>
export DB_USER=<YOUR_DATABASE_USER>
export DB_PASSWORD=<YOUR_DATABASE_PASSWORD>


export AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<YOUR_AWS_ACCESS_KEY>
export AWS_STORAGE_BUCKET_NAME=<YOUR_AWS_BUCKET_NAME>
export AWS_S3_REGION_NAME=<YOUR_AWS_REGION>
```

create the database:

```
$ source .env && poetry run python manage.py migrate
```

Now run the following command to populate the database with humanoids and download the images for each profile:

```
$ source .env && poetry run python manage.py pullhumanoids
```

then you can run the server and test the API:

```
$ source .env && poetry run python manage.py runserver
```

## Test

```
$ source .env && poetry run python manage.py test