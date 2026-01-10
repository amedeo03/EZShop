# Test Report

<The goal of this document is to explain how the application was tested, detailing how the test cases were defined and what they cover>

# Contents

- [Test Report](#test-report)
- [Contents](#contents)
- [Dependency graph](#dependency-graph)
- [Integration approach](#integration-approach)
- [Tests](#tests)
- [Coverage](#coverage)
  - [Coverage of FR](#coverage-of-fr)
  - [Coverage white box](#coverage-white-box)

# Dependency graph

     <report the here the dependency graph of EzShop>

# Integration approach

A bottom-up approach has been used, starting from running unit-tests for the various repositories. We then wrote integration tests for controller, using real repository objects. Finally, the last tests written were e2e tests on available routes to check the whole application flow. 

# Tests

<in the table below list the test cases defined For each test report the object tested, the test level (API, integration, unit) and the technique used to define the test case (BB/ eq partitioning, BB/ boundary, WB/ statement coverage, etc)> <split the table if needed>

## Unit Testing

### ProductRepository

| Test case name                 | Object(s) tested                             | Test level | Technique used                                           |
|:-------------------------------|:---------------------------------------------|:----------:|:---------------------------------------------------------|
| test_create_product            | ProductsRepository.create_product            |  Unit      | WB / Statement Coverage                                  |
| test_list_products             | ProductsRepository.list_products             |  Unit      | WB / Statement Coverage                                  |
| test_get_product               | ProductsRepository.get_product               |  Unit      | WB / Statement Coverage                                  |
| test_get_product_by_barcode    | ProductsRepository.get_product_by_barcode    |  Unit      | WB / Statement Coverage                                  |
| test_get_product_by_description| ProductsRepository.get_product_by_description|  Unit      | WB / Statement Coverage                                  |
| test_update_product_position   | ProductsRepository.update_product_position   |  Unit      | WB / Statement Coverage                                  |
| test_update_product_quantity   | ProductsRepository.update_product_quantity   |  Unit      | WB / Statement Coverage                                  |
| test_update_product            | ProductsRepository.update_product            |  Unit      | WB / Statement Coverage                                  |
| test_delete_product            | ProductsRepository.delete_product            |  Unit      | WB / Statement Coverage                                  |

### OrderRepository

| Test case name               | Object(s) tested                       | Test level | Technique used                                           |
|:-----------------------------|:-------------------------------------- |:----------:|:---------------------------------------------------------|
| test_create_order            | OrdersRepository.create_order          |  Unit      | WB / Statement Coverage                                 |
| test_list_orders             | OrdersRepository.list_orders           |  Unit      | WB / Boundary                                           |
| test_get_order               | OrdersRepository.get_order             |  Unit      | WB / Boundary                                           |
| test_pay_order               | OrdersRepository.pay_order             |  Unit      | WB / Decision Coverage                                  |
| test_record_arrival          | OrdersRepository.record_arrival        |  Unit      | WB / Decision Coverage                                  |
| test_create_and_pay_order    | OrdersRepository.create_and_pay_order  |  Unit      | WB / Statement Coverage                                 |
| test_get_orders_by_barcode   | OrdersRepository.get_orders_by_barcode |  Unit      | WB / Statement Coverage                                 |

### CustomerRepository

| Test case name               | Object(s) tested                       | Test level | Technique used                                           |
|:-----------------------------|:-------------------------------------- |:----------:|:---------------------------------------------------------|
| test_create_customer         | CustomerRepository.create_customer          |  Unit      | WB / Statement Coverage |        
| test_create_customer_with_card_already_attached         | CustomerRepository.create_customer          |  Unit      | WB / Decision Coverage                            |
| test_list_customer             | CustomerRepository.list_customer           |  Unit      | WB / Statement Coverage                                           |
| test_list_customer_empty             | CustomerRepository.list_customer           |  Unit      | WB / Decision Coverage |
| test_get_customer               | CustomerRepository.get_customer             |  Unit      | WB / Decision Coverage                                              |
| test_update_customer_with_card_success               | CustomerRepository.update_customer             |  Unit      | WB / Statement Coverage   |
| test_update_customer_card_not_found        | CustomerRepository.update_customer             |  Unit      | WB / Decision Coverage   |
| test_update_customer_card_already_attached               | CustomerRepository.update_customer             |  Unit      | WB / Decision Coverage   |
| test_update_customer_not_found               | CustomerRepository.update_customer             |  Unit      | WB / Decision Coverage   |
| test_update_customer_only_name             | CustomerRepository.update_customer_only_name             |  Unit      | WB / Decision Coverage                                |
| test_delete_customer_success          | CustomerRepository.delete_customer        |  Unit      | WB / Statement Coverage                                  |
|test_delete_customer_not_found          | CustomerRepository.delete_customer        |  Unit      | WB / Decision Coverage                                |  
| test_create_card     | CustomerRepository.create_card  |  Unit      | WB / Boundary Coverage |
| test_attach_card_success   | CustomerRepository.attach_card |  Unit      | WB / Statement Coverage |
| test_attach_card_card_not_found   | CustomerRepository.attach_card |  Unit      | WB / Decision Coverage |
| test_attach_card_customer_not_found   | CustomerRepository.attach_card |  Unit      | WB / Decision Coverage |
| test_attach_card_already_attached   | CustomerRepository.attach_card |  Unit      | WB / Decision Coverage |
| test_modify_point   | CustomerRepository.modify_point |  Unit      | WB / Statement Coverage                                 |
| test_modify_point_card_not_found   | CustomerRepository.modify_point |  Unit      | WB / Decision Coverage                                 |
| test_get_card_by_id_success   | CustomerRepository.get_card_by_id |  Unit      | WB / Statement Coverage                                 |
| test_get_card_by_id_not_found   | CustomerRepository.get_card_by_id |  Unit      | WB / Decision Coverage                                 |

### SaleRepository
| Test case name               | Object(s) tested                       | Test level | Technique used                                           |
|:-----------------------------|:-------------------------------------- |:----------:|:---------------------------------------------------------|
| test_create_sale_ok         | SaleRepository.create_sale          |  Unit      | WB / Statement Coverage | 
| test_list_sales_full         | SaleRepository.list_sales          |  Unit      | WB / Statement Coverage | 
| test_list_sales_empty         | SaleRepository.list_sales          |  Unit      | WB / Statement Coverage | 
| test_get_sale_by_id_ok  | SaleRepository.get_sale_by_id          |  Unit      | WB / Statement Coverage | 
| test_get_sale_by_id_not_found | SaleRepository.get_sale_by_id          |  Unit      | WB / Statement Coverage | 
| test_get_delete_sale_ok    | SaleRepository.delete_sale          |  Unit      | WB / Statement Coverage | 
| test_get_delete_sale_not_found   | SaleRepository.delete_sale          |  Unit      | WB / Statement Coverage | 
| test_edit_sale_discount_ok         | SaleRepository.edit_sale_discount          |  Unit      | WB / Statement Coverage | 
| test_edit_sale_discount_not_found         | SaleRepository.edit_sale_discount          |  Unit      | WB / Statement Coverage | 
| test_edit_sale_discount_invalid_status   | SaleRepository.edit_sale_discount          |  Unit      | WB / Statement Coverage | 
| test_edit_sale_status_pending         | SaleRepository.edit_sale_status          |  Unit      | WB / Statement Coverage | 
| test_edit_sale_status_pay     | SaleRepository.edit_sale_status       |  Unit      | WB / Statement Coverage |
| test_edit_sale_status_invalid_status    | SaleRepository.edit_sale_status  |  Unit      | WB / Statement Coverage | 


### SoldProductRepository
| Test case name               | Object(s) tested                       | Test level | Technique used                                           |
|:-----------------------------|:-------------------------------------- |:----------:|:---------------------------------------------------------|
| test_create_sold_product_ok         | SoldProductsRepository.create_sold_product          |  Unit      | WB / Statement Coverage | 
| test_create_sold_product_conflict         | SoldProductsRepository.create_sold_product |  Unit      | WB / Statement Coverage | 
| test_get_sale_by_id_ok         | SoldProductsRepository.get_sold_product_by_id          |  Unit      | WB / Statement Coverage | 
| test_get_sale_by_id_not_found  | SoldProductsRepository.get_sold_product_by_id          |  Unit      | WB / Statement Coverage | 
| test_edit_quantity_ok | SoldProductsRepository.edit_sold_product_quantity          |  Unit      | WB / Statement Coverage | 
| test_edit_quantity_not_found    | SoldProductsRepository.edit_sold_product_quantity         |  Unit      | WB / Statement Coverage | 
| test_edit_quantity_big_quantity   | SoldProductsRepository.edit_sold_product_quantity          |  Unit      | WB / Statement Coverage | 
| test_edit_discount_ok         | SoldProductsRepository.edit_sold_product_discount         |  Unit      | WB / Statement Coverage | 
| test_edit_discount_not_found         | SoldProductsRepository.edit_sold_product_discount          |  Unit      | WB / Statement Coverage | 
| test_remove_ok   | SoldProductsRepository.remove_sold_product          |  Unit      | WB / Statement Coverage | 



## Integration Testing

### ProductsController

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_product               | ProductsController.create_product               |  Integration   | BB / Equivalence Partitioning                           |
| test_list_products                | ProductsController.list_products                |  Integration   | BB / Equivalence Partitioning                           |
| test_get_product                  | ProductsController.get_product                  |  Integration   | BB / Equivalence Partitioning                           |
| test_get_product_by_barcode       | ProductsController.get_product_by_barcode       |  Integration   | BB / Equivalence Partitioning                           |
| test_get_product_by_description   | ProductsController.get_product_by_description   |  Integration   | BB / Equivalence Partitioning                           |
| test_update_product_position      | ProductsController.update_product_position      |  Integration   | BB / Equivalence Partitioning                           |
| test_update_product_quantity      | ProductsController.update_product_quantity      |  Integration   | BB / Equivalence Partitioning                           |
| test_update_product               | ProductsController.update_product               |  Integration   | BB / Equivalence Partitioning                           |
| test_update_product_invalid_state | ProductsController.update_product               |  Integration   | BB / Equivalence Partitioning                           |
| test_delete_product               | ProductsController.delete_product               |  Integration   | BB / Equivalence Partitioning                           |
| test_delete_product_invalid_sttate| ProductsController.delete_product               |  Integration   | BB / Equivalence Partitioning                           |

### AccountingController

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_get_balance                  | AccountingController.get_balance                |   Integration  | BB / Equivalence Partitioning                           |
| test_set_balance                  | AccountingController.set_balance                |   Integration  | BB / Equivalence Partitioning                           |
| test_reset_balance                | AccountingController.reset_balance              |   Integration  | BB / Equivalence Partitioning                           |

### OrdersController

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_order                 | OrdersController.create_order                   |   Integration  | BB / Equivalence Partitioning / Boundary                |
| test_list_orders                  | OrdersController.list_orders                    |   Integration  | WB / Statement Coverage                                 |
| test_pay_order                    | OrdersController.pay_order                      |   Integration  | BB / Equivalence Partitioning                           |
| test_record_arrival               | OrdersController.record_arrival                 |   Integration  | BB / Equivalence Partitioning                           |
| test_get_order_by_product_barcode | OrdersController.get_order_by_product_barcode   |   Integration  | BB / Equivalence Partitioning                           |


### CustomerController

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_customer               | CustomerController.create_customer               |  Integration   | BB / Equivalence Partitioning                           |
| test_list_customers                | CustomerController.list_customer                |  Integration   | BB / Equivalence Partitioning                           |
| test_get_customer_by_id                  | CustomerController.get_customer                  |  Integration   | BB / Equivalence Partitioning / Boundary                           |
| test_update_customer       | CustomerController.update_customer       |  Integration   | BB / Equivalence Partitioning                           |
| test_update_customer_detach_card       | CustomerController.update_customer       |  Integration   | BB /   Boundary                           |
| test_update_customer_with_card_already_attached       | CustomerController.update_customer       |  Integration   | BB / Equivalence Partitioning                           |
| test_delete_customer   | CustomerController.delete_customer   |  Integration   | BB / Equivalence Partitioning                           |
| test_create_card      | CustomerController.create_card      |  Integration   | BB / Boundary                           |
| test_attach_card      | CustomerController.attach_card      |  Integration   | BB / Equivalence Partitioning / Boundary                            |
| test_modify_point               | CustomerController.modify_point               |  Integration   | BB / Equivalence Partitioning / Boundary                           |

### SaleController
|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_sale_controller_ok               | SaleController.create_sale               |  Integration   | BB / Equivalence Partitioning                           |
| test_get_all_sale_controller_ok               | SaleController.list_sales               |  Integration   | BB / Equivalence Partitioning
| test_get_sale_controller_ok               | SaleController.get_sale_by_id               |  Integration   | BB / Equivalence Partitioning
| test_get_sale_controller_invalid_input               | SaleController.get_sale_by_id               |  Integration   | BB / Equivalence Partitioning
| test_get_sale_controller_not_found               | SaleController.get_sale_by_id               |  Integration   | BB / Equivalence Partitioning
| test_delete_sale_controller_ok               | SaleController.delete_sale               |  Integration   | BB / Equivalence Partitioning
| test_delete_sale_controller_invalid_input               | SaleController.delete_sale               |  Integration   | BB / Equivalence Partitioning
| test_delete_sale_controller_not_found               | SaleController.delete_sale               |  Integration   | BB / Equivalence Partitioning
| test_delete_sale_controller_invalid_status               | SaleController.delete_sale               |  Integration   | BB / Equivalence Partitioning
| test_add_product_ok               | SaleController.attach_product               |  Integration   | BB / Equivalence Partitioning
| test_add_product_controller_invalid_input               | SaleController.attach_product               |  Integration   | BB / Equivalence Partitioning
| test_add_product_controller_not_found               | SaleController.attach_product               |  Integration   | BB / Equivalence Partitioning
| test_add_product_controller_invalid_status               | SaleController.attach_product               |  Integration   | BB / Equivalence Partitioning
| test_edit_product_controller_ok               | SaleController.edit_sold_product_quantity               |  Integration   | BB / Equivalence Partitioning
| test_edit_product_controller_invalid_input               | SaleController.edit_sold_product_quantity               |  Integration   | BB / Equivalence Partitioning
| test_edit_product_controller_not_found               | SaleController.edit_sold_product_quantity               |  Integration   | BB / Equivalence Partitioning
Partitioning
| test_edit_sale_discount_controller_ok               | SaleController.edit_sale_discount               |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_invalid_inputt              | SaleController.edit_sale_discount               |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_not_found             | SaleController.edit_sale_discount               |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_invalid_status              | SaleController.edit_sale_discount               |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_ok               | SaleController.edit_product_discount            |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_invalid_inputt              | SaleController.edit_product_discount            |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_not_found             | SaleController.edit_product_discount               |  Integration   | BB / Equivalence Partitioning
| test_edit_sale_discount_controller_invalid_status              | SaleController.edit_product_discount               |  Integration   | BB / Equivalence Partitioning
| test_close_sale_controller_ok               | SaleController.close_sale            |  Integration   | BB / Equivalence Partitioning
| test_close_sale_controller_invalid_inputt              | SaleController.close_sale            |  Integration   | BB / Equivalence Partitioning
| test_close_sale_controller_not_found             | SaleController.close_sale               |  Integration   | BB / Equivalence Partitioning
| test_close_sale_controller_invalid_status              | SaleController.close_sale               |  Integration   | BB / Equivalence Partitioning
| test_pay_sale_controller_ok               | SaleController.pay_sale            |  Integration   | BB / Equivalence Partitioning
| test_pay_sale_controller_invalid_inputt              | SaleController.pay_sale            |  Integration   | BB / Equivalence Partitioning
| test_pay_sale_controller_not_found             | SaleController.pay_sale               |  Integration   | BB / Equivalence Partitioning
| test_pay_sale_controller_invalid_status              | SaleController.pay_sale               |  Integration   | BB / Equivalence Partitioning
| test_get_point_controller_ok               | SaleController.get_points            |  Integration   | BB / Equivalence Partitioning
| test_get_point_controller_invalid_inputt              | SaleController.get_points            |  Integration   | BB / Equivalence Partitioning
| test_get_point_controller_not_found             | SaleController.get_points               |  Integration   | BB / Equivalence Partitioning
| test_get_point_controller_invalid_status              | SaleController.get_points               |  Integration   | BB / Equivalence Partitioning

### SoldProductsController
| test_create_sold_product_controller_ok           | SoldProductsController.create_sold_product               |  Integration   | BB / Equivalence Partitioning
| test_create_sold_product_controller_invalid_input           | SoldProductsController.create_sold_product               |  Integration   | BB / Equivalence Partitioning
| test_get_sold_product_by_id_controller_ok           | SoldProductsController.get_sold_product_by_id               |  Integration   | BB / Equivalence Partitioning
| test_get_sold_product_by_id_controller_invalid_input           | SoldProductsController.get_sold_product_by_id               |  Integration   | BB / Equivalence Partitioning
| test_get_sold_product_by_id_controller_not_found           | SoldProductsController.get_sold_product_by_id               |  Integration   | BB / Equivalence Partitioning
| test_edit_sold_product_quantity_controller_ok           | SoldProductsController.edit_sold_product_quantity               |  Integration   | BB / Equivalence Partitioning
| test_edit_sold_product_quantity_controller_invalid_input           | SoldProductsController.edit_sold_product_quantity               |  Integration   | BB / Equivalence Partitioning
| test_edit_sold_product_discount_controller_ok           | SoldProductsController.edit_sold_product_discount               |  Integration   | BB / Equivalence Partitioning
| test_edit_sold_product_discount_controller_invalid_input           | SoldProductsController.edit_sold_product_discount               |  Integration   | BB / Equivalence Partitioning
| test_remove_sold_product_ok           | SoldProductsController.remove_sold_product               |  Integration   | BB / Equivalence Partitioning
| test_remove_sold_product_invalid_input           | SoldProductsController.remove_sold_product               |  Integration   | BB / Equivalence Partitioning

## End to end Testing

### ProductsRouter

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_product               | ProductsRouter.create_product                   |  End to End    | BB / Equivalence Partitioning                           |
| test_list_products                | ProductsRouter.list_products                    |  End to End    | BB / Equivalence Partitioning                           |
| test_get_product                  | ProductsRouter.get_product                      |  End to End    | BB / Equivalence Partitioning                           |
| test_get_product_by_barcode       | ProductsRouter.get_product_by_barcode           |  End to End    | BB / Equivalence Partitioning                           |
| test_get_product_by_description   | ProductsRouter.get_product_by_description       |  End to End    | BB / Equivalence Partitioning                           |
| test_update_product_position      | ProductsRouter.update_product_position          |  End to End    | BB / Equivalence Partitioning                           |
| test_update_product_quantity      | ProductsRouter.update_product_quantity          |  End to End    | BB / Equivalence Partitioning                           |
| test_update_product               | ProductsRouter.update_product                   |  End to End    | BB / Equivalence Partitioning                           |
| test_update_product_invalid_state | ProductsRouter.update_product                   |  End to End    | BB / Equivalence Partitioning                           |
| test_update_product_duplicates    | ProductsRouter.update_product                   |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product               | ProductsRouter.delete_product                   |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_invalid_state | ProductsRouter.delete_product                   |  End to End    | BB / Equivalence Partitioning                           |

### AccountingRouter

| Test case name                     | Object(s) tested                       | Test level | Technique used                                          |
|:-----------------------------------|:---------------------------------------|:----------:|:--------------------------------------------------------|
| test_get_current_balance           | AccountingRouter.get_current_balance   | End to End | BB / Equivalence Partitioning                           |
| test_set_balance_authentication    | AccountingRouter.set_balance (auth)    | End to End | BB / Equivalence Partitioning                           |
| test_set_balance_authenticated     | AccountingRouter.set_balance           | End to End | BB / Boundary                                           |
| test_reset_balance_authentication  | AccountingRouter.reset_balance (auth)  | End to End | BB / Equivalence Partitioning                           |
| test_reset_balance_authenticated   | AccountingRouter.reset_balance         | End to End | BB / State-based                                        |

### OrdersRouter

| Test case name                     | Object(s) tested                       | Test level | Technique used                                          |
|:-----------------------------------|:---------------------------------------|:----------:|:--------------------------------------------------------|
| test_issue_order_authentication    | OrdersRouter.issue_order (auth)        | End to End | BB / Equivalence Partitioning                           |
| test_issue_order                   | OrdersRouter.issue_order               | End to End | BB / Equivalence Partitioning                           |
| test_pay_order_for_authentication  | OrdersRouter.pay_order_for (auth)      | End to End | BB / Equivalence Partitioning                           |
| test_pay_order_for                 | OrdersRouter.pay_order_for             | End to End | BB / Equivalence Partitioning                           |
| test_list_orders                   | OrdersRouter.list_orders               | End to End | BB / Equivalence Partitioning                           |
| test_pay_order_authentication      | OrdersRouter.pay_order                 | End to End | BB / Equivalence Partitioning                           |
| test_pay_order                     | OrdersRouter.pay_order (auth)          | End to End | BB / Equivalence Partitioning                           |
| test_record_arrival_authentication | OrdersRouter.record_arrival (auth)     | End to End | BB / Equivalence Partitioning                           |
| test_record_arrival                | OrdersRouter.record_arrival            | End to End | BB / Equivalence Partitioning                           |

### CustomerRouter

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_customer               | CustomerRouter.create_customer                   |  End to End    | BB / Equivalence Partitioning                           |
| test_list_customers                | CustomerRouter.list_customer                    |  End to End    | BB / Equivalence Partitioning                           |
| test_get_customer                  | CustomerRouter.get_customer                      |  End to End    | BB / Equivalence Partitioning                           |
| test_update_customer       | CustomerRouter.update_customer           |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_customer   | CustomerRouter.delete_customer       |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_customer_with_card      | CustomerRouter.delete_customer          |  End to End    | BB / Equivalence Partitioning                           |
| test_create_card      | CustomerRouter.create_card          |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_card               | CustomerRouter.attach_card                   |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_card_already_attached               | CustomerRouter.attach_card                   |  End to End    | BB / Equivalence Partitioning                           |
| test_modify_points               | CustomerRouter.modify_point                   |  End to End    | BB / Equivalence Partitioning                           |

### SalesRoute
| test_close_sale_route_ok               | SaleRoute.close_sale                   |  End to End    | BB / Equivalence Partitioning                           |
| test_create_sale_route               | SaleRoute.create_sale                   |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_sale_route               | SaleRoute.delete_sale                   |  End to End    | BB / Equivalence Partitioning                           |
| test_get_all_sale_route               | SaleRoute.list_sales                   |  End to End    | BB / Equivalence Partitioning                           |
| test_get_sale_id_route_ok               | SaleRoute.get_sale_by_id                   |  End to End    | BB / Equivalence Partitioning                           |
| test_paid_sale_route               | SaleRoute.pay_sale                   |  End to End    | BB / Equivalence Partitioning                           |
| test_points_sale_route_ok               | SaleRoute.get_sale_points                   |  End to End    | BB / Equivalence Partitioning                           |
| test_product_added_route               | SaleRoute.attach_product                   |  End to End    | BB / Equivalence Partitioning                           |
| test_remove_added_route_ok               | SaleRoute.edit_product_quantity                   |  End to End    | BB / Equivalence Partitioning                           |
| test_set_discount_product_route               | SaleRoute.edit_product_discount                  |  End to End    | BB / Equivalence Partitioning                           |
| test_set_discount_route               | SaleRoute.edit_sale_discount                  |  End to End    | BB / Equivalence Partitioning                           |

# Coverage

## Coverage of FR

<Report in the following table the coverage of functional requirements and scenarios(from official requirements) >

| Functional Requirement or scenario |           Test(s)                   |
| :--------------------------------: | :----------------------------------:|
|                FR1                 |                                     |
|                FR1.1               |                                     |
|                FR1.2               |                                     |
|                FR1.3               |                                     |
|                FR1.4               |                                     |
|                FR1.5               |                                     |
|                FR3                 |                                     |
|                FR3.1               |test_create_product,test_update_product_position,|
|                                    |test_update_product_quantity,test_update_product,|
|                                    |test_update_product_invalid_state, test_update_product_duplicates|                                 
|                FR3.2               |       test_delete_product           |
|                FR3.3               |        test_list_products           |
|                FR3.4               |test_get_product, test_get_product_by_barcode,|
|                                    |   test_get_product_by_description   |
|                FR4                 |                                     |
|                FR4.1               |                                     |
|                FR4.2               |                                     |
|                FR4.3               |                                     |
|                FR4.4               |      test_pay_order_for (e2e)       |
|                FR4.5               |                                     |
|                FR4.6               |      test_record_arrival (e2e)      |
|                FR4.7               |       test_list_orders (e2e)        |
|                FR 5                |                                     |
|                FR5.1               |                                     |
|                FR5.2               |                                     |
|                FR5.3               |                                     |
|                FR5.4               |                                     |
|                FR5.5               |                                     |
|                FR5.6               |                                     | 
|                FR5.7               |                                     |
|                FR6                 |                                     |
|                FR6.1               | test_create_sale_route, test_create_sale_controller_ok,   test_create_sale_ok                                   |
|                FR6.2               |      test_create_sold_product_ok, test_create_sold_product_conflict, test_add_product_ok,test_add_product_invalid_input,test_add_product_invalid_status, test_add_product_not_found, test_product_added_route                               |
|                FR6.3               |  test_remove_ok, test_remove_sold_product_ok, test_remove_sold_product_invalid_input, test_remove_product_route_ok                                    |
|                FR6.4               | test_set_discount,  test_edit_sale_discount_controller_ok,test_edit_sale_discount_controller_invalid_input, test_edit_sale_discount_controller_not_found, test_edit_sale_discount_controller_invalid_status,test_edit_sale_ok,test_edit_sale_discount_invalid_status, test_edit_sale_discount_not_found                                    |
|                FR6.5               | test_set_discount_product_route, test_edit_product_discount_controllore_ok,test_edit_product_discount_controllore_invalid_input,
test_edit_product_discount_controllore_invalid_status,
test_edit_product_discount_controllore_not_found, test_edit_discount_ok,test_edit_discount_not_found                                   |
|                FR6.6               | test_get_point_controller_ok, test_get_point_controller_invalid_input, test_get_point_controller_invalid_status, test_get_point_controller_not_found, test_point_route_ok                                   |
|                FR6.7               |                                     |
|                FR6.8               | test_get_sale_id_route_ok, test_get_sale_controller_ok,test_get_sale_controller_invalid_input,test_get_sale_controller_not_found, test_get_sale_by_id_ok, test_get_sale_by_id_not_found                                    |
|                FR6.10              | test_edit_sale_status_pending, test_close_sale_controlle_ok,test_close_sale_controlle_not_found,test_close_sale_controlle_invalid_input,test_close_sale_controlle_invalid_status,test_close_sale_sale_route_ok,test_edit_sale_status_invalid_status                                     |
|                FR6.11              | test_delete_sale_route, test_paid_sale_route, test_delete_sale_controller_ok,test_delete_sale_controller_invalid_input,test_delete_sale_controller_not_found, test_delete_sale_controller_invalid_status,test_delete_paid_controller_invalid_input,test_paid_sale_controller_not_found, test_paid_sale_controller_invalid_status, test_paid_sale_controller_ok, test_delete_sale_ok, test_delete_sale_not_found, test_edit_sale_status_paid, test_edit_sale_status_invalid_status                                  |
|                FR6.12              |                                     |
|                FR6.13              |                                     |
|                FR6.14              |                                     |
|                FR6.15              |                                     |
|                FR7                 |                                     |
|                FR7.1               |                                     |
|                FR7.2               |                                     |
|                FR7.3               |                                     |
|                FR7.4               |                                     |
|                FR8                 |                                     |
|                FR8.1               |test_set_balance_authenticated (e2e) |
|                FR8.2               |test_set_balance_authenticated (e2e) |
|                FR8.3               |   test_get_current_balance (e2e)    |
|                FR8.4               |test_set_balance_authenticated (e2e) |
|             Scenario 1-1           |                                     |
|             Scenario 1-2           |                                     |
|             Scenario 1-3           |                                     |
|             Scenario 2-1           |                                     |
|             Scenario 2-2           |                                     |
|             Scenario 2-3           |                                     |
|             Scenario 3-1           |       test_issue_order (e2e)        |
|             Scenario 3-2           |       test_pay_order (e2e)          |
|             Scenario 3-3           |      test_record_arrival (e2e)      |
|             Scenario 4-1           |                                     |
|             Scenario 4-2           |                                     |
|             Scenario 4-3           |                                     |
|             Scenario 4-4           |                                     |
|             Scenario 4-1           |                                     |
|             Scenario 5-1           |                                     |
|             Scenario 5-2           |                                     |
|             Scenario 6-1           |                                     |
|             Scenario 6-2           |                                     |
|             Scenario 6-3           |                                     |
|             Scenario 6-4           |                                     |
|             Scenario 6-5           |                                     |
|             Scenario 6-6           |                                     |
|             Scenario 7-1           |                                     |
|             Scenario 7-2           |                                     |
|             Scenario 7-3           |                                     |
|             Scenario 7-4           |                                     |
|             Scenario 8-1           |                                     |
|             Scenario 8-2           |                                     |
|             Scenario 9-1           |                                     |
|             Scenario 10-1          |                                     |
|             Scenario 10-2          |                                     |


## Coverage white box

Report here the screenshot of coverage values obtained with PyTest
