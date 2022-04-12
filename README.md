# Stock Market Simulator   

This is a stock market simuator written in Python, using Django framework with Postgres. 
The backend web server of this simulator allows to create multiple user account and for each account it maintains a stock portfolio. In the portfolio user can add the trades (stock buy and sell) from the year 2017. To calculate the portfolio value on any date of 2017, it uses daily stock price data of 100 stocks from S&P 500. All the trades in this simulator are constrained by the cash balance on that day and the portfolio starts (on Jan, 1st 2017) with no stocks and $100,000 cash balance.

## Workflow
After authentication user can add buy and sell trades the portfolio. These trades are stored in transaction table. While recording the trades, the codes checks for the validity of the transaction. Some of these cases are shown in the follwoing flow chart (e.g. reported transaction is on a weekday, the buy order can be satisfied by the current cash balance etc.).   

### Transaction and position table   
Once the trade is added to the transaction table it updates the position table. The transaction table is collection of all the descrete events of buy and sell of the stocks. The position table stores user's non-zero postion in stock (short sell or fractional stock trading not included). The position table indicates the current position the user has on a given day. This is used in the Evaluate API for calculate the portfolio value on any given day in 2017. (Note: for portfolio value calculation the closing price of the stock on the requested date is used)   

### Cash transaction and Cash balance table   
Similar to the transaction table, cash transaction table stores all the effects of stock trading. This table is kept separate from the original transaction table to add new features in future (e.g. adding dividends issued, capital gain/loss etc). Effects of cash trasactions are reported to the cash balance table. The value of cash balance is checked everytime buy trade is added to the trasaction table. Also cash balance is used to calculate the portfoilio value for the Evaluate API.

<img src="./assets/StockSimulator-flowChart.drawio.png" alt="flowchart" width="80%"/>   


## Stock-simulator tables  

<img src="./assets/StockSimulator-tables.drawio.png" alt="tables" width="80%"/>   

## Evaluate API
Portfolio value calculation:   
<img src="./assets/StockSimulator-EvaluateAPI.drawio.png" alt="equation" width="80%"/>   

## Prerequisites:
- Docker
- Docker compose

This repository contains 2 services:
- **Backend:** API written using Django REST Framework.
- **DB:** Postgres database to store user, transaction, position and cash balance information

## Environment

The following steps can be used to setup a full development environment.

**Currently, server in the container is bound to port 8000. Please update the line 21 in docker-compose file to change the binding as needed.**

| Commands             |      Description                                                                               |
|----------------------|------------------------------------------------------------------------------------------------|
| make build           | Performs a docker-compose build to build the docker images used in this environment.           |
| make up              | Starts the services provided by this microservice such as the database and API backend.        |
| make migrate         | Creates the database migration files and performs database migrations from the django backend. |
| make down            | Stops a running development environment.                                                       |


Additional Commands: 
| Commands             |      Description                                             |
|----------------------|--------------------------------------------------------------|
| make build-clean     | Build the-no-cache images to prepare for runtime.            |
| make shell           | Connect to a bash shell on the backend django container.     |
| make psql            | Connect to stock simulator database as DB user postgres.     |
| make up-new          | Removes the database volume and starts a clean environment.  |
| make createsuperuser | Creates credentials to login to API.                         |
| make obtain-token    | Provides JSON web token.                                     |


## API

| Endpoint                 |  Description                                                    |
|--------------------------|-----------------------------------------------------------------|
| api/obtain-token/        | Pass in the user's username and password to obtain auth token. |
| api/refresh-token/       | Pass in an existing token to the refresh endpoint ({"token": EXISTING_TOKEN}). Only non-expired tokens will work. The JsON response looks the same as the normal obtain token endpoint. |
| api/verify-token/        | Pass in an existing token and it will return a 200 response and the token if it is valid. Otherwise, it will return a 400 Bad Request as well as an error identifying why the token was invalid. |
| api/cash-balance/        | API endpoint that allows CRUD operations on cash balance for the user. |
| api/transaction/         | API endpoint that allows to create or view the stock transaction. This create method also adds record in position and cash-transaction table. |
| api/position/            | API endpoint that allows to view stock positions for the user.
| api/cash-transaction/    | API endpoint that allows to view stock cash transactions for the user.     |
| api/evaluate/            | API endpint that shows the value of a portfolio for given a date in 2017.  |
| api/upload-trade/by-file | API endpoint that allows upload a CSV file with transactions.              |

## Authentication

### Obtain JWT token:

