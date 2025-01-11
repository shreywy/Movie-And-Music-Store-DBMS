import tkinter as tk
import customtkinter as ctk
import cx_Oracle
from tabulate import tabulate
import datetime

# Connects the program to the local Oracle DB
def connect_to_db():
    global connection, cursor
    try:
        update_terminal_output("----- EXECUTING connect_to_db -----")
        
        # point this to your installation directory of Oracle Instant Client
        cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\instantclient_23_6") # Initialize the Oracle client

        # if not working, try these:
        # run lsnrctl start in cmd
        # check services.msc for OracleServiceXElistener

        # Define connection details
        user = "SYS"  # Connecting as SYS user
        password = "123p"  # Password for SYS user
        dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XE")  # Default service name for Oracle XE
        encoding = "UTF-8"
        mode = cx_Oracle.SYSDBA

        # Connect to the Oracle database as SYSDBA
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn, encoding=encoding, mode=mode)
        cursor = connection.cursor()

        # Verify the connection
        update_terminal_output("Connection established successfully!")
        update_terminal_output("Oracle version: " + connection.version)

        # Run a test query to confirm functionality
        cursor.execute("SELECT 'Hello, Oracle XE!' FROM DUAL")
        result = cursor.fetchone()
        update_terminal_output("Test query result: " + result[0])

        # Update UI
        status_label.configure(text="Connected to Oracle XE!")
        connect_button.configure(state=tk.DISABLED, text="[Already Connected]")  # Disable button after connection

    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error connecting to database: {e}")
        status_label.configure(text=f"Error connecting to DB: {e}")


def create_tables():
    update_terminal_output("\n----- EXECUTING create_tables -----")
    # List of table creation SQL statements
    create_sql = [
        """
        CREATE TABLE Supplier (
            SupplierID INT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            ProductType VARCHAR(255),
            StreetNumber INT,
            StreetName VARCHAR(255),
            CityName VARCHAR(255),
            Province VARCHAR(255),
            Country VARCHAR(255),
            PostalCode VARCHAR(6)
        )
        """,
        """
        CREATE TABLE Product (
            ProductID INT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            StockQuantity INT DEFAULT 0 CHECK (StockQuantity >= 0),
            ReleaseDate DATE,
            Price DECIMAL(10, 2) CHECK (Price >= 0),
            RentalPrice DECIMAL(10, 2) CHECK (RentalPrice >= 0)
        )
        """,
        """
        CREATE TABLE Inventory (
            InventoryID INT PRIMARY KEY,
            Status VARCHAR(255),
            ProductID INT,
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        )
        """,
        """
        CREATE TABLE ProductSupplier (
            ProductID INT,
            SupplierID INT,
            PRIMARY KEY (ProductID, SupplierID),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
            FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
        )
        """,
        """
        CREATE TABLE Music (
            ProductID INT PRIMARY KEY,
            Genre VARCHAR(255), -- comma separated multi-value attribute
            Artist VARCHAR(255), -- comma separated multi-value attribute
            Producer VARCHAR(255), -- comma separated multi-value attribute
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        )
        """,
        """
        CREATE TABLE Movie (
            ProductID INT PRIMARY KEY,
            Genre VARCHAR(255), -- comma separated multi-value attribute
            Director VARCHAR(255), -- comma separated multi-value attribute
            Studio VARCHAR(255),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        )
        """,
        """
        CREATE TABLE Customer (
            CustomerID INT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            PhoneNumber VARCHAR(20),
            StoreStanding VARCHAR(255),
            WishlistItem VARCHAR(255)
        )
        """,
        """
        CREATE TABLE Rentals (
            RentalID INT PRIMARY KEY,
            RentalDate DATE NOT NULL,
            ReturnDate DATE,
            Status VARCHAR(255),
            CustomerID INT,
            FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
        )
        """,
        """
        CREATE TABLE InventoryCustomer (
            CustomerID INT,
            InventoryID INT,
            PRIMARY KEY (CustomerID, InventoryID),
            FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
        )
        """,
        """
        CREATE TABLE Transactions (
            TransactionID INT PRIMARY KEY,
            TransactionDate DATE NOT NULL,
            TransactionType VARCHAR(255),
            AmountExchanged DECIMAL(10, 2),
            CustomerID INT,
            InventoryID INT,
            FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
        )
        """,
        """
        CREATE TABLE InventoryProduct (
            InventoryID INT,
            ProductID INT,
            PRIMARY KEY (InventoryID, ProductID),
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        )
        """
    ]

    try:
        # Loop through the create SQL statements
        for sql in create_sql:
            try:
                cursor.execute(sql)
                update_terminal_output(f"Table created successfully.")
            except cx_Oracle.DatabaseError as e:
                message = str(e)[0:9]
                update_terminal_output(f"Table already exists. (error code: {message})")

        connection.commit()
        update_status("create_tables completed successfully")

    except cx_Oracle.DatabaseError as e:
        update_status(f"create_tables failed: {e}")
        update_terminal_output(f"Error creating tables: {e}")


