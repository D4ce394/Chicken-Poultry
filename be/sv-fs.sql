-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: May 19, 2025 at 12:44 PM
-- Server version: 8.0.40
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sv-fs.sqlite`
--

-- --------------------------------------------------------

--
-- Table structure for table `sequelize_migrations`
--

CREATE TABLE `sequelize_migrations` (
  `name` varchar(255) COLLATE utf8mb3_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

--
-- Dumping data for table `sequelize_migrations`
--

INSERT INTO `sequelize_migrations` (`name`) VALUES
('20241025023422-create-user.js');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `name`, `username`, `password`, `created_at`, `updated_at`) VALUES
('3ed081c9-fff2-4209-99eb-b068063b0066', 'peco@gmail.com', 'Peco Bagnaia', 'peco-marud2s6', '$2b$10$cyNEUgD9t/vIxZk9/yI3euSNz6G9eD79AeHtB7uJoiS6qOKccEgGu', '2025-05-17 15:23:38', '2025-05-17 15:23:38'),
('95eba1ff-3265-4b70-81c6-5c8636688db4', 'jorge@gmail.com', 'Jorge Martin', 'jorge-mary3luj', '$2b$10$wjIwZ8/GLUSasceQp8JZ/.G/Dh7APspuASKvLrFpAvZ61jaaYdEwC', '2025-05-17 17:08:15', '2025-05-17 17:08:15');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `sequelize_migrations`
--
ALTER TABLE `sequelize_migrations`
  ADD PRIMARY KEY (`name`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
