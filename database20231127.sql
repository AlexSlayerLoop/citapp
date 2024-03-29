-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: citapp2
-- ------------------------------------------------------
-- Server version	8.0.33

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
-- Table structure for table `alergia`
--

DROP TABLE IF EXISTS `alergia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alergia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int NOT NULL,
  `nombre_alergia` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `alergia_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cita`
--

DROP TABLE IF EXISTS `cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cita` (
  `id_doctor` varchar(10) NOT NULL,
  `id_paciente` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `cita_confirmada` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_doctor`,`id_paciente`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`id_doctor`) REFERENCES `doctor` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor` (
  `id` varchar(10) NOT NULL DEFAULT (concat(_utf8mb4'doc_',cast(floor((rand() * 10000)) as char charset utf8mb4))),
  `nombre` varchar(100) NOT NULL,
  `cedula` varchar(15) NOT NULL,
  `telefono` char(15) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `correo` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cedula` (`cedula`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `enfermedades_cronicas`
--

DROP TABLE IF EXISTS `enfermedades_cronicas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enfermedades_cronicas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int NOT NULL,
  `nombre_enfermedad` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `enfermedades_cronicas_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `estudios_medicos`
--

DROP TABLE IF EXISTS `estudios_medicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estudios_medicos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int NOT NULL,
  `nombre_estudio` varchar(255) DEFAULT NULL,
  `url_estudio` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `estudios_medicos_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_usuario` varchar(10) NOT NULL,
  `comentario` varchar(2000) DEFAULT NULL,
  `evaluacion` decimal(2,1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_rango_evaluacion` CHECK (((`evaluacion` >= 0.0) and (`evaluacion` <= 5.0)))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historial_cirugias`
--

DROP TABLE IF EXISTS `historial_cirugias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_cirugias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int NOT NULL,
  `nombre_cirugia` varchar(255) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `historial_cirugias_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historial_cita`
--

DROP TABLE IF EXISTS `historial_cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_cita` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_doctor` varchar(10) NOT NULL,
  `id_paciente` int NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_doctor` (`id_doctor`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `historial_cita_ibfk_1` FOREIGN KEY (`id_doctor`) REFERENCES `doctor` (`id`) ON DELETE CASCADE,
  CONSTRAINT `historial_cita_ibfk_2` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `horario`
--

DROP TABLE IF EXISTS `horario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `horario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_doctor` varchar(10) NOT NULL,
  `hora_entrada` time NOT NULL,
  `hora_salida` time NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_doctor` (`id_doctor`),
  CONSTRAINT `horario_ibfk_1` FOREIGN KEY (`id_doctor`) REFERENCES `doctor` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `medicamentos_actuales`
--

DROP TABLE IF EXISTS `medicamentos_actuales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicamentos_actuales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int NOT NULL,
  `nombre_medicamento` varchar(255) DEFAULT NULL,
  `duracion_tratamiento` int DEFAULT NULL,
  `frecuencia` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `medicamentos_actuales_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `medicamentos_receta`
--

DROP TABLE IF EXISTS `medicamentos_receta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicamentos_receta` (
  `id_receta_medica` int NOT NULL,
  `id_medicamento` int NOT NULL,
  KEY `id_receta_medica` (`id_receta_medica`),
  KEY `id_medicamento` (`id_medicamento`),
  CONSTRAINT `medicamentos_receta_ibfk_1` FOREIGN KEY (`id_receta_medica`) REFERENCES `receta_medica` (`id`),
  CONSTRAINT `medicamentos_receta_ibfk_2` FOREIGN KEY (`id_medicamento`) REFERENCES `medicamentos_actuales` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paciente`
--

DROP TABLE IF EXISTS `paciente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paciente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_usuario` varchar(10) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` enum('H','M') NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `peso_kg` decimal(5,2) NOT NULL,
  `estatura_mts` decimal(3,2) DEFAULT NULL,
  `relacion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `paciente_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `receta_medica`
--

DROP TABLE IF EXISTS `receta_medica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta_medica` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_paciente` int NOT NULL,
  `id_doctor` varchar(10) NOT NULL,
  `fecha` date DEFAULT (curdate()),
  `temperatura` decimal(3,1) DEFAULT NULL,
  `presion_arterial` varchar(20) DEFAULT NULL,
  `diagnostico` varchar(255) DEFAULT NULL,
  `indicaciones_generales` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_paciente` (`id_paciente`),
  KEY `id_doctor` (`id_doctor`),
  CONSTRAINT `receta_medica_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id`),
  CONSTRAINT `receta_medica_ibfk_2` FOREIGN KEY (`id_doctor`) REFERENCES `doctor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `secretaria`
--

DROP TABLE IF EXISTS `secretaria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `secretaria` (
  `id` varchar(10) NOT NULL DEFAULT (concat(_utf8mb4'scr_',cast(floor((rand() * 10000)) as char charset utf8mb4))),
  `id_doctor` varchar(10) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`),
  KEY `id_doctor` (`id_doctor`),
  CONSTRAINT `secretaria_ibfk_1` FOREIGN KEY (`id_doctor`) REFERENCES `doctor` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` varchar(10) NOT NULL DEFAULT (concat(_utf8mb4'usr_',cast(floor((rand() * 10000)) as char charset utf8mb4))),
  `nombre` varchar(255) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `password` char(94) NOT NULL,
  `telefono` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-11-27 14:51:23
