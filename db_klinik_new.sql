-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 09, 2026 at 12:43 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_klinik`
--

-- --------------------------------------------------------

--
-- Table structure for table `akun`
--

CREATE TABLE `akun` (
  `IdAkun` int NOT NULL,
  `Username` varchar(50) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `NamaLengkap` varchar(100) NOT NULL,
  `Jobdesk` enum('Dokter','Perawat','Frontdesk','Kasir','Admin') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `akun`
--

INSERT INTO `akun` (`IdAkun`, `Username`, `Password`, `NamaLengkap`, `Jobdesk`) VALUES
(1, 'dokter1', '123', 'Dr. Budi Santoso', 'Dokter'),
(2, 'dokter2', '123', 'Dr. Siti Nurhaliza', 'Dokter'),
(3, 'perawat1', '123', 'Susanti', 'Perawat'),
(4, 'admin1', '123', 'Rudi Front', 'Frontdesk'),
(5, 'kasir1', '123', 'Dewi Uang', 'Kasir');

-- --------------------------------------------------------

--
-- Table structure for table `barang`
--

CREATE TABLE `barang` (
  `IdBarang` int NOT NULL,
  `IdSupplier` int DEFAULT NULL,
  `NamaBarang` varchar(100) DEFAULT NULL,
  `Stok` int DEFAULT NULL,
  `Satuan` varchar(20) DEFAULT NULL,
  `HargaSatuan` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `barang`
--

INSERT INTO `barang` (`IdBarang`, `IdSupplier`, `NamaBarang`, `Stok`, `Satuan`, `HargaSatuan`) VALUES
(1, 2, 'Paracetamol 90g', 998, 'strip', 10000.00);

-- --------------------------------------------------------

--
-- Table structure for table `master_tindakan`
--

CREATE TABLE `master_tindakan` (
  `IdTindakan` int NOT NULL,
  `NamaTindakan` varchar(100) NOT NULL,
  `Tarif` decimal(15,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `master_tindakan`
--

INSERT INTO `master_tindakan` (`IdTindakan`, `NamaTindakan`, `Tarif`) VALUES
(1, 'Pemeriksaan Umum (Flu/Demam)', 50000.00),
(2, 'Pemeriksaan Gigi Ringan', 100000.00),
(3, 'Bedah Minor / Jahit Luka', 150000.00),
(4, 'Konsultasi Spesialis', 200000.00),
(5, 'Rontgen', 300000.00);

-- --------------------------------------------------------

--
-- Table structure for table `pasien`
--

CREATE TABLE `pasien` (
  `IdPasien` int NOT NULL,
  `Nama` varchar(100) NOT NULL,
  `Alamat` text,
  `Gender` enum('L','P') DEFAULT NULL,
  `Usia` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `pasien`
--

INSERT INTO `pasien` (`IdPasien`, `Nama`, `Alamat`, `Gender`, `Usia`) VALUES
(2, 'Anti', 'Bantul', 'P', 20),
(3, 'Anta', 'Bantul', 'L', 19),
(4, 'Akbar', 'Temanggung', 'L', 90),
(5, 'Dwiki', 'Jakarta', 'L', 20),
(6, 'Duaki', '-', 'L', 0),
(7, 'Andi', 'Jogja', 'L', 19),
(8, 'kamal', 'ciamis', 'L', 100);

-- --------------------------------------------------------

--
-- Table structure for table `pemeriksaanfisik`
--

CREATE TABLE `pemeriksaanfisik` (
  `IdPeriksa` int NOT NULL,
  `NoReg` varchar(20) DEFAULT NULL,
  `IdAkun_Perawat` int DEFAULT NULL,
  `TinggiBadan` decimal(5,2) DEFAULT NULL,
  `BeratBadan` decimal(5,2) DEFAULT NULL,
  `Suhu` decimal(4,2) DEFAULT NULL,
  `Tensi` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `pemeriksaanfisik`
--

INSERT INTO `pemeriksaanfisik` (`IdPeriksa`, `NoReg`, `IdAkun_Perawat`, `TinggiBadan`, `BeratBadan`, `Suhu`, `Tensi`) VALUES
(1, 'REG-20260103-001', 2, 110.00, 12.00, 40.00, '120/100'),
(2, 'REG-20260103-002', 3, 180.00, 70.00, 40.00, '110/60'),
(3, 'REG-20260105-001', 3, 190.00, 75.00, 40.00, '90/90'),
(4, 'REG-20260103-004', 3, 170.00, 56.00, 20.00, '120/80'),
(5, 'REG-20260103-003', 3, 190.00, 80.00, 90.00, '80/80'),
(6, 'REG-20260106-004', 3, 180.00, 80.00, 60.00, '100/70');

-- --------------------------------------------------------

--
-- Table structure for table `pendaftaran`
--

CREATE TABLE `pendaftaran` (
  `NoReg` varchar(20) NOT NULL,
  `IdPasien` int DEFAULT NULL,
  `IdAkun_Frontdesk` int DEFAULT NULL,
  `IdAkun_Dokter` int DEFAULT NULL,
  `TanggalDanWaktu` datetime DEFAULT CURRENT_TIMESTAMP,
  `Status` enum('Menunggu','Diperiksa','Selesai','Batal') DEFAULT 'Menunggu'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `pendaftaran`
--

INSERT INTO `pendaftaran` (`NoReg`, `IdPasien`, `IdAkun_Frontdesk`, `IdAkun_Dokter`, `TanggalDanWaktu`, `Status`) VALUES
('REG-20260103-001', 2, 3, 2, '2026-01-03 18:21:37', 'Selesai'),
('REG-20260103-002', 2, 3, 2, '2026-01-03 18:33:16', 'Selesai'),
('REG-20260103-003', 3, 4, 2, '2026-01-03 18:47:47', 'Diperiksa'),
('REG-20260103-004', 3, 4, 2, '2026-01-03 19:21:05', 'Selesai'),
('REG-20260103-005', 4, 4, 1, '2026-01-03 19:29:12', 'Selesai'),
('REG-20260105-001', 5, 4, 2, '2026-01-05 15:58:34', 'Selesai'),
('REG-20260105-002', 7, 4, 2, '2026-01-05 19:48:48', 'Selesai'),
('REG-20260106-001', 8, 4, 2, '2026-01-06 22:03:32', 'Selesai'),
('REG-20260106-002', 7, 4, 2, '2026-01-06 22:03:37', 'Menunggu'),
('REG-20260106-003', 4, 4, 2, '2026-01-06 22:03:45', 'Selesai'),
('REG-20260106-004', 4, 4, 1, '2026-01-06 22:34:33', 'Diperiksa'),
('REG-20260106-005', 4, 4, 2, '2026-01-06 22:39:10', 'Selesai'),
('REG-20260109-001', 8, 4, 1, '2026-01-09 07:39:11', 'Menunggu');

-- --------------------------------------------------------

--
-- Table structure for table `rekammedis`
--

CREATE TABLE `rekammedis` (
  `IdRek` int NOT NULL,
  `NoReg` varchar(20) DEFAULT NULL,
  `Diagnosa` varchar(100) DEFAULT NULL,
  `CatatanDokter` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `rekammedis`
--

INSERT INTO `rekammedis` (`IdRek`, `NoReg`, `Diagnosa`, `CatatanDokter`) VALUES
(1, 'REG-20260103-001', 'Pemeriksaan Umum (Flu/Demam)', 'Resep Diberikan'),
(2, 'REG-20260103-002', 'Pemeriksaan Umum (Flu/Demam). bro ini kebanyakan scroll ig', 'Resep Diberikan'),
(3, 'REG-20260105-001', 'Pemeriksaan Umum (Flu/Demam). ', 'Resep Diberikan'),
(4, 'REG-20260103-005', 'Bedah Minor / Jahit Luka. instalasi pen', 'Resep Diberikan'),
(5, 'REG-20260105-002', 'Bro hampir saja meninggal', 'Resep Diberikan'),
(7, 'REG-20260103-004', 'Mengalami gejala hipotermia', 'Resep Diberikan'),
(8, 'REG-20260106-003', 'kebanyakan ngelem (Tindakan: Konsultasi Spesialis)', 'Resep Diberikan'),
(9, 'REG-20260106-001', 'up syndrome  (Tindakan: Konsultasi Spesialis)', 'Resep Diberikan'),
(10, 'REG-20260106-005', 'kebanyakan main hp (Tindakan: Rontgen)', 'Resep Diberikan');

-- --------------------------------------------------------

--
-- Table structure for table `resepobat`
--

CREATE TABLE `resepobat` (
  `IdResep` int NOT NULL,
  `IdRek` int DEFAULT NULL,
  `IdBarang` int DEFAULT NULL,
  `Jumlah` int DEFAULT NULL,
  `SubTotalHarga` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `resepobat`
--

INSERT INTO `resepobat` (`IdResep`, `IdRek`, `IdBarang`, `Jumlah`, `SubTotalHarga`) VALUES
(1, 10, 1, 1, 10000.00),
(2, 10, 1, 1, 10000.00);

-- --------------------------------------------------------

--
-- Table structure for table `supplier`
--

CREATE TABLE `supplier` (
  `IdSupplier` int NOT NULL,
  `NamaSupplier` varchar(100) NOT NULL,
  `Alamat` text,
  `NoTelepon` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `supplier`
--

INSERT INTO `supplier` (`IdSupplier`, `NamaSupplier`, `Alamat`, `NoTelepon`) VALUES
(1, 'Umbrella Corporation', '-', '999'),
(2, 'PT. ViccoBat', 'Nganjuk', '110');

-- --------------------------------------------------------

--
-- Table structure for table `tagihan`
--

CREATE TABLE `tagihan` (
  `NoTagihan` varchar(20) NOT NULL,
  `NoReg` varchar(20) DEFAULT NULL,
  `TotalBiayaTindakan` decimal(15,2) DEFAULT NULL,
  `TotalBiayaObat` decimal(15,2) DEFAULT NULL,
  `GrandTotal` decimal(15,2) DEFAULT NULL,
  `StatusBayar` enum('Lunas','Pending') DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tagihan`
