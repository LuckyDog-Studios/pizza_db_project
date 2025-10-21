-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: pizza_db
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `CustomerId` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(100) NOT NULL,
  `LastName` varchar(100) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `BirthDate` date DEFAULT NULL,
  `PhoneNumber` varchar(50) DEFAULT NULL,
  `Email` varchar(120) DEFAULT NULL,
  `Street` varchar(200) DEFAULT NULL,
  `HouseNumber` int DEFAULT NULL,
  `City` varchar(100) DEFAULT NULL,
  `PostalCode` varchar(20) DEFAULT NULL,
  `TotalPizzasOrdered` int DEFAULT NULL,
  PRIMARY KEY (`CustomerId`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_person`
--

DROP TABLE IF EXISTS `delivery_person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_person` (
  `DeliveryPersonId` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `IsAvailable` tinyint(1) DEFAULT NULL,
  `UnavailableUntil` datetime DEFAULT NULL,
  PRIMARY KEY (`DeliveryPersonId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_person`
--

LOCK TABLES `delivery_person` WRITE;
/*!40000 ALTER TABLE `delivery_person` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dessert`
--

DROP TABLE IF EXISTS `dessert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dessert` (
  `DessertId` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Price` decimal(10,2) NOT NULL,
  `CreateDate` datetime DEFAULT NULL,
  PRIMARY KEY (`DessertId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dessert`
--

LOCK TABLES `dessert` WRITE;
/*!40000 ALTER TABLE `dessert` DISABLE KEYS */;
/*!40000 ALTER TABLE `dessert` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discount_code`
--

DROP TABLE IF EXISTS `discount_code`;
CREATE TABLE `discount_code` (
  `DiscountCodeId` INT NOT NULL AUTO_INCREMENT,
  `Code` VARCHAR(50) NOT NULL,
  `IsRedeemed` TINYINT(1) DEFAULT 0,
  `ExpiryDate` DATE DEFAULT NULL,
  `DiscountPercent` DECIMAL(5,2) NOT NULL DEFAULT 0,
  `CustomerId` INT DEFAULT NULL,
  PRIMARY KEY (`DiscountCodeId`),
  UNIQUE KEY `Code` (`Code`),
  CONSTRAINT `fk_discount_customer`
    FOREIGN KEY (`CustomerId`) REFERENCES `customer`(`CustomerId`)
    ON DELETE SET NULL
    ON UPDATE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discount_code`
--

LOCK TABLES `discount_code` WRITE;
/*!40000 ALTER TABLE `discount_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `discount_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drink`
--

DROP TABLE IF EXISTS `drink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drink` (
  `DrinkId` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Price` decimal(10,2) NOT NULL,
  `CreateDate` datetime DEFAULT NULL,
  PRIMARY KEY (`DrinkId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drink`
--

LOCK TABLES `drink` WRITE;
/*!40000 ALTER TABLE `drink` DISABLE KEYS */;
/*!40000 ALTER TABLE `drink` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingredient`
--

DROP TABLE IF EXISTS `ingredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredient` (
  `IngredientId` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Price` decimal(10,2) NOT NULL,
  `IsVegetarian` tinyint(1) DEFAULT NULL,
  `IsVegan` tinyint(1) DEFAULT NULL,
  `CreateDate` datetime DEFAULT NULL,
  PRIMARY KEY (`IngredientId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredient`
--

LOCK TABLES `ingredient` WRITE;
/*!40000 ALTER TABLE `ingredient` DISABLE KEYS */;
/*!40000 ALTER TABLE `ingredient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_dessert`
--

DROP TABLE IF EXISTS `order_dessert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_dessert` (
  `OrderId` int NOT NULL,
  `DessertId` int NOT NULL,
  `Amount` int DEFAULT NULL,
  PRIMARY KEY (`OrderId`,`DessertId`),
  KEY `DessertId` (`DessertId`),
  CONSTRAINT `order_dessert_ibfk_1` FOREIGN KEY (`OrderId`) REFERENCES `orders` (`OrderId`),
  CONSTRAINT `order_dessert_ibfk_2` FOREIGN KEY (`DessertId`) REFERENCES `dessert` (`DessertId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_dessert`
--

LOCK TABLES `order_dessert` WRITE;
/*!40000 ALTER TABLE `order_dessert` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_dessert` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_drink`
--

DROP TABLE IF EXISTS `order_drink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_drink` (
  `OrderId` int NOT NULL,
  `DrinkId` int NOT NULL,
  `Amount` int DEFAULT NULL,
  PRIMARY KEY (`OrderId`,`DrinkId`),
  KEY `DrinkId` (`DrinkId`),
  CONSTRAINT `order_drink_ibfk_1` FOREIGN KEY (`OrderId`) REFERENCES `orders` (`OrderId`),
  CONSTRAINT `order_drink_ibfk_2` FOREIGN KEY (`DrinkId`) REFERENCES `drink` (`DrinkId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_drink`
--

LOCK TABLES `order_drink` WRITE;
/*!40000 ALTER TABLE `order_drink` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_drink` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `OrderId` int NOT NULL AUTO_INCREMENT,
  `CustomerId` int NOT NULL,
  `PlaceDateTime` datetime DEFAULT NULL,
  `DeliveryDateTime` datetime DEFAULT NULL,
  `OrderStatus` varchar(50) DEFAULT NULL,
  `DiscountCodeId` int DEFAULT NULL,
  `DeliveryPersonId` int DEFAULT NULL,
  PRIMARY KEY (`OrderId`),
  KEY `CustomerId` (`CustomerId`),
  KEY `DiscountCodeId` (`DiscountCodeId`),
  KEY `DeliveryPersonId` (`DeliveryPersonId`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`CustomerId`) REFERENCES `customer` (`CustomerId`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`DiscountCodeId`) REFERENCES `discount_code` (`DiscountCodeId`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`DeliveryPersonId`) REFERENCES `delivery_person` (`DeliveryPersonId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pizza`
--

DROP TABLE IF EXISTS `pizza`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pizza` (
  `PizzaId` int NOT NULL AUTO_INCREMENT,
  `OrderId` int NOT NULL,
  `Amount` int DEFAULT NULL,
  `Finished` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`PizzaId`),
  KEY `OrderId` (`OrderId`),
  CONSTRAINT `pizza_ibfk_1` FOREIGN KEY (`OrderId`) REFERENCES `orders` (`OrderId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pizza`
--

LOCK TABLES `pizza` WRITE;
/*!40000 ALTER TABLE `pizza` DISABLE KEYS */;
/*!40000 ALTER TABLE `pizza` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pizza_ingredient`
--

DROP TABLE IF EXISTS `pizza_ingredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pizza_ingredient` (
  `PizzaId` int NOT NULL,
  `IngredientId` int NOT NULL,
  PRIMARY KEY (`PizzaId`,`IngredientId`),
  KEY `IngredientId` (`IngredientId`),
  CONSTRAINT `pizza_ingredient_ibfk_1` FOREIGN KEY (`PizzaId`) REFERENCES `pizza` (`PizzaId`),
  CONSTRAINT `pizza_ingredient_ibfk_2` FOREIGN KEY (`IngredientId`) REFERENCES `ingredient` (`IngredientId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pizza_ingredient`
--

LOCK TABLES `pizza_ingredient` WRITE;
/*!40000 ALTER TABLE `pizza_ingredient` DISABLE KEYS */;
/*!40000 ALTER TABLE `pizza_ingredient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postal_assignments`
--

DROP TABLE IF EXISTS `postal_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `postal_assignments` (
  `PostalCode` varchar(20) NOT NULL,
  `DeliveryPersonId` int NOT NULL,
  PRIMARY KEY (`PostalCode`,`DeliveryPersonId`),
  KEY `DeliveryPersonId` (`DeliveryPersonId`),
  CONSTRAINT `postal_assignments_ibfk_1` FOREIGN KEY (`DeliveryPersonId`) REFERENCES `delivery_person` (`DeliveryPersonId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postal_assignments`
--

LOCK TABLES `postal_assignments` WRITE;
/*!40000 ALTER TABLE `postal_assignments` DISABLE KEYS */;
/*!40000 ALTER TABLE `postal_assignments` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-26 18:05:20
