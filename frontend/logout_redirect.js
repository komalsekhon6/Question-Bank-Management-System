// --- Dedicated Logout Function ---
function logout() {
    // Clear the stored user role
    localStorage.removeItem('userRole');
    
    // Redirect the user to the login page
    window.location.href = 'login.html';
}