--

INSERT INTO `tagihan` (`NoTagihan`, `NoReg`, `TotalBiayaTindakan`, `TotalBiayaObat`, `GrandTotal`, `StatusBayar`) VALUES
('INV-REG-20260103-001', 'REG-20260103-001', 50000.00, 72000.00, 122000.00, 'Lunas'),
('INV-REG-20260103-002', 'REG-20260103-002', 50000.00, 50000.00, 100000.00, 'Lunas'),
('INV-REG-20260103-004', 'REG-20260103-004', 50000.00, 32000.00, 82000.00, 'Lunas'),
('INV-REG-20260103-005', 'REG-20260103-005', 150000.00, 0.00, 150000.00, 'Lunas'),
('INV-REG-20260105-001', 'REG-20260105-001', 50000.00, 120000.00, 170000.00, 'Lunas'),
('INV-REG-20260105-002', 'REG-20260105-002', 50000.00, 15000.00, 65000.00, 'Lunas'),
('INV-REG-20260106-001', 'REG-20260106-001', 200000.00, 60000.00, 260000.00, 'Lunas'),
('INV-REG-20260106-003', 'REG-20260106-003', 200000.00, 17000.00, 217000.00, 'Lunas'),
('INV-REG-20260106-005', 'REG-20260106-005', 300000.00, 20000.00, 320000.00, 'Lunas');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `akun`
--
ALTER TABLE `akun`
  ADD PRIMARY KEY (`IdAkun`),
  ADD UNIQUE KEY `Username` (`Username`);