def drop_tables():
    update_terminal_output("\n----- EXECUTING drop_tables -----")
    # List of table names to drop
    tables_to_drop = [
        "InventoryProduct",
        "Transactions",
        "InventoryCustomer",
        "Rentals",
        "Customer",
        "Movie",
        "Music",
        "ProductSupplier",
        "Inventory",
        "Product",
        "Supplier"
    ]

    try:
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
                update_terminal_output(f"Table {table} dropped successfully.")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error dropping table {table}: {e}")

        connection.commit()
        update_status("drop_tables completed successfully")

    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error dropping tables: {e}")
        update_status(f"drop_tables failed: {e}")


def populate_tables():
    update_terminal_output("\n----- EXECUTING populate_tables -----")

    # List of records to populate each table 
    suppliers = [
        (1, 'Universal Suppliers', 'Movies', 123, 'King St W', 'Toronto', 'ON', 'Canada', 'M5V1E3'),
        (2, 'Global Music Co', 'Music', 456, 'Queen St E', 'Toronto', 'ON', 'Canada', 'M5A1S3')]

    products = [
        (1, 'Inception Blu-ray', 10, '2022-01-01', 19.99, 5.99),
        (2, 'Imagine Dragons Album', 20, '2023-01-01', 15.99, 4.99)]

    inventory = [
        (1, 'Available', 1),
        (2, 'Rented', 2)]

    product_supplier = [
        (1, 1),
        (2, 2)]

    music = [
        (2, 'Rock', 'Imagine Dragons', 'Alex Da Kid')]

    movie = [
        (1, 'Sci-Fi', 'Christopher Nolan', 'Paramount Pictures')]

    customers = [
        (1, 'John Doe', '123-456-7890', 'Good', 'Interstellar Blu-ray'),
        (2, 'Jane Smith', '987-654-3210', 'Average', 'Imagine Dragons Album')]

    rentals = [
        (1, '2024-11-01', '2024-11-10', 'Returned', 1),
        (2, '2024-11-01', '2024-11-15', 'Rented', 2)]

    transactions = [
        (1, '2024-11-01', 'Purchase', 19.99, 1, 1),
        (2, '2024-11-01', 'Rental', 5.99, 2, 2)]

    inventory_customers = [
        (1, 1),
        (2, 2)]

    inventory_products = [
        (1, 1),
        (2, 1)]

    try:
        # Insert records into the tables
        for supplier in suppliers:
            try:
                cursor.execute("INSERT INTO Supplier VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)", supplier)
                update_terminal_output(f"Inserted into Supplier: {supplier}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into Supplier: {e}")

        for product in products:
            try:
                cursor.execute("INSERT INTO Product VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), :5, :6)", product)
                update_terminal_output(f"Inserted into Product: {product}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into Product: {e}")

        for record in inventory:
            try:
                cursor.execute("INSERT INTO Inventory VALUES (:1, :2, :3)", record)
                update_terminal_output(f"Inserted into Inventory: {record}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Duplicate record skipped in Inventory: {record}")

        for record in product_supplier:
            try:
                cursor.execute("INSERT INTO ProductSupplier VALUES (:1, :2)", record)
                update_terminal_output(f"Inserted into ProductSupplier: {record}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Duplicate record skipped in ProductSupplier: {record}")

        for record in music:
            try:
                cursor.execute("INSERT INTO Music VALUES (:1, :2, :3, :4)", record)
                update_terminal_output(f"Inserted into Music: {record}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Duplicate record skipped in Music: {record}")

        for record in movie:
            try:
                cursor.execute("INSERT INTO Movie VALUES (:1, :2, :3, :4)", record)
                update_terminal_output(f"Inserted into Movie: {record}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Duplicate record skipped in Movie: {record}")

        for customer in customers:
            try:
                cursor.execute("INSERT INTO Customer VALUES (:1, :2, :3, :4, :5)", customer)
                update_terminal_output(f"Inserted into Customer: {customer}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into Customer: {e}")

        for rental in rentals:
            try:
                cursor.execute(
                    "INSERT INTO Rentals VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), TO_DATE(:3, 'YYYY-MM-DD'), :4, :5)",
                    rental)
                update_terminal_output(f"Inserted into Rentals: {rental}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into Rentals: {e}")

        for transaction in transactions:
            try:
                cursor.execute("INSERT INTO Transactions VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6)",
                               transaction)
                update_terminal_output(f"Inserted into Transactions: {transaction}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into Transactions: {e}")

        for inventory_customer in inventory_customers:
            try:
                cursor.execute(
                    "INSERT INTO InventoryCustomer VALUES (:1, :2)",
                    inventory_customer
                )
                update_terminal_output(f"Inserted into InventoryCustomer: {inventory_customer}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into InventoryCustomer: {e}")

        for inventory_product in inventory_products:
            try:
                cursor.execute(
                    "INSERT INTO InventoryProduct VALUES (:1, :2)",
                    inventory_product
                )
                update_terminal_output(f"Inserted into InventoryProduct: {inventory_product}")
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error inserting into InventoryProduct: {e}")

        connection.commit()
        update_terminal_output("\nAll tables populated successfully.")

    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error populating tables: {e}")

