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
);

CREATE TABLE Product (
    ProductID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    StockQuantity INT DEFAULT 0 CHECK (StockQuantity >= 0),
    ReleaseDate DATE,
    Price DECIMAL(10, 2) CHECK (Price >= 0),
    RentalPrice DECIMAL(10, 2) CHECK (RentalPrice >= 0)
);

CREATE TABLE Inventory (
    InventoryID INT PRIMARY KEY,
    Status VARCHAR(255),
    ProductID INT,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE ProductSupplier (
    ProductID INT,
    SupplierID INT,
    PRIMARY KEY (ProductID, SupplierID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
);

CREATE TABLE Music (
    ProductID INT PRIMARY KEY,
    Genre VARCHAR(255), 
    Artist VARCHAR(255), 
    Producer VARCHAR(255), 
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE Movie (
    ProductID INT PRIMARY KEY,
    Genre VARCHAR(255),
    Director VARCHAR(255), 
    Studio VARCHAR(255),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(20),
    StoreStanding VARCHAR(255),
    WishlistItem VARCHAR(255)
);

CREATE TABLE Rentals (
    RentalID INT PRIMARY KEY,
    RentalDate DATE NOT NULL,
    ReturnDate DATE,
    Status VARCHAR(255),
    CustomerID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);

CREATE TABLE InventoryCustomer (
    CustomerID INT,
    InventoryID INT,
    PRIMARY KEY (CustomerID, InventoryID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
);

CREATE TABLE Transactions (
    TransactionID INT PRIMARY KEY,
    TransactionDate DATE NOT NULL,
    TransactionType VARCHAR(255),
    AmountExchanged DECIMAL(10, 2),
    CustomerID INT,
    InventoryID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
);

CREATE TABLE InventoryProduct (
    InventoryID INT,
    ProductID INT,
    PRIMARY KEY (InventoryID, ProductID),
    FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);
