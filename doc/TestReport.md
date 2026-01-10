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

### ReturnRepository

| Test case name                                        | Object(s) tested                              | Test level | Technique used                    |
|:------------------------------------------------------|:----------------------------------------------|:----------:|:----------------------------------|
| test_create_return_transaction                        | ReturnRepository.create_return_transaction    |  Unit      | WB / Statement Coverage           |
| test_list_returns_with_results                        | ReturnRepository.list_returns                 |  Unit      | WB / Statement Coverage           |
| test_list_returns_empty_raises_not_found              | ReturnRepository.list_returns                 |  Unit      | WB / Decision Coverage            |
| test_get_return_by_id_success                         | ReturnRepository.get_return_by_id             |  Unit      | WB / Statement Coverage           |
| test_get_return_by_id_not_found                       | ReturnRepository.get_return_by_id             |  Unit      | WB / Decision Coverage            |
| test_delete_return_success                            | ReturnRepository.delete_return                |  Unit      | WB / Statement Coverage           |
| test_delete_return_not_found                          | ReturnRepository.delete_return                |  Unit      | WB / Decision Coverage            |
| test_list_returns_for_sale_id_success                 | ReturnRepository.list_returns_for_sale_id     |  Unit      | WB / Statement Coverage           |
| test_close_return_transaction_not_found               | ReturnRepository.close_return_transaction     |  Unit      | WB / Decision Coverage            |
| test_reimburse_return_not_closed_raises_invalid_state | ReturnRepository.reimburse_return_transaction |  Unit      | WB / Decision Coverage            |
| test_reimburse_return_not_found                       | ReturnRepository.reimburse_return_transaction |  Unit      | WB / Decision Coverage            |

### ReturnedProductsRepository

| Test case name                             | Object(s) tested                                                 | Test level | Technique used          |
|:-------------------------------------------|:-----------------------------------------------------------------|:----------:|:------------------------|
| test_create_returned_product               | ReturnedProductsRepository.create_returned_product               |  Unit      | WB / Statement Coverage |
| test_create_returned_product_duplicate     | ReturnedProductsRepository.create_returned_product               |  Unit      | WB / Decision Coverage  |
| test_edit_quantity_decrease                | ReturnedProductsRepository.edit_quantity_of_returned_product     |  Unit      | WB / Statement Coverage |
| test_edit_quantity_to_zero                 | ReturnedProductsRepository.edit_quantity_of_returned_product     |  Unit      | WB / Decision Coverage  |
| test_edit_quantity_not_found               | ReturnedProductsRepository.edit_quantity_of_returned_product     |  Unit      | WB / Decision Coverage  |
| test_edit_quantity_insufficient            | ReturnedProductsRepository.edit_quantity_of_returned_product     |  Unit      | WB / Decision Coverage  |
| test_get_by_id                             | ReturnedProductsRepository.get_returned_products_by_id           |  Unit      | WB / Statement Coverage |
| test_get_by_id_not_found                   | ReturnedProductsRepository.get_returned_products_by_id           |  Unit      | WB / Decision Coverage  |
| test_get_returned_products_by_barcode      | ReturnedProductsRepository.get_returned_product_by_barcode       |  Unit      | WB / Decision Coverage  |

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

