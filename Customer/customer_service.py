# customer_service.py
from models import db, Customer

def find_by_email(email):
    return Customer.query.filter_by(Email=email).first()

def find_by_id(customer_id):
    return Customer.query.get(customer_id)

def create_customer(first_name, last_name, email, password_hash):
    new_customer = Customer(
        FirstName=first_name,
        LastName=last_name,
        Email=email,
        PasswordHash=password_hash,
        TotalPizzasOrdered=0
    )
    db.session.add(new_customer)
    db.session.commit()
    return new_customer

def update_customer(customer, data):
    customer.BirthDate = data.get("birthdate") or customer.BirthDate
    customer.PhoneNumber = data.get("phone") or customer.PhoneNumber
    customer.Street = data.get("street") or customer.Street
    customer.HouseNumber = data.get("house_number") or customer.HouseNumber
    customer.City = data.get("city") or customer.City
    customer.PostalCode = data.get("postal_code") or customer.PostalCode
    db.session.commit()
    return customer
