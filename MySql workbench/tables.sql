-- ******************************************************
-- * QBMS DATABASE SCHEMA: WITH AUTO_INCREMENT *
-- ******************************************************

-- 1. Create the Database and select it
DROP DATABASE IF EXISTS qbms_project;
CREATE DATABASE qbms_project;
USE qbms_project;

-- 2. Independent Tables

-- Stores subject names and codes
CREATE TABLE Courses (
    CourseID VARCHAR(20) PRIMARY KEY,
    CourseName VARCHAR(100) NOT NULL
);

-- Stores educator/admin details (FacultyID kept as manual INT)
CREATE TABLE Faculty (
    FacultyID INT PRIMARY KEY,
    FacultyName VARCHAR(100) NOT NULL,
    Department VARCHAR(50)
);

-- 3. Dependent Tables (Level 1)

-- Stores Course Learning Outcomes (CLOs)
CREATE TABLE CLOs (
    CLOID INT PRIMARY KEY AUTO_INCREMENT,  -- *** AUTO_INCREMENT ADDED ***
    CLOText TEXT NOT NULL,
    CourseID VARCHAR(20),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

-- Stores metadata about past exam papers
CREATE TABLE PreviousYearPapers (
    PaperID INT PRIMARY KEY AUTO_INCREMENT,
    Year INT NOT NULL,
    Semester INT,
    ExamType ENUM('Quiz', 'MidSem', 'EndSem', 'Auxiliary'),
    CourseID VARCHAR(20),
    FacultyID INT,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID)
);

-- 4. Core Content Table (Level 2)

-- Stores the actual questions
CREATE TABLE Questions (
    QuestionID INT PRIMARY KEY AUTO_INCREMENT,  -- *** AUTO_INCREMENT ADDED ***
    QuestionText TEXT NOT NULL,
    QuestionType ENUM('MCQ', 'Numerical', 'Theory') NOT NULL,
    DifficultyLevel VARCHAR(20),
    Marks DECIMAL(5, 2),
    CLOID INT,
    FOREIGN KEY (CLOID) REFERENCES CLOs(CLOID)
);

-- 5. Final Dependent Tables (Level 3)

-- Stores options for MCQ type questions
CREATE TABLE Options (
    OptionID INT PRIMARY KEY AUTO_INCREMENT,  -- *** AUTO_INCREMENT ADDED ***
    OptionText VARCHAR(255) NOT NULL,
    IsCorrect BOOLEAN NOT NULL,
    QuestionID INT,
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID)
);

-- Junction table for Many-to-Many relationship between Papers and Questions
CREATE TABLE PaperQuestions (
    PaperQuestionID INT PRIMARY KEY AUTO_INCREMENT,  -- *** AUTO_INCREMENT ADDED ***
    PaperID INT,
    QuestionID INT,
    FOREIGN KEY (PaperID) REFERENCES PreviousYearPapers(PaperID),
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID)
);

-- Stores user accounts for application login
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Role ENUM('Faculty', 'Student') NOT NULL
);