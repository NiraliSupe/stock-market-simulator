1. Directory structure
2. README
3. Demo
    - different make targets
    - how to start env
    - execute transaction manually
        - stock price post: curl -i -X POST http://localhost:8000/api/stockprice/ -H "Content-Type: application/json" -d @top100.json -H 'Authorization: JWT <token>'
        - transactions: 
                1. {
                        "transaction_type": "buy",
                        "created_at": "2017-04-25T14:37:00Z",
                        "quantity": 100,
                        "ticker": "NFLX",
                        "cash_balance": 1
                }

                2. {
                        "transaction_type": "sell",
                        "created_at": "2017-11-06T14:00:00Z",
                        "quantity": 50,
                        "ticker": "NFLX",
                        "cash_balance": 1
                }

    - upload CSV file
4. Questions