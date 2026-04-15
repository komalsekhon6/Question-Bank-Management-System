// utils.js

// --- CONFIGURATION CONSTANTS ---
const API_BASE_URL = 'http://127.0.0.1:5000/api';
const ROLE_KEY = 'userRole';
const USERNAME_KEY = 'username';

// --- Shared Function: Logout ---
function logout() {
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(USERNAME_KEY);
    window.location.href = 'index.html'; // Redirect to login page
}

// --- Shared Function: Load Courses for Dropdown ---
/**
 * Fetches and populates the Course dropdown menu.
 * @param {string} selectElementId - The ID of the <select> element (e.g., 'courseSelect').
 * @param {function} [callback] - An optional function to run after courses are loaded.
 */
async function loadCourses(selectElementId, callback) {
    const select = document.getElementById(selectElementId);
    if (!select) return; 

    // Reset dropdown with loading message
    select.innerHTML = '<option value="">Loading Courses...</option>';
    select.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/courses`);
        const courses = await response.json();
        
        // Clear old options, keep default
        select.innerHTML = '<option value="">Select Course</option>'; 
        select.disabled = false;
        
        if (response.ok) {
            courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.CourseID;
                option.textContent = `${course.CourseName} (${course.CourseID})`;
                select.appendChild(option);
            });
        } else {
             select.innerHTML = `<option value="">Error: ${courses.error || 'Failed to load'}</option>`;
             console.error(`Error loading courses for ${selectElementId}:`, courses.error);
        }

        if (callback) callback();

    } catch (error) {
        console.error(`Network error loading courses for ${selectElementId}:`, error);
        select.innerHTML = '<option value="">Error loading courses</option>';
        select.disabled = false;
    }
}

// --- Shared Function: Load CLOs based on selected Course ---
/**
 * Fetches and populates the CLO dropdown menu based on the selected course.
 * @param {string} courseSelectId - The ID of the Course <select> element.
 * @param {string} cloSelectId - The ID of the CLO <select> element to populate.
 * @param {string} [allOptionText='Select CLO'] - The default text for the initial option.
 */
async function loadCLOs(courseSelectId, cloSelectId, allOptionText = 'Select CLO') {
    const courseSelect = document.getElementById(courseSelectId);
    const cloSelect = document.getElementById(cloSelectId);
    
    // Safety check
    if (!courseSelect || !cloSelect) return; 

    const courseID = courseSelect.value;

    // If no course is selected
    if (!courseID) {
        cloSelect.innerHTML = `<option value="">${allOptionText}</option>`;
        return;
    }

    cloSelect.innerHTML = '<option value="">Loading...</option>';

    try {
        // API call using the alphanumeric CourseID
        const response = await fetch(`${API_BASE_URL}/clos/${courseID}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to fetch CLOs: ${response.statusText}`);
        }
        
        const clos = await response.json();
        
        // Reset with default option
        cloSelect.innerHTML = `<option value="">${allOptionText}</option>`; 
        
        clos.forEach(clo => {
            const option = document.createElement('option');
            // Value is the CLOID (integer from your DB)
            option.value = clo.CLOID;
            
            // Format display text: CLO-1: Description
            const displayText = `CLO-${clo.CLOID}: ${clo.CLOText}`;
            option.textContent = displayText.substring(0, 100) + (displayText.length > 100 ? '...' : ''); 
            cloSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading CLOs:', error);
        cloSelect.innerHTML = `<option value="">Error loading CLOs</option>`;
    }
}

// --- Shared Function: Load Faculty for Dropdown ---
/**
 * Fetches and populates the Faculty dropdown menu.
 * @param {string} selectElementId - The ID of the <select> element (e.g., 'facultySelect').
 * @param {string} [allOptionText='All Faculty'] - The default text for the initial option.
 */
async function loadFaculty(selectElementId, allOptionText = 'All Faculty') {
    const select = document.getElementById(selectElementId);
    if (!select) return; 

    // Reset dropdown with loading message
    select.innerHTML = `<option value="">Loading Faculty...</option>`;
    select.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/faculty`);
        const facultyList = await response.json();
        
        // Clear and add default option
        select.innerHTML = `<option value="">${allOptionText}</option>`; 
        select.disabled = false;
        
        if (response.ok) {
            facultyList.forEach(faculty => {
                const option = document.createElement('option');
                option.value = faculty.FacultyID;
                option.textContent = faculty.FacultyName;
                select.appendChild(option);
            });
        } else {
             select.innerHTML = `<option value="">Error: ${facultyList.error || 'Failed to load'}</option>`;
             console.error(`Error loading faculty for ${selectElementId}:`, facultyList.error);
        }

    } catch (error) {
        console.error(`Network error loading faculty for ${selectElementId}:`, error);
        select.innerHTML = '<option value="">Error loading faculty</option>';
        select.disabled = false;
    }
}