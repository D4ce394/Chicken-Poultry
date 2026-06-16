const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Path ke database SQLite
const dbPath = path.join(__dirname, 'src', 'sv-fs.sqlite');

// Data admin yang akan di-insert
const adminData = {
  id: uuidv4(),
  name: 'Admin',
  email: 'admin@admin.com',
  username: 'admin',
  password: 'Admin123!', // Password yang akan di-hash
  roleId: 1, // Role ID untuk admin (sesuaikan jika perlu)
  isApproved: true,
  department: 'IT',
  isOnline: false,
  lastLogin: null,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
};

async function seedAdmin() {
  try {
    // Hash password
    const hashedPassword = await bcrypt.hash(adminData.password, 10);
    
    // Buka koneksi ke database
    const db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Error opening database:', err.message);
        return;
      }
      console.log('Connected to SQLite database');
    });

    // Insert role admin terlebih dahulu (jika belum ada)
    const insertRole = `
      INSERT OR IGNORE INTO Roles (id, name, description, permissions, createdAt, updatedAt)
      VALUES (?, ?, ?, ?, ?, ?)
    `;

    db.run(insertRole, [
      1,
      'admin',
      'Administrator with full access',
      JSON.stringify(['all']),
      new Date().toISOString(),
      new Date().toISOString()
    ], function(err) {
      if (err) {
        console.error('Error inserting role:', err.message);
      } else {
        console.log('✓ Role admin created/verified');
      }
    });

    // Insert user admin
    const insertUser = `
      INSERT INTO Users (id, name, email, username, password, role_id, is_approved, department, is_online, last_login, createdAt, updatedAt)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(insertUser, [
      adminData.id,
      adminData.name,
      adminData.email,
      adminData.username,
      hashedPassword,
      adminData.roleId,
      adminData.isApproved ? 1 : 0,
      adminData.department,
      adminData.isOnline ? 1 : 0,
      adminData.lastLogin,
      adminData.createdAt,
      adminData.updatedAt
    ], function(err) {
      if (err) {
        console.error('Error inserting admin user:', err.message);
      } else {
        console.log('✓ Admin user created successfully!');
        console.log('\n=== Admin Credentials ===');
        console.log('Email:', adminData.email);
        console.log('Username:', adminData.username);
        console.log('Password:', adminData.password);
        console.log('=========================\n');
      }
    });

    // Tutup koneksi database
    db.close((err) => {
      if (err) {
        console.error('Error closing database:', err.message);
      } else {
        console.log('Database connection closed');
      }
    });

  } catch (error) {
    console.error('Error seeding admin:', error);
  }
}

// Jalankan seeder
seedAdmin();
