class AuthService {
  constructor() {
    this.isLoggedIn = false;
    this.user = null;
  }

  // Set user as logged in
  login(userData) {
    this.isLoggedIn = true;
    this.user = userData;
   
    sessionStorage.setItem('isLoggedIn', 'true');
    sessionStorage.setItem('user', JSON.stringify(userData));
    
    console.log(`User ${userData.name} from ${userData.division_name} division logged in`);
  }

  // Logout user
  logout() {
    this.isLoggedIn = false;
    this.user = null;
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('user');
    
    console.log('User logged out and session cleared');
  }

  // Check if user is logged in
  checkAuthStatus() {
    const stored = sessionStorage.getItem('isLoggedIn');
    const userData = sessionStorage.getItem('user');
    
    if (stored === 'true' && userData) {
      this.isLoggedIn = true;
      this.user = JSON.parse(userData);
      return true;
    }
    
    this.isLoggedIn = false;
    this.user = null;
    return false;
  }

  // Get current user
  getCurrentUser() {
    return this.user;
  }

  // Get current user's division
  getCurrentUserDivision() {
    return this.user ? this.user.division_name : null;
  }

  // Check if current user is a manager
  isManager() {
    if (!this.user) return false;
    
    // Check if role contains "manager" (case insensitive)
    const role = this.user.role_name || this.user.role || '';
    return role.toLowerCase().includes('manager');
  }

  // Get user role information
  getUserRole() {
    if (!this.user) return null;
    
    return {
      role: this.user.role,
      role_name: this.user.role_name,
      role_num: this.user.role_num,
      isManager: this.isManager()
    };
  }

  // Check if user has division access
  hasDivisionAccess(targetDivision) {
    if (!this.user) return false;
    
    // Users can only access their own division data
    return this.user.division_name === targetDivision;
  }

  // Validate user session and division access
  validateDivisionAccess(requiredDivision) {
    if (!this.checkAuthStatus()) {
      console.warn('User not authenticated');
      return false;
    }
    
    if (!this.hasDivisionAccess(requiredDivision)) {
      console.warn(`Access denied: User from ${this.user.division_name} cannot access ${requiredDivision} data`);
      return false;
    }
    
    return true;
  }

  // Get user info for display
  getUserDisplayInfo() {
    if (!this.user) return null;
    
    return {
      name: this.user.name,
      email: this.user.email,
      division: this.user.division_name,
      role: this.user.role_name || this.user.role,
      isManager: this.isManager()
    };
  }
}

export default new AuthService();