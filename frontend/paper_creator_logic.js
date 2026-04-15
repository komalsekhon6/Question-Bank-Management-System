// Assume this file is named 'paper_creator_logic.js' or similar.

// --- CONFIGURATION ---
const API_BASE_URL = 'http://127.0.0.1:5000/api';
let currentPaperId = null; // Global variable to hold the ID of the paper currently being edited.

// --- INITIAL SETUP (Load dropdowns) ---
document.addEventListener('DOMContentLoaded', () => {
    // Check if we are editing an existing paper (e.g., loaded from a query parameter)
    currentPaperId = getPaperIdFromUrl();
    if (currentPaperId) {
        console.log(`Editing existing Paper ID: ${currentPaperId}`);
        // TODO: A function here to load existing paper metadata and questions.
    }
    
    // Load dropdowns when the page starts
    loadCoursesDropdown();
    loadFacultyDropdown();
});

// --- HELPER FUNCTIONS ---
function getPaperIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('paperId');
}

// Function to load Course dropdown options
async function loadCoursesDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/courses`);
        const courses = await response.json();
        const select = document.getElementById('course-id');
        select.innerHTML = '<option value="">Select Course</option>'; // Default option
        courses.forEach(course => {
            select.innerHTML += `<option value="${course.CourseID}">${course.CourseName} (${course.CourseID})</option>`;
        });
    } catch (e) {
        console.error("Failed to load courses:", e);
    }
}

// Function to load Faculty dropdown options
async function loadFacultyDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/faculty`);
        const facultyList = await response.json();
        const select = document.getElementById('faculty-id');
        select.innerHTML = '<option value="">Set By Faculty</option>'; // Default option
        facultyList.forEach(faculty => {
            select.innerHTML += `<option value="${faculty.FacultyID}">${faculty.FacultyName}</option>`;
        });
    } catch (e) {
        console.error("Failed to load faculty:", e);
    }
}


// --- API ROUTE 11: CREATE NEW PAPER METADATA ---
async function createPaper() {
    // 1. Collect form data
    const paperData = {
        CourseID: document.getElementById('course-id').value,
        Year: document.getElementById('year').value,
        Semester: document.getElementById('semester').value,
        ExamType: document.getElementById('exam-type').value,
        FacultyID: document.getElementById('faculty-id').value,
    };

    // 2. Simple validation
    if (!paperData.CourseID || !paperData.Year || !paperData.ExamType || !paperData.FacultyID) {
        alert("Please fill in Course, Year, Exam Type, and Faculty fields.");
        return;
    }

    // Disable the button to prevent double-submission
    const createButton = document.getElementById('create-paper-btn');
    createButton.disabled = true;

    // 3. Send POST request to the API
    try {
        const response = await fetch(`${API_BASE_URL}/papers/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(paperData)
        });

        const result = await response.json();

        if (response.ok) {
            // SUCCESS! Set the global ID and update UI
            currentPaperId = result.paper_id;
            
            document.getElementById('paper-status').innerText = `Paper Draft Created! ID: ${currentPaperId}`;
            alert(`Paper created successfully with ID ${currentPaperId}. You can now add questions.`);
            
            // OPTIONAL: Update the URL to reflect the new ID without reloading
            window.history.pushState({}, '', `paper_creator.html?paperId=${currentPaperId}`);

            // Enable the question search/add section
            document.getElementById('question-management-section').style.display = 'block';

        } else {
            // ERROR handling
            alert(`Error creating paper: ${result.error || 'Unknown error'}`);
            createButton.disabled = false; // Re-enable button on error
        }

    } catch (error) {
        console.error("Network error creating paper:", error);
        alert("A network error occurred. Could not create paper.");
        createButton.disabled = false; // Re-enable button on network error
    }
}