def execute_custom_sql():
    """Execute the SQL code entered in the custom SQL textarea."""
    sql_code = sql_text_area.get("1.0", "end").strip()  # Get the SQL code from the textarea
    try:
        cursor.execute(sql_code)  # Execute the SQL command
        if sql_code.lower().startswith("select"):
            results = cursor.fetchall()  # Fetch results for SELECT queries
            columns = [desc[0] for desc in cursor.description]  # Get column names
            table = tabulate(results, headers=columns, tablefmt="grid")  # Format as a table
            update_terminal_output(f"Results:\n{table}")
        else:
            connection.commit()  # Commit changes for non-SELECT queries
            update_terminal_output("SQL executed successfully.")
    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error executing SQL: {e}")


# function has been replace with manage_entries
def show_table(table_selector):
    """Display the selected table's contents in a neatly formatted table design."""
    try:
        # Get the selected table
        selected_table = table_selector.get()
        cursor.execute(f"SELECT * FROM {selected_table}")
        records = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]

        if not records:
            update_terminal_output(f"The table {selected_table} is empty.")
            return

        # Create a new pop-up window
        popup = ctk.CTkToplevel()
        popup.title(f"Contents of {selected_table}")
        popup.geometry("800x600")

        # Format the table with | and _ to mimic a border
        def format_row(row, col_widths):
            """Helper function to format a row with fixed-width columns."""
            return "| " + " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)) + " |"

        # Calculate column widths based on the longest value in each column
        col_widths = [
            max(len(str(col)), max(len(str(row[i])) for row in records)) + 2
            for i, col in enumerate(column_names)
        ]

        # Create a table header
        header = format_row(column_names, col_widths)
        separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

        # Add a scrollable frame to the popup
        scrollable_frame = ctk.CTkScrollableFrame(popup, width=750, height=550)
        scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Display the table in the popup
        header_label = ctk.CTkLabel(scrollable_frame, text=separator, font=("Courier", 10))
        header_label.pack(anchor="w", pady=2)

        header_label = ctk.CTkLabel(scrollable_frame, text=header, font=("Courier", 10))
        header_label.pack(anchor="w", pady=2)

        separator_label = ctk.CTkLabel(scrollable_frame, text=separator, font=("Courier", 10))
        separator_label.pack(anchor="w", pady=2)

        # Display each record row
        for row in records:
            row_text = format_row(row, col_widths)
            row_label = ctk.CTkLabel(scrollable_frame, text=row_text, font=("Courier", 10))
            row_label.pack(anchor="w", pady=2)

        # Add a final separator
        footer_label = ctk.CTkLabel(scrollable_frame, text=separator, font=("Courier", 10))
        footer_label.pack(anchor="w", pady=2)

        update_terminal_output(f"Displayed contents of table: {selected_table}")
    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error fetching data from table {selected_table}: {e}")
        
