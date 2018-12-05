# Billing 
Project build with Django 2.

A project implement base billing operations as:
- register new user with wallet (USD, EUR, CAD, CNY)
- create exchange rates on date to USD
- refill wallets
- transfer money between wallets with direct or 2 step (USD) conversion
- view or download report of operations on wallets

### Requirements:
1. Docker: https://store.docker.com/editions/community/docker-ce-desktop-mac
2. Docker-compose: ```pip install docker-compose```
 
### Run develop server:
Build and run project.  
```docker-compose up```

### Run tests and linters:
Build and run project.  
```docker-compose run --rm django python manage.py test```  
```docker-compose run --rm django flake8```

### Load fixtures in order to save time.
```docker-compose run --rm django python manage.py loaddata dump```

### Admin access:
url: /admin/
if you load fixtures use ```user1/fake_password``` as credentials or run  
```docker-compose run --rm django python manage.py createsuperuser```

### Example of project usage:

## 1. Register new user
```
POST /users/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
	"username": "myuser",
	"name": "Александр Процко",
	"country": "Россия",
	"city": "Москва",
	"password": 12345,
	"wallet": {
		"currency": "USD"
	}
}
```

## 2. Create exchange rate
```
POST /rates/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
	"date": "2018-12-06",
	"rate": 1.13,
	"source_currency": "EUR"
}
```

## 3. Refill wallet by id
```
PUT /wallets/{wallet_id}/refill/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
    "amount": 150,
    "currency": "USD"
}
```

## 4. Transfer money between wallets
```
POST /wallets/{wallet_id}/transfer/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
	"target_wallet_id": "2",
	"amount": 25
}
```

## 5. View reports (html page)
```
url: /report/
```
