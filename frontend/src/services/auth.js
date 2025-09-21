
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
  }

  // Logout user
  logout() {
    this.isLoggedIn = false;
    this.user = null;
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('user');
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

  getCurrentUser() {
    return this.user;
  }
}

export default new AuthService();