--
-- Indexes for table `barang`
--
ALTER TABLE `barang`
  ADD PRIMARY KEY (`IdBarang`),
  ADD KEY `IdSupplier` (`IdSupplier`);

--
-- Indexes for table `master_tindakan`
--
ALTER TABLE `master_tindakan`
  ADD PRIMARY KEY (`IdTindakan`);

--
-- Indexes for table `pasien`
--
ALTER TABLE `pasien`
  ADD PRIMARY KEY (`IdPasien`);

--
-- Indexes for table `pemeriksaanfisik`
--
ALTER TABLE `pemeriksaanfisik`
  ADD PRIMARY KEY (`IdPeriksa`),
  ADD KEY `NoReg` (`NoReg`);

--
-- Indexes for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  ADD PRIMARY KEY (`NoReg`),
  ADD KEY `IdPasien` (`IdPasien`),
  ADD KEY `IdAkun_Dokter` (`IdAkun_Dokter`);

--
-- Indexes for table `rekammedis`
--
ALTER TABLE `rekammedis`
  ADD PRIMARY KEY (`IdRek`),
  ADD KEY `NoReg` (`NoReg`);

--
-- Indexes for table `resepobat`
--
ALTER TABLE `resepobat`
  ADD PRIMARY KEY (`IdResep`),
  ADD KEY `IdRek` (`IdRek`),
  ADD KEY `IdBarang` (`IdBarang`);

