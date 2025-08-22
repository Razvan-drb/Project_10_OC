# 📋 Project Workflow Guide

---

## 🚀 Immediate Actions

### 🔧 Set Up the Project

1. **Clone and fork** the repository.
2. **Set up the project locally** following the [README](./README.md) instructions.
3. **Install required dependencies**:
   - Flask
   - pytest
   - Locust
   - Others listed in `requirements.txt`

---

## 🐞 Phase 1: Bug Fixes

### 📄 Review QA Report

- Check the **"Issues"** section in the repository for reported bugs.
- **Reproduce bugs locally** to better understand their causes.

### ❗ Fix Critical Bug

- **Address the crash bug first**, as it causes the application to fail.

### 🛠️ General Code Review

- Read through the **entire codebase** to identify and fix any hidden bugs.
- Add **proper error handling** where it's missing.

---

## ✨ Phase 2: Implement New Features

### 📌 Check the "Issues" Section

- Focus on tasks labeled for **Phase 2** implementation.

### 🧪 Follow TDD (Test-Driven Development)

- **Write tests first**, then implement the features.
- Test:
  - **Happy paths** (expected behavior)
  - **Sad paths** (error cases and exceptions)

---

## 🧪 Testing & Reporting

### ✅ Thorough Testing

- Test **all existing and new functionalities**.
- Use:
  - `pytest` for **unit and integration tests**
  - `Locust` for **performance testing**

### 📊 Prepare Reports

- **Test Report**:
  - Document test cases
  - Include results and test coverage

- **Performance Report**:
  - Include performance benchmarks from Locust

---

## 📦 Code Review & Submission

### 🧾 Push Changes to QA Branch

- Ensure all fixes and new features are pushed to the correct branch.

### ✅ Prepare for Review

- Be ready to **explain your code choices and fixes**.
- Make sure code follows **company coding standards**.

---

## 📌 Additional Notes

### 📙 Follow Development Guidelines

- Stick to the **functional specifications document** provided.

### 📣 Communicate if Blocked

- Sam is unavailable — **reach out to other team members** if needed.

---

## 🧰 Summary of Tools & Technologies

| Component     | Technology                     |
|---------------|---------------------------------|
| Backend       | Flask + JSON (no database)     |
| Testing       | `pytest` (unit/integration)     |
| Performance   | `Locust` (load/performance)     |
| Methodology   | TDD (Test-Driven Development)   |
