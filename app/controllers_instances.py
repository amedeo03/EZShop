from app.controllers.accounting_controller import AccountingController
from app.controllers.customer_controller import CustomerController
from app.controllers.orders_controller import OrdersController
from app.controllers.products_controller import ProductsController
from app.controllers.return_controller import ReturnController
from app.controllers.sales_controller import SalesController
from app.controllers.sold_products_controller import SoldProductsController

products_controller = ProductsController()
sales_controller = SalesController()
returns_controller = ReturnController()
customer_controller = CustomerController()
accounting_controller = AccountingController()
orders_controller = OrdersController()
sold_products_controller = SoldProductsController()