### ReturnController

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_return_transaction                 | ReturnController.create_return_transaction      |   Integration  | BB / Equivalence Partitioning                           |
| test_create_return_invalid_sale_id             | ReturnController.create_return_transaction      |   Integration  | BB / Equivalence Partitioning                           |
| test_create_return_negative_sale_id            | ReturnController.create_return_transaction      |   Integration  | BB / Boundary                                           |
| test_get_return_by_id_success                  | ReturnController.get_return_by_id               |   Integration  | BB / Equivalence Partitioning                           |
| test_get_return_by_id_not_found                | ReturnController.get_return_by_id               |   Integration  | BB / Equivalence Partitioning                           |
| test_get_return_by_id_invalid_id               | ReturnController.get_return_by_id               |   Integration  | BB / Boundary                                           |
| test_delete_return_success                     | ReturnController.delete_return                  |   Integration  | BB / Equivalence Partitioning                           |
| test_delete_return_not_found                   | ReturnController.delete_return                  |   Integration  | BB / Equivalence Partitioning                           |
| test_close_return_transaction_success          | ReturnController.close_return_transaction       |   Integration  | BB / Equivalence Partitioning                           |
| test_close_return_already_closed               | ReturnController.close_return_transaction       |   Integration  | BB / Equivalence Partitioning                           |
| test_close_return_not_found                    | ReturnController.close_return_transaction       |   Integration  | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_success          | ReturnController.attach_product_to_return_transaction |   Integration  | BB / Equivalence Partitioning                     |
| test_attach_product_invalid_barcode            | ReturnController.attach_product_to_return_transaction |   Integration  | BB / Equivalence Partitioning                     |
| test_attach_product_negative_amount            | ReturnController.attach_product_to_return_transaction |   Integration  | BB / Boundary                                     |
| test_attach_product_to_closed_return           | ReturnController.attach_product_to_return_transaction |   Integration  | BB / Equivalence Partitioning                     |
| test_reimburse_return_not_closed               | ReturnController.reimburse_return_transaction   |   Integration  | BB / Equivalence Partitioning                           |
| test_reimburse_return_not_found                | ReturnController.reimburse_return_transaction   |   Integration  | BB / Equivalence Partitioning                           |
| test_list_returns_for_sale_id                  | ReturnController.list_returns_for_sale_id       |   Integration  | BB / Equivalence Partitioning                           |

### ReturnedProductController

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_returned_product                   | ReturnedProductController.create_returned_product             |   Integration  | BB / Equivalence Partitioning         |
| test_create_returned_product_validation        | ReturnedProductController.create_returned_product             |   Integration  | BB / Boundary                         |
| test_create_returned_product_duplicate         | ReturnedProductController.create_returned_product             |   Integration  | BB / Equivalence Partitioning         |
| test_edit_quantity_decrease                    | ReturnedProductController.edit_quantity_of_returned_product   |   Integration  | BB / Equivalence Partitioning         |
| test_edit_quantity_to_zero_deletes             | ReturnedProductController.edit_quantity_of_returned_product   |   Integration  | BB / Boundary                         |
| test_edit_quantity_validation                  | ReturnedProductController.edit_quantity_of_returned_product   |   Integration  | BB / Boundary                         |
| test_edit_quantity_not_found                   | ReturnedProductController.edit_quantity_of_returned_product   |   Integration  | BB / Equivalence Partitioning         |
| test_edit_quantity_insufficient                | ReturnedProductController.edit_quantity_of_returned_product   |   Integration  | BB / Equivalence Partitioning         |
| test_get_by_id                                 | ReturnedProductController.get_returned_products_by_id         |   Integration  | BB / Equivalence Partitioning         |
| test_get_by_id_not_found                       | ReturnedProductController.get_returned_products_by_id         |   Integration  | BB / Equivalence Partitioning         |
| test_get_by_id_validation                      | ReturnedProductController.get_returned_products_by_id         |   Integration  | BB / Boundary                         |
| test_get_by_barcode                            | ReturnedProductController.get_returned_product_by_barcode     |   Integration  | BB / Equivalence Partitioning         |
| test_get_by_barcode_not_found                  | ReturnedProductController.get_returned_product_by_barcode     |   Integration  | BB / Equivalence Partitioning         |
| test_get_by_barcode_validation                 | ReturnedProductController.get_returned_product_by_barcode     |   Integration  | BB / Boundary                         |


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

### ReturnsRouter

