-- MySQL dump 10.17  Distrib 10.3.22-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: library
-- ------------------------------------------------------
-- Server version	10.3.22-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Book`
--

DROP TABLE IF EXISTS `Book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Book` (
  `BookID` int(11) NOT NULL AUTO_INCREMENT,
  `Author` varchar(255) DEFAULT NULL,
  `Nation` varchar(255) DEFAULT NULL,
  `Category` varchar(255) DEFAULT NULL,
  `Quantity` int(11) DEFAULT NULL,
  `Title` varchar(255) NOT NULL DEFAULT 'Unknown',
  PRIMARY KEY (`BookID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Book`
--

LOCK TABLES `Book` WRITE;
/*!40000 ALTER TABLE `Book` DISABLE KEYS */;
INSERT INTO `Book` VALUES (1,'Harper Lee','United States','Fiction',3,'To Kill a Mockingbird'),(2,'George Orwell','United Kingdom','Dystopian',1,'1984'),(3,'Jane Austen','United Kingdom','Classic',0,'Pride and Prejudice'),(4,'F. Scott Fitzgerald','United States','Classic',0,'The Great Gatsby'),(5,'Gabriel García Márquez','Colombia','Magical Realism',0,'One Hundred Years of Solitude');
/*!40000 ALTER TABLE `Book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BookHistory`
--

DROP TABLE IF EXISTS `BookHistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `BookHistory` (
  `BookHistoryID` int(11) NOT NULL AUTO_INCREMENT,
  `BorrowDate` datetime DEFAULT NULL,
  `ReturnDate` datetime DEFAULT NULL,
  `PenaltyTotal` decimal(10,2) DEFAULT NULL,
  `PenaltyPaid` tinyint(1) DEFAULT NULL,
  `CopyID` int(11) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL,
  PRIMARY KEY (`BookHistoryID`),
  KEY `CopyID` (`CopyID`),
  KEY `UserID` (`UserID`),
  CONSTRAINT `BookHistory_ibfk_1` FOREIGN KEY (`CopyID`) REFERENCES `Copy` (`CopyID`),
  CONSTRAINT `BookHistory_ibfk_2` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BookHistory`
--

LOCK TABLES `BookHistory` WRITE;
/*!40000 ALTER TABLE `BookHistory` DISABLE KEYS */;
INSERT INTO `BookHistory` VALUES (1,'2024-01-10 00:00:00','2024-02-10 00:00:00',0.00,0,1,9),(2,'2024-02-15 00:00:00','2024-03-15 00:00:00',0.00,0,2,10),(3,'2024-03-20 00:00:00',NULL,0.00,0,3,9),(4,'2024-04-10 00:00:00',NULL,0.00,0,4,10),(5,'2024-04-15 00:00:00',NULL,0.00,0,5,9),(9,'2024-04-19 01:54:05','2024-04-19 01:54:49',NULL,NULL,6,10),(10,'2024-04-19 04:36:13','2024-04-19 04:36:57',NULL,NULL,7,9),(11,'2024-04-19 07:06:12','2024-04-19 07:06:39',NULL,NULL,1,10);
/*!40000 ALTER TABLE `BookHistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Copy`
--

DROP TABLE IF EXISTS `Copy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Copy` (
  `CopyID` int(11) NOT NULL AUTO_INCREMENT,
  `BoughtTime` datetime DEFAULT NULL,
  `Status` varchar(255) DEFAULT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `BorrowDate` datetime DEFAULT NULL,
  `Penalty` decimal(10,2) DEFAULT NULL,
  `BookID` int(11) DEFAULT NULL,
  `ShelfID` int(11) DEFAULT NULL,
  PRIMARY KEY (`CopyID`),
  KEY `BookID` (`BookID`),
  KEY `ShelfID` (`ShelfID`),
  CONSTRAINT `Copy_ibfk_1` FOREIGN KEY (`BookID`) REFERENCES `Book` (`BookID`),
  CONSTRAINT `Copy_ibfk_2` FOREIGN KEY (`ShelfID`) REFERENCES `Shelf` (`ShelfID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Copy`
--

LOCK TABLES `Copy` WRITE;
/*!40000 ALTER TABLE `Copy` DISABLE KEYS */;
INSERT INTO `Copy` VALUES (1,'2024-04-17 06:11:23','Available',29.99,NULL,0.00,1,1),(2,'2024-04-17 06:11:23','Available',19.99,NULL,0.00,2,2),(3,'2024-04-17 06:11:23','Borrowed',15.99,'2024-01-10 00:00:00',0.00,3,3),(4,'2024-04-17 06:11:23','Borrowed',25.99,'2024-02-15 00:00:00',0.00,4,4),(5,'2024-04-17 06:11:23','Borrowed',9.99,'2024-03-20 00:00:00',0.00,5,5),(6,NULL,'Available',29.90,NULL,0.00,1,1),(7,NULL,'Available',29.90,NULL,0.00,1,1);
/*!40000 ALTER TABLE `Copy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Event`
--

DROP TABLE IF EXISTS `Event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Event` (
  `EventID` int(11) NOT NULL AUTO_INCREMENT,
  `EventName` varchar(255) DEFAULT NULL,
  `DateAndTime` datetime DEFAULT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `Host` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`EventID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Event`
--

LOCK TABLES `Event` WRITE;
/*!40000 ALTER TABLE `Event` DISABLE KEYS */;
INSERT INTO `Event` VALUES (1,'Lecture A','2024-05-15 18:00:00','First Floor Hall 1','Lecture A description','Emily'),(2,'Lecture B','2024-06-12 16:30:00','First Floor Hall 2','Lecture B description','John'),(3,'Lecture C','2024-07-09 10:00:00','Second Floor Hall 1','Lecture C description','Lily');
/*!40000 ALTER TABLE `Event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EventParticipate`
--

DROP TABLE IF EXISTS `EventParticipate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `EventParticipate` (
  `EventID` int(11) NOT NULL,
  `UserID` int(11) NOT NULL,
  PRIMARY KEY (`EventID`,`UserID`),
  KEY `UserID` (`UserID`),
  CONSTRAINT `EventParticipate_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`),
  CONSTRAINT `EventParticipate_ibfk_2` FOREIGN KEY (`EventID`) REFERENCES `Event` (`EventID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EventParticipate`
--

LOCK TABLES `EventParticipate` WRITE;
/*!40000 ALTER TABLE `EventParticipate` DISABLE KEYS */;
INSERT INTO `EventParticipate` VALUES (1,9),(1,10),(1,11),(2,10),(3,2),(3,4),(3,6),(3,9);
/*!40000 ALTER TABLE `EventParticipate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RoomReservation`
--

DROP TABLE IF EXISTS `RoomReservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RoomReservation` (
  `RoomReservationID` int(11) NOT NULL AUTO_INCREMENT,
  `ReserveDate` date DEFAULT NULL,
  `ReserveTimeStart` time DEFAULT NULL,
  `ReserveTimeEnd` time DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL,
  `StudyRoomID` int(11) DEFAULT NULL,
  PRIMARY KEY (`RoomReservationID`),
  KEY `UserID` (`UserID`),
  KEY `StudyRoomID` (`StudyRoomID`),
  CONSTRAINT `RoomReservation_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`),
  CONSTRAINT `RoomReservation_ibfk_2` FOREIGN KEY (`StudyRoomID`) REFERENCES `StudyRoom` (`StudyRoomID`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RoomReservation`
--

LOCK TABLES `RoomReservation` WRITE;
/*!40000 ALTER TABLE `RoomReservation` DISABLE KEYS */;
INSERT INTO `RoomReservation` VALUES (9,'2024-04-20','10:00:00','10:30:00',10,1),(10,'2024-04-20','14:00:00','14:30:00',10,1),(11,'2024-04-19','11:30:00','12:00:00',10,1),(12,'2024-04-21','08:00:00','08:30:00',11,3);
/*!40000 ALTER TABLE `RoomReservation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Shelf`
--

DROP TABLE IF EXISTS `Shelf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Shelf` (
  `ShelfID` int(11) NOT NULL AUTO_INCREMENT,
  `Floor` int(11) DEFAULT NULL,
  `Row` int(11) DEFAULT NULL,
  `Shelf` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ShelfID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Shelf`
--

LOCK TABLES `Shelf` WRITE;
/*!40000 ALTER TABLE `Shelf` DISABLE KEYS */;
INSERT INTO `Shelf` VALUES (1,1,1,'A'),(2,1,2,'B'),(3,2,1,'C'),(4,2,2,'D'),(5,3,1,'E');
/*!40000 ALTER TABLE `Shelf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Staff`
--

DROP TABLE IF EXISTS `Staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Staff` (
  `UserID` int(11) NOT NULL,
  `EmployeeStartTime` datetime DEFAULT NULL,
  `EmployeeEndTime` datetime DEFAULT NULL,
  `JobTitle` varchar(255) DEFAULT NULL,
  `Salary` decimal(10,2) DEFAULT NULL,
  `Responsibility` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  CONSTRAINT `Staff_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Staff`
--

LOCK TABLES `Staff` WRITE;
/*!40000 ALTER TABLE `Staff` DISABLE KEYS */;
INSERT INTO `Staff` VALUES (7,'2024-04-15 23:53:06',NULL,'librarian',20.00,'Organize books and events'),(8,'2024-04-15 23:56:25',NULL,'librarian',15.00,'Organize books'),(10,'2024-04-16 17:27:54',NULL,'librarian',20.00,'Organize books and events'),(11,'2024-04-19 04:34:51',NULL,'librarian',15.00,'Organize books');
/*!40000 ALTER TABLE `Staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `StudyRoom`
--

DROP TABLE IF EXISTS `StudyRoom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `StudyRoom` (
  `StudyRoomID` int(11) NOT NULL AUTO_INCREMENT,
  `RoomNumber` int(11) DEFAULT NULL,
  `ChairNumber` int(11) DEFAULT NULL,
  `MaxUser` int(11) DEFAULT NULL,
  `Equipment` text DEFAULT NULL,
  PRIMARY KEY (`StudyRoomID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `StudyRoom`
--

LOCK TABLES `StudyRoom` WRITE;
/*!40000 ALTER TABLE `StudyRoom` DISABLE KEYS */;
INSERT INTO `StudyRoom` VALUES (1,1,10,20,'Whiteboard'),(2,2,12,24,'Monitor, Speaker System'),(3,3,8,16,'High-speed Internet, Conference Phone');
/*!40000 ALTER TABLE `StudyRoom` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `User` (
  `UserID` int(11) NOT NULL AUTO_INCREMENT,
  `Username` varchar(255) NOT NULL,
  `SSN` varchar(255) DEFAULT NULL,
  `Email` varchar(255) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `Balance` decimal(10,2) DEFAULT NULL,
  `RegisterTime` datetime DEFAULT current_timestamp(),
  `BooksLimit` int(11) DEFAULT NULL,
  `StudyRoomLimit` int(11) DEFAULT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `User`
--

LOCK TABLES `User` WRITE;
/*!40000 ALTER TABLE `User` DISABLE KEYS */;
INSERT INTO `User` VALUES (1,'john_doe','123456789','john.doe@example.com','Hashed_password1',100.00,'2021-01-01 08:00:00',5,2),(2,'jane_smith','987654321','jane.smith@example.com','Hashed_password2',150.00,'2021-02-01 09:00:00',3,3),(3,'jim_bean','123557890','jim.bean@example.com','Hashed_password3',200.00,'2021-03-01 10:00:00',4,1),(4,'jessica_jones','789456123','jessica.jones@example.com','Hashed_password4',250.00,'2021-04-01 11:00:00',6,0),(5,'jack_reacher','456751234','jack.reacher@example.com','Hashed_password5',300.00,'2021-05-01 12:00:00',2,5),(6,'Chloe','111222333','qwe@123','50e8a6173d5ba81ab467cca7184867e6e0af70bb2f02e06299d845f6d6fed585',50.00,'2024-04-07 23:13:39',5,5),(7,'emma','444555666','emma@123.com','8f7b804aad20b88701c182f741a9fd485badfac8b45c9a9e22fe2e46adddcce1',50.00,'2024-04-15 23:53:06',10,5),(8,'grace','777888999','grace@123.com','67b0e2f202d4f90a6f23d1bdbd969b205aa7d595ec19c73a792e26e09145fff9',50.00,'2024-04-15 23:56:25',10,5),(9,'luke','222333444','luke@123.com','d1fdc211f5414e6974317921f57c89e9a7c41def55d3fc7befa436efb8ac7c04',50.00,'2024-04-16 17:26:22',10,5),(10,'leo','333444555','leo@123.com','a2b716ccad2b584fbc99265955016582e4e1c0bbb5f9f01099fb322a478dfe0e',50.00,'2024-04-16 17:27:54',10,5),(11,'nova','333222111','nova@123.com','5ba6e380f1745566cf56aac44dfcdd1aec10eb92fb2dcc33bf98f15ef3ed83b9',50.00,'2024-04-19 04:34:51',10,5);
/*!40000 ALTER TABLE `User` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-19 12:02:32
