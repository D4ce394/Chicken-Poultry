-- Create Roles table
CREATE TABLE Roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  permissions TEXT, -- disimpan sebagai JSON string
  createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create Users table
CREATE TABLE Users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fullname TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  roleId INTEGER,
  createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (roleId) REFERENCES Roles(id)
);

-- Insert dummy roles
INSERT INTO Roles (name, description, permissions)
VALUES 
  ('Admin', 'Full access to all features and settings.', '["Create", "Read", "Update", "Delete"]'),
  ('User', 'Limited access to features.', '["Read"]'),
  ('Manager', 'Access to management features.', '["Create", "Read", "Update"]');

-- Insert dummy users
INSERT INTO Users (fullname, email, password, roleId)
VALUES
  ('Sasha', 'sasha@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'Admin')),
  ('Jane Smith', 'jane.smith@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'User')),
  ('Michael Brown', 'michael.brown@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'Manager')),
  ('Emily Davis', 'emily.davis@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'User')),
  ('William Wilson', 'william.wilson@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'Admin')),
  ('Olivia Martinez', 'olivia.martinez@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'User')),
  ('James Anderson', 'james.anderson@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'Manager')),
  ('Sophia Thomas', 'sophia.thomas@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'User')),
  ('Benjamin Lee', 'benjamin.lee@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'Admin')),
  ('Ava Harris', 'ava.harris@example.com', 'hashed_password', (SELECT id FROM Roles WHERE name = 'User'));
