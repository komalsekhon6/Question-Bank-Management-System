// --- Function to check user role and redirect if unauthorized ---
function checkRole(requiredRole) {
    // We use localStorage to persist the role across sessions
    const role = localStorage.getItem('userRole'); 
    
    if (!role) {
        // Not logged in: Always redirect to login
        window.location.href = 'login.html'; 
        return false;
    }
    
    // Check if a specific role is required
    if (requiredRole && role !== requiredRole) {
        console.error(`Access Denied: Required role is '${requiredRole}' but current role is '${role}'.`);
        
        // Redirect based on the role they DO have
        if (role === 'Student') {
            window.location.href = 'student_view.html'; 
        } else if (role === 'Faculty') {
            window.location.href = 'faculty_dashboard.html';
        } else {
             window.location.href = 'login.html';
        }
        return false;
    }
    return true; // Access granted
}

// Note: The logout function is in logout_redirect.js