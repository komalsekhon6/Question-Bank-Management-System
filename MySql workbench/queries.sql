-- Select the database
USE qbms_project;

-- --------------------------------------------------
-- 1. Insert Sample Users
-- (Required for initial login - DO NOT USE ENCRYPTED PASSWORDS YET)
-- --------------------------------------------------
INSERT INTO Users (Username, Password, Role) VALUES
('komal', 'pass123', 'Faculty'),
('gurpreet', 'pass456', 'Student'),
('rupinder', 'secure789', 'Faculty');


-- --------------------------------------------------
-- 2. Insert Sample Faculty
-- (Used by the "Set by" filter)
-- --------------------------------------------------
INSERT INTO Faculty (FacultyID, FacultyName, Department) VALUES
(101, 'Dr. Sarah Smith', 'CSE'),
(102, 'Mr. John Jones', 'ECE'),
(103, 'Prof. Ritu Sharma', 'MATH');


-- --------------------------------------------------
-- 3. Insert Sample Courses (Alphanumeric CourseIDs)
-- (Required for search functionality)
-- --------------------------------------------------
INSERT INTO Courses (CourseID, CourseName) VALUES
('ULC501', 'Database Management Systems'),
('UCS501', 'Operating Systems'),
('UMA001', 'Calculus');


-- --------------------------------------------------
-- 4. Insert Sample CLOs (Linked to Courses)
-- (Required for question filtering)
-- --------------------------------------------------
INSERT INTO CLOs (CLOID, CLOText, CourseID) VALUES
(1001, 'CLO1: Understand relational database models.', 'ULC501'),
(1002, 'CLO2: Design and implement SQL queries.', 'ULC501'),
(2001, 'CLO1: Explain process synchronization.', 'UCS501');


-- --------------------------------------------------
-- 5. Insert Sample Previous Year Papers
-- (Uses the required MidSem, EndSem, Auxiliary ExamTypes)
-- --------------------------------------------------
INSERT INTO PreviousYearPapers (PaperID, Year, Semester, ExamType, CourseID, FacultyID) VALUES
(1, 2023, 1, 'MidSem', 'ULC501', 101),       -- Smith's MidSem DBMS paper
(2, 2022, 2, 'EndSem', 'ULC501', 102),       -- Jones's EndSem DBMS paper
(3, 2023, 1, 'Auxiliary', 'UCS501', 101),    -- Smith's Auxiliary OS paper
(4, 2024, 1, 'MidSem', 'UMA001', 103);       -- Sharma's MidSem Calculus paper


-- --------------------------------------------------
-- 6. Insert Sample Questions (Linked to CLOs)
-- (Core data for paper content)
-- --------------------------------------------------
INSERT INTO Questions (QuestionID, QuestionText, QuestionType, DifficultyLevel, Marks, CLOID) VALUES
(101, 'Explain the difference between 3NF and BCNF.', 'Theory', 'Hard', 10.00, 1001),
(102, 'Write an SQL query to find the names of students older than 20.', 'Numerical', 'Medium', 5.00, 1002),
(103, 'Which of the following is a non-preemptive scheduling algorithm?', 'MCQ', 'Easy', 2.00, 2001),
(104, 'Define a foreign key and its purpose.', 'Theory', 'Easy', 5.00, 1001);


-- --------------------------------------------------
-- 7. Insert Sample Options (for MCQ questions)
-- --------------------------------------------------
INSERT INTO Options (OptionID, OptionText, IsCorrect, QuestionID) VALUES
(1, 'Round Robin', FALSE, 103),
(2, 'FCFS', TRUE, 103),
(3, 'Preemptive SJF', FALSE, 103),
(4, 'Priority Scheduling', FALSE, 103);


-- --------------------------------------------------
-- 8. Link Questions to Papers (PaperQuestions)
-- (This is how the PYQ viewer knows what questions belong to what paper)
-- --------------------------------------------------
INSERT INTO PaperQuestions (PaperQuestionID, PaperID, QuestionID) VALUES
-- Paper 1 (DBMS MidSem 2023)
(1, 1, 101),
(2, 1, 102),

-- Paper 2 (DBMS EndSem 2022)
(3, 2, 104),
(4, 2, 102),

-- Paper 3 (OS Auxiliary 2023)
(5, 3, 103);


SELECT 'Sample data insertion complete.' AS Status;