``` sh
$ export USERNAME=<username>
$ export PASSWORD=<password>

$ curl -X POST http://localhost:8000/api/obtain-token/ -H 'content-type: application/x-www-form-urlencoded' -d "username=$USERNAME&password=$PASSWORD"

$ {"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjQ5MTI3MTE1LCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjQ4NTIyMzE1fQ.NaBYNC8XUdwykYPqLw7tKGtlqkdmRR26GDdQiGPiwrw"}
```
### Refresh token:

``` sh
curl -X POST http://localhost:8000/api/refresh-token/ -H 'Content-Type: application/json' -d '{"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjQ5MTI3MTE1LCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjQ4NTIyMzE1fQ.NaBYNC8XUdwykYPqLw7tKGtlqkdmRR26GDdQiGPiwrw"}'
```
A new token comes back:
```
$ {"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjQ5MTI3NDExLCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjQ4NTIyMzE1fQ.LrAnW6eFdjUF6FYEsoWqWhS02v4nQXF-NMX4MFWl9dc"}
```

### Verify token 
``` sh
curl -X POST http://localhost:8000/api/verify-token/ -H 'Content-Type: application/json' -d '{"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjQ5MTI3NDExLCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjQ4NTIyMzE1fQ.LrAnW6eFdjUF6FYEsoWqWhS02v4nQXF-NMX4MFWl9dc"}'
```
The same token comes back:
```
{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjQ5MTI3NDExLCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjQ4NTIyMzE1fQ.LrAnW6eFdjUF6FYEsoWqWhS02v4nQXF-NMX4MFWl9dc"}
```

## API Access Examples:

Use the token obtainin the section `Obtain JWT token` for authentication. 

### Stock Price

**POST:** upload stock records from the provided json file
```
$ curl -i -X POST http://localhost:8000/api/stockprice/ -H "Content-Type: application/json" -d @top100.json -H 'Authorization: JWT <token>'
```

**GET:** 
```
$ curl http://localhost:8000/api/stockprice/ -H 'Authorization: JWT <token>'

$ {"count":25100,"next":"http://localhost:8000/api/stockprice/?page=2","previous":null,"results":[{"id":1,"date":"2017-01-03","open":115.8,"close":116.15,"low":114.76,"high":116.33,"volume":28781865,"ticker":1},{"id":2,"date":"2017-01-04","open":115.85,"close":116.02,"low":115.75,"high":116.51,"volume":21118116,"ticker":1},{"id":3,"date":"2017-01-05","open":115.92,"close":116.61,"low":115.81,"high":116.8642,"volume":22193587,"ticker":1},{"id":4,"date":"2017-01-06","open":116.78,"close":117.91,"low":116.47,"high":118.16,"volume":31751900,"ticker":1},{"id":5,"date":"2017-01-09","open":117.95,"close":118.99,"low":117.94,"high":119.43,"volume":33561948,"ticker":1},{"id":6,"date":"2017-01-10","open":118.77,"close":119.11,"low":118.3,"high":119.38,"volume":24462051,"ticker":1},{"id":7,"date":"2017-01-11","open":118.74,"close":119.75,"low":118.6,"high":119.93,"volume":27588593,"ticker":1},{"id":8,"date":"2017-01-12","open":118.895,"close":119.25,"low":118.21,"high":119.3,"volume":27086220,"ticker":1},{"id":9,"date":"2017-01-13","open":119.11,"close":119.04,"low":118.81,"high":119.62,"volume":26111948,"ticker":1},{"id":10,"date":"2017-01-17","open":118.34,"close":120.0,"low":118.22,"high":120.24,"volume":34439843,"ticker":1}, ...
```

### CashBalance:

**POST:** creates cash balance for the user with default $100,000.
```
$ curl -i -X POST http://localhost:8000/api/cash-balance/ -H "Content-Type: application/json" -H 'Authorization: JWT <token>'

{"id":1,"amount":100000.0,"created_at":"2022-03-29T04:02:30.208986Z","object_updated_at":"2017-01-01"}
```

**GET:**

```
$ curl http://localhost:8000/api/cash-balance/ -H 'Authorization: JWT <token>'

$ [{"id":1,"amount":100000.0,"created_at":"2022-03-29T04:02:30.208986Z","object_updated_at":"2017-01-01T00:00:00Z"}]
```

### Transaction:

**POST:**
To buy 10 stocks of AAPL:
```
$ curl -i -X POST http://localhost:8000/api/transaction/ -H "Content-Type: application/json" -d '{ "transaction_type": "buy", "created_at": "2017-05-08T14:37:00Z", "quantity": 10, "ticker": "AAPL", "cash_balance": 1}' -H 'Authorization: JWT <token>'

$ {"id":1,"ticker_name":"AAPL","transaction_type":"buy","amount":1510.1999999999998,"created_at":"2017-05-08T14:37:00Z","quantity":10,"cash_balance":1}
```

To sell 2 stocks of AAPL:
```
$ curl -i -X POST http://localhost:8000/api/transaction/ -H "Content-Type: application/json" -d '{ "transaction_type": "sell", "created_at": "2017-05-10T14:37:00Z", "quantity": 2, "ticker": "AAPL", "cash_balance": 1}' -H 'Authorization: JWT <token>'

$ {"id":2,"ticker_name":"AAPL","transaction_type":"sell","amount":306.89,"created_at":"2017-05-10T14:37:00Z","quantity":2,"cash_balance":1}
```

**GET:**
```
$ curl http://localhost:8000/api/transaction/ -H 'Authorization: JWT <token>'

$ [
    {
        "id":2,
        "ticker_name":"AAPL",
        "transaction_type":"sell",
        "amount":306.89,
        "created_at":"2017-05-10T14:37:00Z",
        "quantity":2,
        "cash_balance":1
    },
    {
        "id":1,
        "ticker_name":"AAPL",
        "transaction_type":"buy",
        "amount":1510.2,
        "created_at":"2017-05-08T14:37:00Z",
        "quantity":10,
        "cash_balance":1
    }
  ]
```

### Position:

**GET:**
```
$ curl http://localhost:8000/api/position/ -H 'Authorization: JWT <token>'

$ {
    "count":2,
    "next":null,
    "previous":null,
    "results":
        [
            {
                "id":2,
                "ticker":"AAPL",
                "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-10\", \"upper\": null}",
                "quantity":8,
                "cash_balance":1
            },
            {
                "id":1,
                "ticker":"AAPL",
                "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-08\", \"upper\": \"2017-05-10\"}","quantity":10,
                "cash_balance":1
            }
        ]
    }
```

### Cash Balance Transaction:

**GET:**
```
$ curl http://localhost:8000/api/cash-transaction/ -H 'Authorization: JWT <token>'

$ {
    "count":3,
    "next":null,
    "previous":null,
    "results":[
        {
            "id":3,
            "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-10\", \"upper\": null}",
            "amount":98796.69,
            "cash_balance":1
        },
        {
            "id":2,
            "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-08\", \"upper\": \"2017-05-10\"}","amount":98489.8,
            "cash_balance":1
        },
        {
            "id":1,
            "date":"{\"bounds\": \"[)\", \"lower\": \"2017-01-01\", \"upper\": \"2017-05-08\"}","amount":100000.0,
            "cash_balance":1
        }
    ]
}
```

### Evaluate:

To check portfolio value for the given day:

```
$ curl http://localhost:8000/api/evaluate/?date=2017-05-31 -H 'Authorization: JWT <token>'

$ {
    "results":
    [
        {
            "id":2,
            "ticker":"AAPL",
            "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-10\", \"upper\": null}",
            "quantity":8,
            "cash_balance":1
        },
        {
            "id":3,
            "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-10\", \"upper\": null}",
            "amount":98796.69,
            "cash_balance":1
        }
    ],
    "total($)": 100018.77
}
```

```
$ curl http://localhost:8000/api/evaluate/?date=2017-05-08 -H 'Authorization: JWT <token>'

$ {
    "count":1,
    "next":null,
    "previous":null,
    "results":
        [
            {
                "id":1,
                "ticker":"AAPL",
                "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-08\", \"upper\": \"2017-05-10\"}",
                "quantity":10,
                "cash_balance":1
            },
            {
                "id":2,
                "date":"{\"bounds\": \"[)\", \"lower\": \"2017-05-08\", \"upper\": \"2017-05-10\"}",
                "amount":98489.8,
                "cash_balance":1
            }
        ],
        "total($)": 100019.9
    }
```

```
$ curl http://localhost:8000/api/evaluate/?date=2017-05-05 -H 'Authorization: JWT <token>'

$ {
    "results": [
        {
            "id": 1,
            "date": "{\"bounds\": \"[)\", \"lower\": \"2017-01-01\", \"upper\": \"2017-05-08\"}",
            "amount": 100000.0,
            "cash_balance": 1
        }
    ],
    "total($)": 100000.0
}
```

### Upload by File:

<img src="./assets/upload-csv-endpoint.png" alt="upload" width="80%"/>   