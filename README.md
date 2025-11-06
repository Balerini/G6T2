# 🎯 About

This is a **full-stack project management system** that enables organizations to efficiently manage projects and tasks.  
The application provides a seamless experience for teams to:

- ✅ **Create and manage projects** with clear timelines  
- 📝 **Track tasks** through various workflow stages  
- 👥 **Collaborate** with team members across departments  
- 📊 **Visualize progress** with intuitive dashboards  
- 🎨 **Enjoy a modern, responsive** user interface  

---

## 🛠️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Balerini/G6T2.git
cd project-directory
```

### 2️⃣ Setup 
```bash
cd frontend > npm install 
npm run serve
```

```bash
cd backend > pip install -r requirements.txt
py app.py
```

### 3️⃣ The application will be available at:
👉 http://localhost:8080
👉 Backend: http://localhost:8000
---

## ⚙️ Tech Stack

### 🖥️ Frontend

- **Framework:** Vue.js  
- **Language:** JavaScript  
- **Styling:** CSS3 with **responsive design** for cross-device compatibility  
- **Files Needed:** .env
---

### 🧠 Backend

- **Language:** Python  
- **Framework:** Flask *(API server)*  
- **Key Features:**
  - RESTful API endpoints  
  - Authentication and authorization  
  - Data validation  
  - Firebase integration
 
- **Files Needed:** 
  - .env
  - requirements.txt
  - service-account.json

---

### 🗄️ Database

- **Platform:** Firebase  
- **Services Used:**
  - **Firestore** – NoSQL cloud database  
  - **Firebase Authentication** – Secure user sign-in  
  - **Real-time Data Synchronization** – Instant updates across clients
 
  
### 💻 Testing 
### Run All Unit Tests

```bash
# From backend directory
python -m unittest discover testing/unit -v
```

### Run Unit Tests with Coverage

```bash
# Run all unit tests with coverage report
python run_unit_tests_with_coverage.py all

# Run specific feature with coverage
python run_unit_tests_with_coverage.py password
python run_unit_tests_with_coverage.py email
python run_unit_tests_with_coverage.py notification

# Run with coverage threshold (e.g., 80%)
python run_unit_tests_with_coverage.py threshold 80
```

### View Coverage Report

After running with coverage:
```bash
# View terminal report
coverage report

# Generate HTML report (opens in browser)
coverage html
# Then open: htmlcov/index.html
```

### Run All Integration Tests

```bash
# From backend directory
python -m pytest testing/integration/ -v

# Or using unittest
python -m unittest discover testing/integration -v
```

### Run Selenium Tests

```bash
# Setting up
Add pytest.exe from your installed scripts folder into path of your system environment variables

# From backend directory
python -m pytest testing/e2e/ -v

# Notes
Test may fail when the laptop hardware is too quick - Selenium tries to execute action before page renders. 
```

