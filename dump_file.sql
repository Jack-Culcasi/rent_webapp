-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: database_name
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('2d10b752c2dd');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `start_datetime` datetime NOT NULL,
  `end_datetime` datetime NOT NULL,
  `car_plate` varchar(8) NOT NULL,
  `user_id` int NOT NULL,
  `note` varchar(160) DEFAULT NULL,
  `money` int DEFAULT NULL,
  `km` int DEFAULT NULL,
  `contact_id` int DEFAULT NULL,
  `group_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `car_plate` (`car_plate`),
  KEY `booking_contacts_id` (`contact_id`),
  KEY `booking_group` (`group_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_booking_km` (`km`),
  KEY `ix_booking_money` (`money`),
  CONSTRAINT `booking_contacts_id` FOREIGN KEY (`contact_id`) REFERENCES `contacts` (`id`),
  CONSTRAINT `booking_group` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`car_plate`) REFERENCES `car` (`plate`),
  CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (1,'2024-03-20 12:49:00','2024-03-23 12:49:00','SZ654SZ',3,'33333',50,100,1,1);
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `car`
--

DROP TABLE IF EXISTS `car`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `car` (
  `plate` varchar(8) NOT NULL,
  `make` varchar(15) DEFAULT NULL,
  `model` varchar(15) DEFAULT NULL,
  `fuel` varchar(8) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `cc` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `days` int DEFAULT NULL,
  `money` int DEFAULT NULL,
  `car_cost` int DEFAULT NULL,
  `insurance_cost` float DEFAULT NULL,
  `insurance_expiry_date` datetime DEFAULT NULL,
  `mot_cost` float DEFAULT NULL,
  `mot_expiry_date` datetime DEFAULT NULL,
  `road_tax_cost` float DEFAULT NULL,
  `road_tax_expiry_date` datetime DEFAULT NULL,
  `km` int DEFAULT NULL,
  PRIMARY KEY (`plate`),
  UNIQUE KEY `ix_car_plate` (`plate`),
  KEY `user_id` (`user_id`),
  KEY `ix_car_car_cost` (`car_cost`),
  KEY `ix_car_cc` (`cc`),
  KEY `ix_car_days` (`days`),
  KEY `ix_car_fuel` (`fuel`),
  KEY `ix_car_insurance_cost` (`insurance_cost`),
  KEY `ix_car_km` (`km`),
  KEY `ix_car_make` (`make`),
  KEY `ix_car_model` (`model`),
  KEY `ix_car_money` (`money`),
  KEY `ix_car_mot_cost` (`mot_cost`),
  KEY `ix_car_road_tax_cost` (`road_tax_cost`),
  KEY `ix_car_year` (`year`),
  CONSTRAINT `car_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `car`
--

LOCK TABLES `car` WRITE;
/*!40000 ALTER TABLE `car` DISABLE KEYS */;
INSERT INTO `car` VALUES ('SZ654SZ','Seat','Ibiza','Petrol',2005,1250,3,4,50,50,50,'2024-04-06 00:00:00',0,NULL,0,NULL,100);
/*!40000 ALTER TABLE `car` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contacts`
--

DROP TABLE IF EXISTS `contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(128) DEFAULT NULL,
  `driver_licence_n` int DEFAULT NULL,
  `dob` varchar(10) DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `user_id` int NOT NULL,
  `money_spent` int DEFAULT NULL,
  `rented_days` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contacts_user_id` (`user_id`),
  KEY `ix_contacts_dob` (`dob`),
  KEY `ix_contacts_driver_licence_n` (`driver_licence_n`),
  KEY `ix_contacts_full_name` (`full_name`),
  KEY `ix_contacts_money_spent` (`money_spent`),
  KEY `ix_contacts_rented_days` (`rented_days`),
  KEY `ix_contacts_telephone` (`telephone`),
  CONSTRAINT `contacts_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacts`
--

LOCK TABLES `contacts` WRITE;
/*!40000 ALTER TABLE `contacts` DISABLE KEYS */;
INSERT INTO `contacts` VALUES (1,'Giacomo Culcasi',52546325,'21/12/1994','09232758',3,50,4);
/*!40000 ALTER TABLE `contacts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `money` int DEFAULT NULL,
  `bookings_number` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_groups_bookings_number` (`bookings_number`),
  KEY `ix_groups_money` (`money`),
  KEY `ix_groups_name` (`name`),
  KEY `ix_groups_telephone` (`telephone`),
  CONSTRAINT `groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'Baia dei Mulini','7854568',50,1,3);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renewal`
--

DROP TABLE IF EXISTS `renewal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `renewal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `car_id` varchar(8) DEFAULT NULL,
  `renewal_type` varchar(50) DEFAULT NULL,
  `renewal_date` date DEFAULT NULL,
  `renewal_expiry` date DEFAULT NULL,
  `renewal_cost` float DEFAULT NULL,
  `description` varchar(160) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `car_id` (`car_id`),
  CONSTRAINT `renewal_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`plate`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renewal`
--

LOCK TABLES `renewal` WRITE;
/*!40000 ALTER TABLE `renewal` DISABLE KEYS */;
INSERT INTO `renewal` VALUES (1,'SZ654SZ','insurance','2024-03-19','2024-04-06',50,'eheh!!');
/*!40000 ALTER TABLE `renewal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `registration_date` datetime DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `currency` varchar(1) DEFAULT NULL,
  `measurement_unit` varchar(5) DEFAULT NULL,
  `language` varchar(2) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_email` (`email`),
  UNIQUE KEY `ix_user_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'2024-03-15 17:31:36','admin','giacomofculcasi@gmail.com','pbkdf2:sha256:600000$qeQxRVoi034fg0Xo$1eb52f3d33619d8657990cc6da44c16d1b5127dcddd3d39d53417aac0a6c9ede','admin','€','Km','en',1),(3,'2024-03-19 12:40:37','prova','prova@prova.com','pbkdf2:sha256:600000$CFk6WRPrk00SA4rl$76a82ad20dcb86322ba0d379ba54776f92fd2f1b66ce1455bd4829405558e3a8','user','$','km','en',1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-03-19 13:16:09