def manage_entries(selected_table):
    """Open a window to manage entries in a selected table."""
    try:
        if not selected_table:
            update_terminal_output("Please select a table to manage entries.")
            return

        cursor.execute(f"SELECT * FROM {selected_table}")
        records = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]

        # Create a new pop-up window
        manage_window = ctk.CTkToplevel()
        manage_window.title(f"Manage Entries in {selected_table}")
        manage_window.geometry("900x700")
        manage_window.focus_force()  # Bring the window to the front

        # Show the table content
        def format_row(row, col_widths):
            """Helper function to format a row with fixed-width columns."""
            return "| " + " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)) + " |"

        col_widths = [
            max(len(str(col)), max(len(str(row[i])) for row in records)) + 2
            for i, col in enumerate(column_names)
        ]
        scrollable_frame = ctk.CTkScrollableFrame(manage_window, width=850, height=300)
        scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        header = format_row(column_names, col_widths)
        ctk.CTkLabel(scrollable_frame, text=separator, font=("Courier", 10)).pack(anchor="w", pady=2)
        ctk.CTkLabel(scrollable_frame, text=header, font=("Courier", 10)).pack(anchor="w", pady=2)
        ctk.CTkLabel(scrollable_frame, text=separator, font=("Courier", 10)).pack(anchor="w", pady=2)
        for row in records:
            row_text = format_row(row, col_widths)
            ctk.CTkLabel(scrollable_frame, text=row_text, font=("Courier", 10)).pack(anchor="w", pady=2)
        ctk.CTkLabel(scrollable_frame, text=separator, font=("Courier", 10)).pack(anchor="w", pady=2)

        # Dropdown for selecting a record to modify/remove
        selected_record = ctk.StringVar()
        record_dropdown = ctk.CTkComboBox(
            manage_window, 
            values=[str(record) for record in records], 
            variable=selected_record, 
            height=40, 
            width=700
        )
        record_dropdown.pack(pady=10)

        # Modify Entry Button
        def open_modify_window():
            """Open a window to modify a selected record."""
            record = selected_record.get()
            if not record:
                update_terminal_output("Please select a record to modify.")
                return
            modify_window = ctk.CTkToplevel()
            modify_window.title(f"Modify Record in {selected_table}")
            modify_window.geometry("500x400")
            modify_window.focus_force()  # Bring the modify window to the front

            selected_row = eval(record)  # Convert the string back to a tuple

            # Dropdown for selecting the column to modify
            selected_column = ctk.StringVar()
            column_dropdown = ctk.CTkComboBox(
                modify_window, 
                values=column_names, 
                variable=selected_column, 
                height=40, 
                width=300
            )
            column_dropdown.pack(pady=10)

            # Entry for new value
            new_value_entry = ctk.CTkEntry(modify_window, width=300, placeholder_text="Enter new value")
            new_value_entry.pack(pady=10)

            def apply_modification():
                """Apply the modification to the selected record."""
                column = selected_column.get()
                new_value = new_value_entry.get()
                if not column or not new_value:
                    update_terminal_output("Please select a column and enter a new value.")
                    return
                primary_key = column_names[0]  # Assuming first column is the primary key
                primary_value = selected_row[0]
                try:
                    cursor.execute(
                        f"UPDATE {selected_table} SET {column} = :new_value WHERE {primary_key} = :primary_value",
                        {"new_value": new_value, "primary_value": primary_value}
                    )
                    connection.commit()
                    update_terminal_output(f"Modified record: {record}")
                    modify_window.destroy()
                    manage_window.destroy()  # Close the current manage window
                    manage_entries(selected_table)  # Reopen the manage entries window
                except cx_Oracle.DatabaseError as e:
                    update_terminal_output(f"Error modifying record: {e}")

            apply_button = ctk.CTkButton(modify_window, text="Apply", command=apply_modification)
            apply_button.pack(pady=10)

        modify_button = ctk.CTkButton(manage_window, text="Modify Record", command=open_modify_window, height=40, width=200)
        modify_button.pack(pady=5)

        # Remove Entry Button
        def remove_entry():
            """Remove the selected record."""
            record = selected_record.get()
            if not record:
                update_terminal_output("Please select a record to remove.")
                return
            selected_row = eval(record)  # Convert the string back to a tuple
            primary_key = column_names[0]  # Assuming first column is the primary key
            primary_value = selected_row[0]
            try:
                cursor.execute(f"DELETE FROM {selected_table} WHERE {primary_key} = :primary_value", {"primary_value": primary_value})
                connection.commit()
                update_terminal_output(f"Removed record: {record}")
                manage_window.destroy()  # Close the current manage window
                manage_entries(selected_table)  # Reopen the manage entries window
            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error removing record: {e}")

        remove_button = ctk.CTkButton(manage_window, text="Remove Record", command=remove_entry, height=40, width=200)
        remove_button.pack(pady=5)

        # Add Entry Button
        def open_add_entry_window():
            """Open a window to add a new record."""
            add_window = ctk.CTkToplevel()
            add_window.title(f"Add Record to {selected_table}")
            add_window.geometry("500x600")
            add_window.focus_force()  # Bring the add window to the front

            entry_fields = []
            for column in column_names:
                label = ctk.CTkLabel(add_window, text=f"{column}:", font=("Arial", 12))
                label.pack(pady=5)
                entry = ctk.CTkEntry(add_window, width=400)
                entry.pack(pady=5)
                entry_fields.append(entry)

            def add_record():
                """Add a new record to the table."""
                values = [entry.get() for entry in entry_fields]
                if any(value.strip() == "" for value in values):
                    update_terminal_output("All fields must be filled.")
                    return
                try:
                    placeholders = ", ".join([":" + str(i + 1) for i in range(len(values))])
                    cursor.execute(
                        f"INSERT INTO {selected_table} VALUES ({placeholders})", 
                        values
                    )
                    connection.commit()
                    update_terminal_output(f"Added record: {values}")
                    add_window.destroy()
                    manage_window.destroy()  # Close the current manage window
                    manage_entries(selected_table)  # Reopen the manage entries window
                except cx_Oracle.DatabaseError as e:
                    update_terminal_output(f"Error adding record: {e}")

            add_button = ctk.CTkButton(add_window, text="Add Record", command=add_record)
            add_button.pack(pady=10)

        add_button = ctk.CTkButton(manage_window, text="Add Record", command=open_add_entry_window, height=40, width=200)
        add_button.pack(pady=5)

    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error fetching data from table {selected_table}: {e}")