--
-- Indexes for table `supplier`
--
ALTER TABLE `supplier`
  ADD PRIMARY KEY (`IdSupplier`);

--
-- Indexes for table `tagihan`
--
ALTER TABLE `tagihan`
  ADD PRIMARY KEY (`NoTagihan`),
  ADD KEY `NoReg` (`NoReg`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `akun`
--
ALTER TABLE `akun`
  MODIFY `IdAkun` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `barang`
--
ALTER TABLE `barang`
  MODIFY `IdBarang` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `master_tindakan`
--
ALTER TABLE `master_tindakan`
  MODIFY `IdTindakan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `pasien`
--
ALTER TABLE `pasien`
  MODIFY `IdPasien` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `pemeriksaanfisik`
--
ALTER TABLE `pemeriksaanfisik`
  MODIFY `IdPeriksa` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `rekammedis`
--
ALTER TABLE `rekammedis`
  MODIFY `IdRek` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `resepobat`
--
ALTER TABLE `resepobat`
  MODIFY `IdResep` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `supplier`
--
ALTER TABLE `supplier`
  MODIFY `IdSupplier` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `barang`
--
ALTER TABLE `barang`
  ADD CONSTRAINT `barang_ibfk_1` FOREIGN KEY (`IdSupplier`) REFERENCES `supplier` (`IdSupplier`) ON DELETE RESTRICT;

--
-- Constraints for table `pemeriksaanfisik`
--
ALTER TABLE `pemeriksaanfisik`
  ADD CONSTRAINT `pemeriksaanfisik_ibfk_1` FOREIGN KEY (`NoReg`) REFERENCES `pendaftaran` (`NoReg`);

--
-- Constraints for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  ADD CONSTRAINT `pendaftaran_ibfk_1` FOREIGN KEY (`IdPasien`) REFERENCES `pasien` (`IdPasien`),
  ADD CONSTRAINT `pendaftaran_ibfk_3` FOREIGN KEY (`IdAkun_Dokter`) REFERENCES `akun` (`IdAkun`);

--
-- Constraints for table `rekammedis`
--
ALTER TABLE `rekammedis`
  ADD CONSTRAINT `rekammedis_ibfk_1` FOREIGN KEY (`NoReg`) REFERENCES `pendaftaran` (`NoReg`);

--
-- Constraints for table `resepobat`
--
ALTER TABLE `resepobat`
  ADD CONSTRAINT `resepobat_ibfk_1` FOREIGN KEY (`IdRek`) REFERENCES `rekammedis` (`IdRek`),
  ADD CONSTRAINT `resepobat_ibfk_2` FOREIGN KEY (`IdBarang`) REFERENCES `barang` (`IdBarang`);

--
-- Constraints for table `tagihan`
--
ALTER TABLE `tagihan`
  ADD CONSTRAINT `tagihan_ibfk_1` FOREIGN KEY (`NoReg`) REFERENCES `pendaftaran` (`NoReg`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
