\# End-to-End Database Architecture with Stored Procedures for Sales Order Management



\## Overview

This project focuses on building a robust and scalable database system for managing a sales order workflow. It is developed using MySQL with procedural logic embedded through stored procedures and triggers, and implemented via Jupyter Notebooks for better clarity and testing. The primary goal is to streamline order management, inventory control, and data auditing in a retail-style environment.



\## Key Features

\- \*\*Normalized Database Design:\*\* Fully normalized schema up to 3NF to remove redundancy and improve consistency.

\- \*\*Entity Relationships:\*\* Designed entities for Customers, Employees, Products, Orders, and OrderDetails with appropriate foreign key constraints to maintain referential integrity.

\- \*\*Stored Procedures:\*\* Core business logic encapsulated in stored procedures to automate cart insertion, validate stock, and manage order transactions.

\- \*\*Advanced Triggers:\*\* Audit triggers capture and log updates to the OrderDetails table for accountability and transparency.

\- \*\*Transaction Management:\*\* Implements TCL statements (`START TRANSACTION`, `COMMIT`, `ROLLBACK`) to ensure ACID compliance.

\- \*\*SQL Commands Used:\*\* Extensive use of DDL, DML, DCL, and TCL commands in schema definition and data operations.

\- \*\*Indexing:\*\* Optimized query performance through indexing on key columns like customer\_id, product\_id, and order\_id.



\## Technical Breakdown



\### Database Schema

\- Tables are created with appropriate data types, primary keys, and foreign key constraints.

\- All schema elements are constructed using standard SQL syntax and tested for integrity.



\### Procedure: `insert\_values\_cart`

\- Handles logic for inserting a product into the user's active cart.

\- Checks if the product exists and if stock is sufficient.

\- Verifies whether a pending order exists for the customer.

\- Either updates the existing cart or creates a new order with the selected items.

\- Automatically updates the stock levels in the product table after insertion.



\### Trigger: Audit Order Updates

\- A trigger is defined to execute after any update on the `OrderDetails` table.

\- Captures old and new values, logs them into an audit table with timestamps.

\- Helps maintain an auditable history of order modifications.



\### ACID Properties in Action

\- \*\*Atomicity:\*\* Multi-step transactions are either fully completed or rolled back if any failure occurs.

\- \*\*Consistency:\*\* Data validation rules and foreign keys ensure consistent state.

\- \*\*Isolation:\*\* Concurrent transactions are isolated from one another.

\- \*\*Durability:\*\* Committed transactions are permanently saved and recoverable.



\### Performance Optimization

\- Indexes are created on columns frequently used in WHERE clauses and joins to improve lookup speed.

\- Partitioning is considered for scalability in future expansions.



\## Challenges Solved

\- Avoided duplication in cart management using control logic inside procedures.

\- Audited complex updates using AFTER UPDATE triggers to maintain a clear data trail.

\- Ensured referential integrity even during high-volume transaction tests.



\## Future Enhancements

\- Integrate with a web-based frontend (Flask/Django) for real-time transaction processing.

\- Add business dashboards with Power BI or Tableau for reporting.

\- Enable import/export from Excel for bulk operations.

\- Expand the system to support multiple store branches.



\## Learning Outcomes

\- Acquired in-depth experience designing relational schemas with normalization.

\- Learned how to implement stored procedures and audit triggers for transaction automation.

\- Gained working knowledge of SQL command types and ACID principles.

\- Improved debugging and optimization techniques for large datasets.