def search_tables():
    """Search specific tables for the term in the search field."""
    search_term = sql_text_area.get("1.0", "end").strip()  # Get the search term from the textarea
    if not search_term:
        update_terminal_output("Please enter a search term.")
        return
    
    # List of tables to search
    tables = [
        "InventoryProduct",
        "Transactions",
        "InventoryCustomer",
        "Rentals",
        "Customer",
        "Movie",
        "Music",
        "ProductSupplier",
        "Inventory",
        "Product",
        "Supplier",
    ]

    try:
        # List to store results
        results = []

        # Loop through all tables and search for the term
        for table_name in tables:
            try:
                # Query all records from the table
                query = f"SELECT * FROM {table_name}"
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Filter rows that contain the search term
                matching_rows = []
                for row in rows:
                    for value in row:
                        # If the value is a string and contains the search term, add the row to the matching_rows list
                        if isinstance(value, str) and search_term.lower() in value.lower():
                            matching_rows.append(row)
                            break  # No need to search further in this row, move to the next one

                # If there are matching rows, format them as a table
                if matching_rows:
                    formatted_table = tabulate(matching_rows, headers=columns, tablefmt="grid")
                    results.append((table_name, formatted_table))

            except cx_Oracle.DatabaseError as e:
                update_terminal_output(f"Error querying table {table_name}: {e}")

        # If no results found, display message
        if not results:
            update_terminal_output(f"No matching records found for '{search_term}'.")
            return

        # Create a new window to display the results
        popup = ctk.CTkToplevel()
        popup.title(f"Search Results for '{search_term}'")
        popup.geometry("800x600")

        # Add results to the popup window
        scrollable_frame = ctk.CTkScrollableFrame(popup, width=750, height=550)
        scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        for table_name, formatted_table in results:
            header_label = ctk.CTkLabel(scrollable_frame, text=f"Found Entry in Table: {table_name}", font=("Arial", 14, "bold"))
            header_label.pack(anchor="w", pady=5)

            result_label = ctk.CTkLabel(scrollable_frame, text=formatted_table, font=("Courier", 10))
            result_label.pack(anchor="w", pady=5)

        update_terminal_output(f"Search completed for term: {search_term}")

    except cx_Oracle.DatabaseError as e:
        update_terminal_output(f"Error during search: {e}")

