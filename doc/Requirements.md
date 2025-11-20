

# Requirements Document - EZShop

Date: 24/10/2025

Version: 1.0.0

| Version number | Change |
| :------------: | :----: |
| 1.0.0 | Initial release |
| 2.0.0 | Added first drafts for business model, stakeholders, interfaces and FR| 

# Contents

- [Requirements Document - EzShop](#requirements-document)
- [Contents](#contents)
- [Informal description](#informal-description)
- [Business model](#business-model)
- [Stakeholders](#stakeholders)
- [Context Diagram and interfaces](#context-diagram-and-interfaces)
  - [Context Diagram](#context-diagram)
  - [Interfaces](#interfaces)
- [Functional and non functional requirements](#functional-and-non-functional-requirements)
  - [Functional Requirements](#functional-requirements)
  - [Non Functional Requirements](#non-functional-requirements)
- [Table of Rights](#table-of-rights)
- [Use case diagram and use cases](#use-case-diagram-and-use-cases)
  - [Use case diagram](#use-case-diagram)
    - [Use case 1, UC1](#use-case-1-uc1)
      - [Scenario 1.1](#scenario-11)
      - [Scenario 1.2](#scenario-12)
      - [Scenario 1.x](#scenario-1x)
    - [Use case 2, UC2](#use-case-2-uc2)
    - [Use case x, UCx](#use-case-x-ucx)
- [Glossary](#glossary)
- [System Design](#system-design)
- [Hardware Software architecture](#Hardware-software-architecture)

# Informal description

Small shops require a simple application to support the owner or manager. A small shop (ex a food shop) occupies 50-200 square meters, sells 500-2000 different item types, has two or a few more cash registers. 
EZShop is a software application to:
* manage sales
* manage inventory
* manage orders to suppliers
* support accounting

In the following describe the requirements of the EZShop application. 
You are free to define the application as you deem more useful and effective for the stakeholders. 
You are also free to modify the structure of the document when needed.
The document will be evaluated considering the typical defects in requirements (omissions, ambiguities, contradictions, etc), and syntactic errors in the formalism used (UML diagrams). 
Consider that the document should be delivered to another team (unknown to you)
 which will be in charge of designing and implementing the system. The design team should be able to proceed only with the information in the document.

# Business Model
EZShop will cost a monthly fee of x euros/month. The product won't contain advertising and will be inaccessible if the monthly fee is not paid for the current month

# Stakeholders

| Stakeholder name       | Description                                                                                      |
| :--------------------: | :----------------------------------------------------------------------------------------------: |
| Developers             | EZShop developers, in charge of developing and maintaining the product                           |
| End User             | owner of the shop, who is the one choosing to adopt EZShop for his business                      |
| End user               | individual who directly interacts with the software, often a sale manager of some kind           |
| Supplier               | company who supplies the shop with products of various nature                                    |
| Cashier                | Employee of the shop who operates the Point of Sale (POS)                                        |
| Cash register software | responsible for exchanging data with EzShop to record product sales                              |
| Payment service        | used **only**  to pay the monthly fee                                                            |
| Accounting software    | possible other software present in the business with whom EZShop will need to interact           |

#TODO is differentiating End User and end user actually useful in the case od a small shop?


# Context Diagram and interfaces

## Context Diagram
![Context Diagram](media/context-diagram-ezshop.png)


## Interfaces

\<describe here each interface in the context diagram>
|   Actor   | Logical Interface | Physical Interface |
| :-------: | :---------------: | :----------------: |
| End user               |        EZShop GUI      | laptop or desktop computer (display, keyboard, mouse)   |
| Cash register software (Sqaure POS) | RESTful API (or similar, e.g., GraphQL) exchanging JSON | internet connection (WAN) |
| Payment service        | Payment gateway's API or a secure, hosted payment webpage | internet connection (HTTPS) |
| Accounting software    | file-based export/import (e.g., CSV or XML format). | internet connection |
# Functional and non functional requirements

## Functional Requirements

\<In the form DO SOMETHING, or VERB NOUN, describe high level capabilities of the system>

\<they match to high level use cases>

|  ID   | Description |
| :---: | :---------: |
|FR1: Manage sales               | 1.1 Insert, read, update, delete sales records |
|                                | 1.2 Refund a product |
|FR2: Manage inventory           | 2.1 Insert, read, update, delete inventory records |
|                                | 2.2 Notification when stock is low |
|FR3: Manage orders to suppliers | 3.1 Insert, read, update, delete suppliers contacts |
|                                | 3.2 Create a new purchase order from a given supplier, specifying products and amounts |
|                                | 3.3 EZShop is able to send email to a supplier after the creation of a new order |
|                                | 3.4 Automatically insert a record for an order when email is sent |
|                                | 3.5 Function to mark an order as completed and adding received products to inventory table |
|FR4: Data visualization         | 4.1 Display charts overview about stored data |
|                                | 4.2 Filtering by category, time range, etc |
|                                | 4.3 Computes profits, expenses, taxes |
|                                | 4.4 Real time sync with database tables |
|FR5: Authentication and autorization process| 5.1 Login with email and password |
|                                            | 5.2 Logout |
|                                            | 5.2 Check if a subscription is active |
|                                            | 5.3 Prompt to pay the subscription if it is not active |
|                                            | 5.4 Create a new account for a shop |
|FR6: Exchange data with other software products| 6.1 Connect to the internet (via HTTPS) to exchange data with external cloud-based services (e.g., POS system, payment services) |
|                                | 6.2 Usage of an already established format to exchange standardized product data between software components |

## Non Functional Requirements

\<Describe constraints on functional requirements>

|   ID    | Type (efficiency, reliability, ..) | Description | Refers to |
| :-----: | :--------------------------------: | :---------: | :-------: |
|  NFR1   | Portability                        | The application is targeting desktop platforms and to reduce porting work, a cross platform framework will be used to support Windows, Mac Os and Linux environments |        |
|  NFR2   | Performance                        | Query return time should be less than 3 seconds |           |
|  NFR3   | Performance                        | Synchronization with local tables should happen every minute and should take less than 5 seconds |           |
|  NFR4   | Maintainability                    | Codebase should be structured in distinct modules that can be easily maintained and updated |           |
|  NFR5   | Security                           | Each account needs to have 2FA enabled | FR5 |
|  NFR6   | Usability                          | Adult between 18 and 70 years old accustomed to using desktop softwares, average education level (ex total 13 years in school). Users should be able to use application without training in less than 5 minutes|  |

# Table of rights

|  Actor   | FR1         | FR2 | FR3 | FR4 | FR5 | FR6 |
| :---:    | :---------: | :---: | :---: | :---: | :---: | :---: |
| end user | y | y | y | y | n | n |
#TODO ask if we have to add each FR

# Use case diagram and use cases

## Use case brief
|  UC name   | Goal         | Description |
| :---:    | :---------: | :---: |
| UC1 Account creation | Activate a new account for a shop | main actor: end user - The end user inserts the requested credentials in the EZShop account database |
| UC2 Payment of the subscription | Activate the subscription for the selected account | main actor: End User, payment service - Thanks to a credit card circuit, the End User is able to (automatically) pay the monthly fee |
| UC3 Login process | Access to main functions | main actor: end user - With a given pair of credentials the end user can login to EZShop and start using it |
| UC4 Logout process | Sign out from the currently signed in account | main actor: end user - the user is able to log out and lose access to EZShop features |
| UC5 Register a new product | Registration of a new product in stock | main actor: end user - A new product can be inserted in the inventory manually |
| UC6 Record a new sale | Record a sale | main actor: end user - A new sale can be inserted in the sale database by the end user |
| UC7 Record a refund | Record a refund | main actor: end user, cash register software - A customer can decide to ask for a refund of a previously sold product. This operation can be both managed by the cash register software as well as the end user |
| UC8 Manage supplier contacts | Create and keep supplier information up to date | main actor: end user - The end user can add, edit, or delete supplier contact details. Supplier data is stored in a dedicated database table for use when creating purchase orders |
| UC9 Submit a new purchase order | Generate a new purchase order to restock items | main actor: end user, supplier - The end user selects a supplier and specifies the products and quantities needed. The system generates a purchase order document and stores it in the database. The system automatically sends an email to the supplier |
| UC10 Mark an order as completed | End the order procedure | main actor: end user - when one order is delivered, the end user marks it as completed |
| UC11 Update inventory | Update inventory | main actor: end user - end user can change manually the amounts of products in stock |
| UC12 Visualization of data | Show charts, aggregating data | main actor: end user - end user can filter the data as desired |


## Use case diagram

![Use Case Diagram](media/uc_diagram_ezshop.png)

### Use case 1, UC1: Account Creation

| Actors Involved | End User |
| :---: | :--- |
| Precondition | End User has access to the EZShop application. |
| Post condition | A new Account record exists in the database. The account's Subscription status is 'inactive'. |
| Nominal Scenario | The End User successfully fills the registration form, and the system creates a new account. |
| Variants | N/A |
| Exceptions | 1a. Email already in use. |

##### Scenario 1.1: Successful New Account Registration

| Scenario 1.1 | Successful new account registration |
| :---: | :--- |
| Precondition | End User is on the application's "Create Account" screen. |
| Post condition | A new Account is created. The system prompts the user to pay for the subscription (UC2). |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Selects "Create Account". | 2. Displays the registration form. | FR5.5 |
| 3. Fills in the required details and clicks "Register". | 4. Validates the provided data | FR5.5 |
| | 5. Creates a new Account record in the database. | FR5.5 |
| | 6. Redirects the user to the subscription payment screen (initiating UC2). | FR5.4 |

##### Scenario 1.2: (Exception) Email Already In Use

| Scenario 1.2 | Email already in use |
| :---: | :--- |
| Precondition | End User is on the application's "Create Account" screen. |
| Post condition | A new Account is not created. The system shows an "Account with the inserted email already exists" notification. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Selects "Create Account". | 2. Displays the registration form. | FR5.5 |
| 3. Fills in the required details and clicks "Submit". | 4. Validates the provided data. | FR5.5 |
| | 5. Checks database and finds the email is already associated with another Account. | |
| | 6. Notifies the user that the provided email already exists. | |

---

### Use case 2, UC2: Payment of the Subscription

| Actors Involved | End User, Payment Service (External) |
| :---: | :--- |
| Precondition | An Account exists but its Subscription status is 'inactive' (Post-condition of UC1). |
| Post condition | The Account's Subscription status is set to 'active'. |
| Nominal Scenario | The End User provides valid payment details, the external Payment Service confirms the transaction, and the system activates the subscription. |
| Variants | 1v. End User pays for an expired subscription. |
| Exceptions | 1a. The Payment Service declines the transaction. <br> 2a. The Payment Service is unreachable. |

##### Scenario 2.1: Successful Subscription Activation

| Scenario 2.1 | Successful subscription activation |
| :---: | :--- |
| Precondition | End User is at the payment screen, prompted to pay. |
| Post condition | The Subscription status is set to 'true'. The user is granted access to the application's main features. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters credit card details and confirms payment. | | |
| | 2. Securely sends the payment request to the external Payment Service via API. | FR6.1 |
| | 3. (External Payment Service) Processes the payment and returns a 'success' confirmation. | FR6.1 |
| | 4. Receives the 'success' confirmation. | FR6.1 |
| | 5. Updates the Subscription status for the Account to 'active'. | FR5.3 |
| | 6. Displays the main application dashboard. | |

##### Scenario 2.2: (Variant) Pay for Expired Subscription

| Scenario 2.2 | Pay for expired subscription |
| :---: | :--- |
| Precondition | End User is logged in, but blocked from features due to an 'inactive' subscription. |
| Post condition | The Subscription status is set to 'true'. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Tries to log in (UC4). | 2. System checks subscription and finds it 'inactive'. | FR5.3 |
| | 3. System blocks access and redirects to the payment screen. | FR5.4 |
| 4. Follows steps 1-6 from Scenario 2.1. | | FR6.1, FR5.3 |

##### Scenario 2.3: (Exception) Payment Declined

| Scenario 2.3 | Payment declined |
| :---: | :--- |
| Precondition | End User is at the payment screen. |
| Post condition | The Subscription status remains 'inactive'. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters credit card details and confirms payment. | | |
| | 2. Securely sends the payment request to the external Payment Service via API. | FR6.1 |
| | 3. (External Payment Service) Processes the payment and returns a 'declined' message. | |
| | 4. Receives the 'declined' message. | |
| | 5. Displays an error message to the user. | |

##### Scenario 2.4: (Exception) Payment Service Unreachable

| Scenario 2.4 | Payment service unreachable |
| :---: | :--- |
| Precondition | End User is at the payment screen. |
| Post condition | The Subscription status remains 'inactive'. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters credit card details and confirms payment. | | |
| | 2. Attempts to send the payment request to the external Payment Service via API. | FR6.1 |
| | 3. The connection fails. | FR6.1 |
| | 4. Displays an error message to the user. | |

---

### Use case 3, UC3: Login Process

| Actors Involved | End User |
| :---: | :--- |
| Precondition | End User has an active Account. |
| Post condition | The End User is authenticated. |
| Nominal Scenario | The End User provides valid credentials and gains access to the system. |
| Variants | N/A |
| Exceptions | 1a. Invalid email or password. <br> 2a. Subscription is not active. <br> 3a. 2FA code is incorrect. |

##### Scenario 3.1: Successful Login

| Scenario 3.1 | Successful login |
| :---: | :--- |
| Precondition | End User is on the login screen. |
| Post condition | End User is logged in and the main dashboard is diplayed. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters email and password. Clicks "Login". | 2. Verifies credentials against the Account database. | FR5.1 |
| | 3. Prompts the user to enter their 2FA (Two-Factor Authentication) code. | NFR5 |
| 4. Enters the 2FA code. | 5. Validates the 2FA code. | NFR5 |
| | 6. Checks if the Subscription linked to the Account is 'active'. | FR5.3 |
| | 7. Creates an active session for the user. | |
| | 8. Displays the main application dashboard. | NFR6 |

##### Scenario 3.2: (Exception) Invalid Credentials

| Scenario 3.2 | Invalid email or password |
| :---: | :--- |
| Precondition | User is on the login screen. |
| Post condition | User is not logged in. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters incorrect email or password. Clicks "Login". | 2. Verifies credentials against the Account database and fails to find a match. | FR5.1 |
| | 3. Displays an error message. | |
| | 4. User remains on the login screen. | |

##### Scenario 3.3: (Exception) Subscription Inactive

| Scenario 3.3 | Subscription is not active |
| :---: | :--- |
| Precondition | User is on the login screen. |
| Post condition | User is logged in, but has no access to the main dashboard. He is instead redirected to payment (UC2). |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters email and password. Clicks "Login". | 2. Verifies credentials against the Account database (success). | FR5.1 |
| | 3. Checks if the Subscription status and find it is 'inactive'. | FR5.3 |
| | 4. Redirects the user to the subscription payment screen (initiating UC2). | FR5.4 |

##### Scenario 3.4: (Exception) Incorrect 2FA Code

| Scenario 3.4 | 2FA code is incorrect |
| :---: | :--- |
| Precondition | User has entered valid credentials and is on the 2FA screen. |
| Post condition | User is not logged in. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| | 1. (From Scenario 3.1) System has validated credentials and prompts for 2FA. | NFR5.1 |
| 2. Enters an incorrect or expired 2FA code. | 3. Fails to validate the 2FA code. | NFR5.1 |
| | 4. Displays an error message. | |
| | 5. User remains on the 2FA screen. | |

---

### Use case 4, UC4: Logout Process

| Actors Involved | End User |
| :---: | :--- |
| Precondition | User is currently logged in (Post-condition of UC4). |
| Post condition | The user's session is terminated. The system displays the login screen. |
| Nominal Scenario | The user clicks the "Logout" button and is successfully signed out. |
| Variants | N/A |
| Exceptions | N/A |

##### Scenario 4.1: Successful Logout

| Scenario 4.1 | Successful logout |
| :---: | :--- |
| Precondition | User is logged in and interacting with the application. |
| Post condition | User is logged out and sees the login screen. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Clicks the "Logout" button. | | FR5.2 |
| | 2. Terminates and invalidates the user's active session. | |
| | 3. Redirects the user to the main login screen (UC4). | |

---

### Use case 5, UC5: Register a New Product

| Actors Involved | End User, Cash Register Software (External) |
| :---: | :--- |
| Precondition | User is logged in (UC4). |
| Post condition | A new Product record is created in the inventory database. |
| Nominal Scenario | (Manual) The End User navigates to the inventory section and manually fills in the details for a new product. |
| Variants | N/A |
| Exceptions | 1a. The barcode or product ID already exists. <br> 2a. Invalid data (e.g., negative quantity, missing name). |

##### Scenario 5.1: Manual Product Registration

| Scenario 5.1 | Manual product registration |
| :---: | :--- |
| Precondition | User is logged in and in the "Inventory" or "Products" section. |
| Post condition | A new Product record is saved to the database. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Clicks "Add New Product". | 2. Displays the new product form (name, barcode, current_quantity, price, low_stock_threshold). | FR2.1 |
| 3. Fills in the product details and clicks "Save". | 4. Validates the data. | |
| | 5. Saves the new Product record to the database. | FR2.1 |
| | 6. Displays a "Product Saved" success message. | |


##### Scenario 5.2: (Exception) Barcode Already Exists

| Scenario 5.2 | Barcode already exists |
| :---: | :--- |
| Precondition | User is in the "Add New Product" form (Scenario 6.1). |
| Post condition | The new product is not saved. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Fills in product details, including a barcode that already exists. Clicks "Save". | 2. Validates the data and finds the barcode is not unique. | FR2.1 |
| | 3. Displays an error message: "This barcode is already in use by another product." | |
| | 4. User remains on the product form. | |

##### Scenario 5.3: (Exception) Invalid Data

| Scenario 5.3 | Invalid data |
| :---: | :--- |
| Precondition | User is in the "Add New Product" form (Scenario 6.1). |
| Post condition | The new product is not saved. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Fills in product details but omits the name. Clicks "Save". | 2. Validates the data and finds the 'name' field is required. | FR2.1 |
| | 3. Displays an error message: "Product name is required." | |
| | 4. User remains on the product form. | |

---

### Use case 6, UC6: Record a New Sale

| Actors Involved | End User |
| :---: | :--- |
| Precondition | Product(s) exist in the inventory (UC6). |
| Post condition | A new Sale (Transaction) record is created. The Product.current_quantity for sold items is decreased. |
| Nominal Scenario | The End User manually enters a sale into the EZShop interface. |
| Variants | N/A |
| Exceptions | 1a. Product not found in inventory. <br> 2a. API connection failure. |

##### Scenario 6.1: (Variant) Manual Sale Record

| Scenario 6.1 | Manual sale record |
| :---: | :--- |
| Precondition | User is logged in. |
| Post condition | Sale record is created. Product inventory is updated. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Navigates to "Sales" and clicks "Add Manual Sale". | 2. Displays a form to select products and enter quantities and other details. | FR1.1 |
| 3. Selects products/quantities and clicks "Save". | 4. Performs steps 3-6 from Scenario 7.1. | FR1.1, FR2.1, FR2.2 |

##### Scenario 6.3: (Exception) Product Not Found

| Scenario 6.3 | Product not found |
| :---: | :--- |
| Precondition | System receives sale data (manual or automatic). |
| Post condition | Sale record is (partially) created, but inventory for the unknown item is not updated. An alert is logged. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| | 1. Receives sale data including an item with a barcode 'XYZ' that is not in the Product database. | FR1.1 |
| | 2. Creates the Sale record. | FR1.1 |
| | 3. Attempts to update inventory for barcode 'XYZ', but fails. | FR2.1 |
| | 4. Logs an error: "Sold item 'XYZ' not found in inventory. Stock not updated." | |
| | 5. (Optional) Creates a placeholder Product (see UC5, Scenario 5.2). | FR2.1 |


---

### Use case 7, UC7: Record a Refund

| Actors Involved | Cash Register Software (Primary), End User (Secondary) |
| :---: | :--- |
| Precondition | A previous Sale transaction exists. Product(s) exist. |
| Post condition | A new Refund (Transaction) record is created. The Product.current_quantity for refunded items is increased. |
| Nominal Scenario | (Automatic) The Cash Register reports a refund, and the system records it and updates (restocks) inventory. |
| Variants | 1v. (Manual) The End User manually enters a refund. |
| Exceptions | 1a. Original sale not found (if refund requires it). |

##### Scenario 7.1: (Nominal) Automatic Refund Record from POS

| Scenario 7.1 | Automatic refund record from POS |
| :---: | :--- |
| Precondition | A customer refund is processed at the Cash Register. |
| Post condition | Refund record is created. Product inventory is restocked. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. (Cash Register) Sends refund data (list of items) via API. | | FR6.1, FR6.2 |
| | 2. Receives the refund data. | NFR3 |
| | 3. Creates a new Refund record. | FR1.2 |
| | 4. For each refunded item: <br> &nbsp;&nbsp; a. Finds the matching Product. <br> &nbsp;&nbsp; b. Increases the Product.current_quantity. | FR2.1 |

##### Scenario 7.2: (Variant) Manual Refund Record

| Scenario 7.2 | Manual refund record |
| :---: | :--- |
| Precondition | User is logged in. |
| Post condition | Refund record is created. Product inventory is restocked. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Navigates to "Refunds" and clicks "Add Manual Refund". | 2. Displays a form to select products and enter quantities. | FR1.2 |
| 3. Selects products/quantities (and optionally links to original sale) and clicks "Save". | 4. Performs steps 3-4 from Scenario 7.1. | FR1.2, FR2.1 |

##### Scenario 7.3: (Exception) Original Sale Not Found

| Scenario 7.3 | Original sale not found |
| :---: | :--- |
| Precondition | User is in the "Manual Refund" form (Scenario 7.2) and the process requires linking to an original sale. |
| Post condition | Refund is not created. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Tries to create a manual refund, entering an original sale ID '123'. | 2. System searches for Sale ID '123' and does not find it. | FR1.2 |
| | 3. Displays an error: "Original Sale ID not found." | |
| | 4. User remains on the refund form. | |

---

### Use case 8, UC8: Manage Supplier Contacts

| Actors Involved | End User |
| :---: | :--- |
| Precondition | User is logged in (UC4). |
| Post condition | The Supplier database table is modified (record created, updated, or deleted). |
| Nominal Scenario | The user accesses the "Suppliers" section and performs Create, Read, Update, or Delete (CRUD) operations on supplier records. |
| Variants | N/A |
| Exceptions | 1a. Invalid data (e.g., missing supplier name or email). <br> 2a. Cannot delete a supplier with existing orders. |

##### Scenario 8.1: (Nominal) Add a New Supplier

| Scenario 8.1 | Add a new supplier |
| :---: | :--- |
| Precondition | User is logged in and in the "Suppliers" section. |
| Post condition | A new Supplier record is created. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Clicks "Add New Supplier". | 2. Displays the new supplier form (company_name, email). | FR3.1 |
| 3. Fills in the supplier details and clicks "Save". | 4. Validates the data. | |
| | 5. Creates a new Supplier record in the database. | FR3.1 |
| | 6. Displays the updated list of suppliers. | FR3.1 (Read) |

##### Scenario 8.2: (Nominal) Update a Supplier

| Scenario 8.2 | Update a supplier |
| :---: | :--- |
| Precondition | User is in the "Suppliers" section. A supplier exists. |
| Post condition | The Supplier record is updated. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Selects a supplier from the list and clicks "Edit". | 2. Displays the supplier form populated with existing data. | FR3.1 (Read) |
| 3. Changes the supplier's email address and clicks "Save". | 4. Validates the data. | |
| | 5. Updates the Supplier record in the database. | FR3.1 (Update) |

##### Scenario 8.3: (Nominal) Delete a Supplier

| Scenario 8.3 | Delete a supplier |
| :---: | :--- |
| Precondition | User is in the "Suppliers" section. A supplier (with no associated orders) exists. |
| Post condition | The Supplier record is deleted. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Selects a supplier from the list and clicks "Delete". | 2. Displays a confirmation prompt: "Are you sure?" | FR3.1 |
| 3. Confirms the deletion. | 4. Checks for associated Order records (finds none). | |
| | 5. Deletes the Supplier record from the database. | FR3.1 (Delete) |

##### Scenario 8.4: (Exception) Cannot Delete Supplier with Orders

| Scenario 8.4 | Cannot delete supplier with existing orders |
| :---: | :--- |
| Precondition | User attempts to delete a supplier (Scenario 8.3). |
| Post condition | The Supplier record is not deleted. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Confirms the deletion of a supplier. | 2. Checks for associated Order records and finds existing orders linked to this supplier. | FR3.1 |
| | 3. Does not delete the supplier. | |
| | 4. Displays an error: "Cannot delete supplier. They are associated with existing purchase orders." | |

---

### Use case 9, UC9: Submit a New Purchase Order

| Actors Involved | End User |
| :---: | :--- |
| Precondition | User is logged in (UC4). At least one Supplier (UC9) and one Product (UC6) exist. |
| Post condition | An Order record (with OrderItems) is created. An email is sent to the supplier. |
| Nominal Scenario | The user creates a new purchase order, adds products, and submits it. The system saves the order and emails the supplier. |
| Variants | N/A |
| Exceptions | 1a. Supplier email address is missing. <br> 2a. The email sending service fails. |

##### Scenario 9.1: Create and Send Purchase Order

| Scenario 9.1 | Create and send purchase order |
| :---: | :--- |
| Precondition | User is in the "Purchase Orders" section. |
| Post condition | Order is saved with 'Sent' status. Email is sent to the supplier. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Clicks "New Purchase Order". | 2. Prompts user to select a Supplier from the list. | FR3.2 |
| 3. Selects a Supplier. | 4. Displays the new order form. | |
| 5. Adds Products and specifies quantities for each. | | FR3.2 |
| 6. Clicks "Submit Order". | 7. Saves the Order and its OrderItems to the database (status 'Pending'). | FR3.4 |
| | 8. Generates an email (e.g., PDF) with the order details. | FR3.3 |
| | 9. Sends the email to the selected Supplier.email. | FR3.3 |
| | 10. Updates the Order status to 'Sent'. | FR3.4 |

##### Scenario 9.2: (Exception) Supplier Email Missing

| Scenario 9.2 | Supplier email address is missing |
| :---: | :--- |
| Precondition | User clicks "Submit Order" (Scenario 9.1, step 6). |
| Post condition | Order is saved with status 'Pending' or 'Draft'. Email is not sent. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| | 1. Saves the Order. | FR3.4 |
| | 2. Attempts to retrieve Supplier.email to send the email. | FR3.3 |
| | 3. Finds the email field is null or empty. | |
| | 4. Does not send the email. Updates Order status to 'Draft' or 'Error'. | |
| | 5. Notifies the user: "Order saved as Draft. Cannot send: Supplier email is missing." | |

##### Scenario 9.3: (Exception) Email Sending Service Fails

| Scenario 9.3 | The email sending service fails |
| :---: | :--- |
| Precondition | User clicks "Submit Order" (Scenario 9.1, step 6). |
| Post condition | Order is saved with status 'Pending'. Email is not sent. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| | 1. Saves the Order. | FR3.4 |
| | 2. Generates the email. | FR3.3 |
| | 3. Attempts to send the email, but the external email service returns an error (e.g., 500). | FR3.3 |
| | 4. Does not update the Order status to 'Sent'. It remains 'Pending'. | |
| | 5. Notifies the user: "Order saved. Failed to send email. Please try sending again manually." | |

---

### Use case 10, UC10: Mark an Order as Completed

| Actors Involved | End User |
| :---: | :--- |
| Precondition | An Order exists with a 'Sent' status (Post-condition of UC10). The shop has received the physical products. |
| Post condition | The Order status is updated to 'Completed'. The Product.current_quantity for received items is increased. |
| Nominal Scenario | The user finds the pending order, confirms receipt of all items, and the system updates inventory. |
| Variants | 1v. (Partial Delivery) User marks only some items as received, Order status becomes 'Partially Received'. |
| Exceptions | 1a. User tries to mark an already completed order. |

##### Scenario 10.1: Receive Full Order

| Scenario 10.1 | Receive full order |
| :---: | :--- |
| Precondition | A physical delivery from a supplier has arrived. User is logged in. |
| Post condition | Order status is 'Completed'. Product inventory is restocked. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Navigates to "Purchase Orders" and finds the 'Sent' order. | | |
| 2. Clicks "Receive Stock" or "Mark as Completed". | 3. Displays the list of OrderItems from the order. | FR3.5 |
| 4. Confirms all quantities are correct and clicks "Confirm". | 5. Updates the Order status to 'Completed'. | FR3.5 |
| | 6. For each OrderItem in the order: <br> &nbsp;&nbsp; a. Finds the matching Product. <br> &nbsp;&nbsp; b. Increases Product.current_quantity by the received amount. | FR3.5, FR2.1 |

##### Scenario 10.2: (Variant) Receive Partial Order

| Scenario 10.2 | Receive partial order |
| :---: | :--- |
| Precondition | A partial delivery has arrived. User is logged in. |
| Post condition | Order status is 'Partially Received'. Inventory is updated only for received items. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Navigates to the 'Sent' order. Clicks "Receive Stock". | 2. Displays the list of expected OrderItems (e.g., 10x 'Apple', 5x 'Banana'). | FR3.5 |
| 3. Edits the received quantity (e.g., to 10x 'Apple', 0x 'Banana'). Clicks "Confirm". | 4. Validates the partial quantities. | |
| | 5. Updates the Order status to 'Partially Received'. | FR3.5 |
| | 6. Increases Product.current_quantity for 'Apple' by 10. | FR3.5, FR2.1 |
| | 7. Does not update inventory for 'Banana'. | |

##### Scenario 10.3: (Exception) Order Already Completed

| Scenario 10.3 | Order already completed |
| :---: | :--- |
| Precondition | User navigates to an order that is already marked 'Completed'. |
| Post condition | No change is made. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Finds a 'Completed' order. | | |
| | 2. The "Receive Stock" button is disabled. | FR3.5 |
| 3. (If button were enabled) Clicks "Receive Stock". | 4. System checks status and shows message: "This order is already completed. No further actions can be taken." | |

---

### Use case 11, UC11: Update Inventory (Manual Adjustment)

| Actors Involved | End User |
| :---: | :--- |
| Precondition | User is logged in (UC4). Product(s) exist (UC6). |
| Post condition | The Product.current_quantity is updated to a new specified value. |
| Nominal Scenario | User is doing a stock count, finds a discrepancy (due to theft, breakage, or error), and manually corrects the quantity in the system. |
| Variants | N/A |
| Exceptions | 1a. User enters an invalid quantity (e.g., non-numeric, negative). |

##### Scenario 11.1: Manual Stock Adjustment

| Scenario 11.1 | Manual stock adjustment |
| :---: | :--- |
| Precondition | User is in the "Inventory" section. |
| Post condition | The Product.current_quantity is updated. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Finds the Product to adjust. Clicks "Adjust Stock" or "Edit". | 2. Displays the product details, highlighting the current_quantity field. | FR2.1 (Read) |
| 3. Enters the new, correct quantity (e.g., changes '10' to '8'). | | |
| 4. Clicks "Save". | 5. Updates the Product.current_quantity in the database to the new value. | FR2.1 (Update) |
| | 6. (Optional) Creates a log entry for the stock adjustment. | |

##### Scenario 11.2: (Exception) Invalid Quantity Entered

| Scenario 11.2 | Invalid quantity entered |
| :---: | :--- |
| Precondition | User is in the stock adjustment form (Scenario 11.1). |
| Post condition | Inventory is not updated. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Enters an invalid quantity (e.g., "eight" or "-1"). | | |
| 2. Clicks "Save". | 3. Validates the input and finds it is not a valid, non-negative integer. | FR2.1 |
| | 4. Displays an error: "Quantity must be a whole number (0 or greater)." | |
| | 5. User remains on the adjustment form. | |

---

### Use case 12, UC12: Visualization of Data

| Actors Involved | End User |
| :---: | :--- |
| Precondition | User is logged in (UC4). Data (Sales, Orders) exists in the database. |
| Post condition | The user has viewed the requested charts and aggregated data. |
| Nominal Scenario | The user accesses the dashboard, views default charts, and applies filters to analyze data. |
| Variants | 1v. User exports data to CSV/XML for Accounting Software. |
| Exceptions |  |

##### Scenario 12.1: View and Filter Dashboard

| Scenario 12.1 | View and filter dashboard |
| :---: | :--- |
| Precondition | User is logged in. |
| Post condition | User views charts/data based on selected filters. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Clicks on the "Dashboard" or "Reports" tab. | 2. Queries the database. | FR4.4 |
| | 3. Displays default charts (e.g., Sales over time, Top Products). | FR4.1 |
| | 4. Displays computed metrics (Profits, Expenses, Taxes). | FR4.3 |
| 5. Selects a time range filter (e.g., "Last 30 days"). | | FR4.2 |
| | 6. Re-queries the database with the new filter. | NFR2 |
| | 7. Updates the charts and metrics to reflect the filtered data. | FR4.1, FR4.2 |

##### Scenario 12.2: (Variant) Export Data for Accounting

| Scenario 12.2 | Export data for accounting |
| :---: | :--- |
| Precondition | User is in the "Reports" section. |
| Post condition | A file (CSV/XML) is downloaded to the user's computer. |

Steps

| Actor's action | System action | FR needed |
| :--- | :--- | :---: |
| 1. Clicks "Export Data". | | FR6.2 |
| 2. Selects a date range and format (e.g., CSV). Clicks "Export". | 3. Queries the database for the relevant financial data. | FR4.3 |
| | 4. Formats the data into the standardized CSV/XML format. | FR6.2 |
| | 5. Prompts the user to save the file. | |
| 6. Saves the file. | | |



\<describe here scenarios instances of UC1>

\<a scenario is a sequence of steps that corresponds to a particular execution of one use case>

\<a scenario is a more formal description of a story>

\<only relevant scenarios should be described>



# Glossary

\<use UML class diagram to define important terms, or concepts in the domain of the application, and their relationships>

\<concepts must be used consistently all over the document, ex in use cases, requirements etc>

# System Design

\<describe here system design>

\<must be consistent with Context diagram>

# Hardware Software architecture

\<describe here the hardware software architecture using UML deployment diagram >
