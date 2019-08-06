SET NAMES utf8mb4;
CREATE DATABASE `grimoire`;
USE `grimoire`;
#CREATE TABLE `Users` (  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,  `username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'anonymous',  `password` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '123',  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,  PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
#INSERT INTO `users` (`id`, `username`, `password`, `email`) VALUES (NULL, 'testuser', '123', 'test@test.com');
#INSERT INTO `users` (`id`, `username`, `password`, `email`) VALUES (NULL, 'd2user', 'd2ec8329', 'test@test.com');
CREATE TABLE `Guides` (    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,	`data` LONGBLOB,    PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;