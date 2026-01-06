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

    <Write here the integration sequence you adopted, in general terms (top down, bottom up, mixed) and as sequence

    (ex: step1: unit A, step 2: unit A+B, step 3: unit A+B+C, etc)>

    <Some steps may  correspond to unit testing (ex step1 in ex above)>

    <One step will  correspond to API testing >

# Tests

<in the table below list the test cases defined For each test report the object tested, the test level (API, integration, unit) and the technique used to define the test case (BB/ eq partitioning, BB/ boundary, WB/ statement coverage, etc)> <split the table if needed>

## Unit Testing
| Test case name               | Object(s) tested                       | Test level | Technique used                                           |
|:-----------------------------|:-------------------------------------- |:----------:|:---------------------------------------------------------|
| test_create_order            | OrdersRepository.create_order          |  Unit       | WB / Statement Coverage                                 |
| test_list_orders             | OrdersRepository.list_orders           |  Unit       | WB / Boundary                                           |
| test_get_order               | OrdersRepository.get_order             |  Unit       | WB / Boundary                                           |
| test_pay_order               | OrdersRepository.pay_order             |  Unit       | WB / Decision Coverage                                  |
| test_record_arrival          | OrdersRepository.record_arrival        |  Unit       | WB / Decision Coverage                                  |
| test_create_and_pay_order     | OrdersRepository.create_and_pay_order |  Unit       | WB / Statement Coverage                                 |
| test_get_orders_by_barcode    | OrdersRepository.get_orders_by_barcode|  Unit       | WB / Statement Coverage                                 |


## Integration Testing
|         Test case name            | Object(s) tested                                |   Test level   |         Technique used                                  |
|:--------------------------------: |:----------------------------------------------: |:--------------:|:--------------------------------------------------------|
| test_get_balance                  | AccountingController.get_balance                |   Integration  | BB / Equivalence Partitioning                           |
| test_set_balance                  | AccountingController.set_balance                |   Integration  | BB **TODO**                                  |
| test_reset_balance                | AccountingController.reset_balance              |   Integration  | BB / Equivalence Partitioning                           |
| test_create_order                 | OrdersController.create_order                   |   Integration  | BB / Equivalence Partitioning / Boundary                |
| test_list_orders                  | OrdersController.list_orders                    |   Integration  | BB **TODO**                                 |
| test_pay_order                    | OrdersController.pay_order                      |   Integration  | BB **TODO**                                  |
| test_record_arrial                | OrdersController.record_arrial                  |   Integration  | BB **TODO**                                  |
| test_get_order_by_product_barcode | OrdersController.get_order_by_product_barcode   |   Integration  | BB / Equivalence Partitioning                           |



## End to end Testing
| Test case name                     | Object(s) tested                       | Test level | Technique used                                          |
|:-----------------------------------|:---------------------------------------|:----------:|:--------------------------------------------------------|
| test_get_current_balance           | AccountingRouter.get_current_balance   | End to End | BB / Equivalence Partitioning                           |
| test_set_balance_authentication    | AccountingRouter.set_balance (auth)    | End to End | BB / Equivalence Partitioning                           |
| test_set_balance_authenticated     | AccountingRouter.set_balance           | End to End | BB / Boundary                                           |
| test_reset_balance_authentication  | AccountingRouter.reset_balance (auth)  | End to End | BB / Equivalence Partitioning                           |
| test_reset_balance_authenticated   | AccountingRouter.reset_balance         | End to End | BB / State-based                                        |
| test_issue_order_authentication    | OrdersRouter.issue_order (auth)        | End to End | BB / Equivalence Partitioning                           |
| test_issue_order                   | OrdersRouter.issue_order               | End to End | BB / Equivalence Partitioning                           |
| test_pay_order_for_authentication  | OrdersRouter.pay_order_for (auth)      | End to End | BB / Equivalence Partitioning                           |
| test_pay_order_for                 | OrdersRouter.pay_order_for             | End to End | BB / Equivalence Partitioning                           |
| test_list_orders                   | OrdersRouter.list_orders               | End to End | BB / Equivalence Partitioning                           |
| test_pay_order_authentication      | OrdersRouter.pay_order                 | End to End | BB / Equivalence Partitioning                           |
| test_pay_order                     | OrdersRouter.pay_order (auth)          | End to End | BB / Equivalence Partitioning                           |
| test_record_arrival_authentication | OrdersRouter.record_arrival (auth)     | End to End | BB / Equivalence Partitioning                           |
| test_record_arrival                | OrdersRouter.record_arrival            | End to End | BB / Equivalence Partitioning                           |


# Coverage

## Coverage of FR

<Report in the following table the coverage of functional requirements and scenarios(from official requirements) >

| Functional Requirement or scenario | Test(s) |
| :--------------------------------: | :-----: |
|                FRx                 |         |
|                FRy                 |         |
|                Scx                 |         |
|                Scy                 |         |
|                ...                 |         |

## Coverage white box

Report here the screenshot of coverage values obtained with PyTest
