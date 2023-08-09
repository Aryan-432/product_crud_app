#Make a CRUD on Product model by using MySQL with SQLAlchemy.
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sanic import Sanic, HTTPResponse
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic.response import text, json


"""
1. Create DB user
2. Create DB
3. Assign permissons to DB user for DB usage
"""

"""
Add serializer by using python marshmallow 
"""

Sanic.start_method = "fork"
from sanic.worker.manager import WorkerManager
WorkerManager.THRESHOLD = 100

DB_STRING = "mysql://aryan:qwerty@127.0.0.1:3306/testdb"

engine = create_engine(DB_STRING)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(1000))




class ProductView(HTTPMethodView):

    def get(self, request):
        try:
            products = session.query(Product).all()
            data = []
            for product in products:
                data.append({
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "description": product.description,
                })
            
            return json(data, status=200)
    
        except SQLAlchemyError as e:
            session.rollback()
            return HTTPResponse("Error occurred while fetching data.", status=500)


    def post(self, request):
        try:
            data = request.json
            new_product = Product(
                name=data.get('name'),
                price=data.get('price'), 
                description=data.get('description')
            )
            session.add(new_product)
            session.commit()
            return text('Product created successfully')
    
        except SQLAlchemyError as e:
            session.rollback()
            return HTTPResponse("Error occurred while creating the product!", status=500)


    def patch(self, request):
        try:
            data = request.json
            product_id = data.get('id')
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                product.name = data.get('name', product.name)
                product.price = data.get('price', product.price)
                product.description = data.get('description', product.description)
                session.commit()
                return text('Product updated successfully!')
            else:
                return text('Product not found!', status=404)
        except SQLAlchemyError as e:
            session.rollback()
            return HTTPResponse("Error occurred while updating the product.", status=500)


    def delete(self, request):
        try:
            data = request.json
            product_id = data.get('id')
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                session.delete(product)
                session.commit()
                return text('Product deleted successfully!')
            else:
                return text('Product not found!', status=404)
        except SQLAlchemyError as e:
            session.rollback()
            return HTTPResponse("Error occurred while deleting the product.", status=500)

if __name__ == '__main__':
    
    app = Sanic(__name__)
    app.add_route(ProductView.as_view(), '/products')

    Base.metadata.create_all(engine)
    app.run(host="0.0.0.0", port=8080, debug=True, auto_reload=True)