|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_create_return_transaction_authentication      | ReturnsRouter.create_return_transaction (auth)   |  End to End    | BB / Equivalence Partitioning                           |
| test_create_return_transaction_success             | ReturnsRouter.create_return_transaction          |  End to End    | BB / Equivalence Partitioning                           |
| test_create_return_transaction_invalid_sale        | ReturnsRouter.create_return_transaction          |  End to End    | BB / Equivalence Partitioning                           |
| test_create_return_transaction_unpaid_sale         | ReturnsRouter.create_return_transaction          |  End to End    | BB / Equivalence Partitioning                           |
| test_create_return_transaction_negative_sale_id    | ReturnsRouter.create_return_transaction          |  End to End    | BB / Boundary                                           |
| test_create_return_transaction_zero_sale_id        | ReturnsRouter.create_return_transaction          |  End to End    | BB / Boundary                                           |
| test_list_all_returns                              | ReturnsRouter.list_all_returns                   |  End to End    | BB / Equivalence Partitioning                           |
| test_get_return_by_id                              | ReturnsRouter.get_return_by_id                   |  End to End    | BB / Equivalence Partitioning / Boundary                |
| test_get_return_by_id_authentication               | ReturnsRouter.get_return_by_id (auth)            |  End to End    | BB / Equivalence Partitioning                           |
| test_list_returns_for_sale_id_success              | ReturnsRouter.list_returns_for_sale_id           |  End to End    | BB / Equivalence Partitioning                           |
| test_list_returns_for_sale_id_negative_id          | ReturnsRouter.list_returns_for_sale_id           |  End to End    | BB / Boundary                                           |
| test_list_returns_for_sale_id_zero_id              | ReturnsRouter.list_returns_for_sale_id           |  End to End    | BB / Boundary                                           |
| test_list_returns_for_sale_id_string_id            | ReturnsRouter.list_returns_for_sale_id           |  End to End    | BB / Equivalence Partitioning                           |
| test_list_returns_for_sale_id_authentication       | ReturnsRouter.list_returns_for_sale_id (auth)    |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_success              | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_authentication       | ReturnsRouter.attach_product_to_return (auth)    |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_product_not_found    | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_negative_return_id   | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Boundary                                           |
| test_attach_product_to_return_string_return_id     | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_invalid_barcode_too_short | ReturnsRouter.attach_product_to_return      |  End to End    | BB / Boundary                                           |
| test_attach_product_to_return_invalid_barcode_with_letters | ReturnsRouter.attach_product_to_return  |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_negative_amount      | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Boundary                                           |
| test_attach_product_to_return_string_amount        | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_return_invalid_return_id    | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Equivalence Partitioning                           |
| test_attach_product_to_closed_return               | ReturnsRouter.attach_product_to_return           |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_return_success            | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_return_authentication     | ReturnsRouter.delete_product_from_return (auth)  |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_return_negative_return_id | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Boundary                                           |
| test_delete_product_from_return_string_return_id   | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_return_negative_amount    | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Boundary                                           |
| test_delete_product_from_return_string_amount      | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_return_not_found          | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_return_product_not_found  | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_closed_return             | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_product_from_reimbursed_return         | ReturnsRouter.delete_product_from_return         |  End to End    | BB / Equivalence Partitioning                           |
| test_close_return_transaction_success              | ReturnsRouter.close_return_transaction           |  End to End    | BB / Equivalence Partitioning                           |
| test_close_return_transaction_authentication       | ReturnsRouter.close_return_transaction (auth)    |  End to End    | BB / Equivalence Partitioning                           |
| test_close_return_transaction_not_found            | ReturnsRouter.close_return_transaction           |  End to End    | BB / Equivalence Partitioning                           |
| test_close_return_transaction_negative_id          | ReturnsRouter.close_return_transaction           |  End to End    | BB / Boundary                                           |
| test_close_return_transaction_zero_id              | ReturnsRouter.close_return_transaction           |  End to End    | BB / Boundary                                           |
| test_close_return_transaction_string_id            | ReturnsRouter.close_return_transaction           |  End to End    | BB / Equivalence Partitioning                           |
| test_close_return_transaction_already_closed       | ReturnsRouter.close_return_transaction           |  End to End    | BB / Equivalence Partitioning                           |
| test_reimburse_return_transaction_success          | ReturnsRouter.reimburse_return_transaction       |  End to End    | BB / Equivalence Partitioning                           |
| test_reimburse_return_transaction_authentication   | ReturnsRouter.reimburse_return_transaction (auth)|  End to End    | BB / Equivalence Partitioning                           |
| test_reimburse_return_transaction_not_found        | ReturnsRouter.reimburse_return_transaction       |  End to End    | BB / Equivalence Partitioning                           |
| test_reimburse_return_transaction_negative_id      | ReturnsRouter.reimburse_return_transaction       |  End to End    | BB / Boundary                                           |
| test_reimburse_return_transaction_zero_id          | ReturnsRouter.reimburse_return_transaction       |  End to End    | BB / Boundary                                           |
| test_reimburse_return_transaction_string_id        | ReturnsRouter.reimburse_return_transaction       |  End to End    | BB / Equivalence Partitioning                           |
| test_reimburse_return_transaction_not_closed       | ReturnsRouter.reimburse_return_transaction       |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_return_success                         | ReturnsRouter.delete_return                      |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_return_authentication                  | ReturnsRouter.delete_return (auth)               |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_return_not_found                       | ReturnsRouter.delete_return                      |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_return_negative_id                     | ReturnsRouter.delete_return                      |  End to End    | BB / Boundary                                           |
| test_delete_return_zero_id                         | ReturnsRouter.delete_return                      |  End to End    | BB / Boundary                                           |
| test_delete_return_string_id                       | ReturnsRouter.delete_return                      |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_closed_return                          | ReturnsRouter.delete_return                      |  End to End    | BB / Equivalence Partitioning                           |
| test_delete_reimbursed_return                      | ReturnsRouter.delete_return                      |  End to End    | BB / Equivalence Partitioning                           |


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
|                FR6.1               |  test_create_return_transaction_success (e2e)  |
|                FR6.2               |  test_attach_product_to_return_success (e2e)   |
|                FR6.3               |  test_delete_product_from_return_success (e2e) |
|                FR6.4               |  test_close_return_transaction_success (e2e)   |
|                FR6.5               |  test_list_all_returns (e2e)                   |
|                FR6.6               |  test_get_return_by_id (e2e)                   |
|                FR6.7               |  test_list_returns_for_sale_id_success (e2e)   |
|                FR6.8               |  test_delete_return_success (e2e)              |
|                FR6.10              |  test_attach_product_to_return_success (e2e)   |
|                FR6.11              |  test_delete_product_from_return_success (e2e) |
|                FR6.12              |  test_list_all_returns (e2e)                   |
|                FR6.13              |  test_close_return_transaction_success (e2e)   |
|                FR6.14              |  test_delete_return_success (e2e)              |
|                FR6.15              |  test_reimburse_return_transaction_success (e2e) |
|                FR7                 |                                     |
|                FR7.1               |  test_reimburse_return_transaction_success (e2e) |
|                FR7.2               |  test_reimburse_return_transaction_success (e2e) |
|                FR7.3               |  test_reimburse_return_transaction_success (e2e) |
|                FR7.4               |  test_get_current_balance (e2e)                  |
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
|             Scenario 7-1           | test_create_return_transaction_success, test_attach_product_to_return_success, test_close_return_transaction_success, test_reimburse_return_transaction_success (e2e) |
|             Scenario 7-2           | test_create_return_transaction_success, test_attach_product_to_return_success, test_delete_product_from_return_success, test_close_return_transaction_success, test_reimburse_return_transaction_success (e2e) |
|             Scenario 7-3           | test_list_returns_for_sale_id_success (e2e) |
|             Scenario 7-4           | test_create_return_transaction_success, test_delete_return_success (e2e) |
|             Scenario 8-1           |                                     |
|             Scenario 8-2           |                                     |
|             Scenario 9-1           |                                     |
|             Scenario 10-1          |                                     |
|             Scenario 10-2          |                                     |


## Coverage white box

Report here the screenshot of coverage values obtained with PyTest