def update_terminal_output(message):
    """Update the terminal output (console window)."""
    terminal_output.insert(tk.END, message + '\n')
    terminal_output.yview(tk.END)

def update_status(message):
    """Update the status box with a final completion message."""
    status_label.configure(text=message)

def main():
    # Initialize GUI
    global root, connect_button, status_label, cursor, connection, sql_text_area, terminal_output, selected_table
    root = ctk.CTk()

    # Set window title and size
    root.title("Movie and Music Store Database")
    root.geometry("1200x500")  # Fixed window size
    root.resizable(False, False)  # Prevent resizing

    # Configure grid layout
    root.grid_rowconfigure(0, weight=0)  # Top row fixed height
    root.grid_rowconfigure(1, weight=1)  # Middle row with terminal and text areas
    root.grid_columnconfigure(0, weight=1, uniform="column")  # Uniform width for both halves
    root.grid_columnconfigure(1, weight=1, uniform="column")

    # Create the top box for status message
    status_frame = ctk.CTkFrame(root, width=600, height=40, corner_radius=10, border_width=2, border_color="white")
    status_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
    status_frame.grid_propagate(False)  # Prevent frame from resizing
    status_label = ctk.CTkLabel(status_frame, text="Status", font=("Arial", 14), anchor="w", justify=tk.LEFT)
    status_label.grid(row=0, column=0, padx=20, pady=(5, 0), sticky="w")

    # Custom SQL Label
    sql_label = ctk.CTkLabel(root, text="Enter Custom SQL / Search:", font=("Arial", 14))
    sql_label.grid(row=0, column=1, padx=20, pady=(5, 0), sticky="w")

    # Terminal Output Box
    terminal_output = ctk.CTkTextbox(root, width=600, height=200, corner_radius=10, border_width=2)
    terminal_output.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="n")
    terminal_output.grid_propagate(False)  # Prevent resizing of the terminal box

    # Custom SQL Text Area
    sql_text_area = ctk.CTkTextbox(root, width=600, height=200, corner_radius=10, border_width=2)
    sql_text_area.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="n")
    sql_text_area.grid_propagate(False)  # Prevent resizing of the text area

    # Create the "Connect" button
    connect_button = ctk.CTkButton(root, text="Connect to DB", command=connect_to_db, height=40, width=200)
    connect_button.grid(row=2, column=0, pady=5)

    # Create buttons for actions
    create_button = ctk.CTkButton(root, text="Create Tables", command=create_tables, height=40, width=200)
    create_button.grid(row=3, column=0, pady=5)

    drop_button = ctk.CTkButton(root, text="Drop Tables", command=drop_tables, height=40, width=200)
    drop_button.grid(row=4, column=0, pady=5)

    populate_button = ctk.CTkButton(root, text="Populate Tables", command=populate_tables, height=40, width=200)
    populate_button.grid(row=5, column=0, pady=5)
    
    execute_sql_button = ctk.CTkButton(root, text="Execute SQL Command", command=execute_custom_sql, height=40, width=200)
    execute_sql_button.grid(row=2, column=1, pady=5)

    # Create buttons for table interaction
    tables = [
        "InventoryProduct",
        "Transactions",
        "InventoryCustomer",
        "Rentals",
        "Customer",
        "Movie",
        "Music",
        "ProductSupplier",
        "Inventory",
        "Product",
        "Supplier",
    ]
    table_selector = ctk.CTkComboBox(root, values=tables, height=40, width=400)
    table_selector.grid(row=3, column=1, pady=5)  

    # Single button for entry management
    manage_button = ctk.CTkButton(root, text="Show Table and Manage Entries", command=lambda: manage_entries(table_selector.get()), height=40, width=200)
    manage_button.grid(row=4, column=1, pady=5)
    
    # Show Table Button - replaced with manage_entries
    #select_table_button = ctk.CTkButton(root, text="Show Selected Table", command=lambda: show_table(table_selector), height=40, width=200)
    #select_table_button.grid(row=5, column=1, pady=5)  
    
    #search function
    select_table_button = ctk.CTkButton(root, text="Search", command=search_tables, height=40, width=200)
    select_table_button.grid(row=5, column=1, pady=5)  

    # Start the GUI loop
    root.mainloop()



# Run the application
if __name__ == "__main__":
    main()
