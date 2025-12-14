# 🎓 College Fee Payment System

## 📌 Project Description
The College Fee Payment System is a web-based application developed using *Python Flask*.  
It allows students to pay college fees online by entering academic and payment details, verifying the information, and generating a digital receipt.

This project is developed *for college/institutional purpose*, not for individual use.

---

## 🎯 Objectives
- To provide an online fee payment system for students
- To reduce manual work in fee collection
- To maintain digital records of payments
- To generate fee payment receipts

---

## 🛠 Technologies Used
- *Frontend:* HTML, CSS, JavaScript
- *Backend:* Python (Flask)
- *Database:* JSON files
- *IDE:* VS Code

---

## 📂 Project Structure

college_fee_payment/
│
├── app.py
├── README.md
├── requirements.txt
│
├── database/
│   ├── users.json
│   ├── students.json
│   └── payments.json
│
├── templates/
│   ├── login.html
│   ├── select_payee.html
│   ├── enter_details.html
│   ├── verify.html
│   ├── payment.html
│   └── receipt.html
│
└── static/
    ├── css/style.css
    └── js/script.js


---

## 🔐 Login Module
- Login is *open to all students*
- Authentication is not restricted
- In real colleges, login is handled by ERP systems

---

## 📋 Modules Implemented
1. Login Module  
2. Payee Selection Module  
3. Payment Details Entry  
4. Verification Module  
5. Payment Processing Module  
6. Receipt Generation Module  

---

## ▶ How to Run the Project

1. Install Python (3.10 or above)
2. Install Flask:

pip install flask

3. Run the application:

python app.py

4. Open browser and visit:

http://127.0.0.1:5000


---

## 🧾 Output
- Students can enter fee details
- Payment is processed (demo)
- Receipt is generated
- Data is stored in JSON files

---

## 📌 Conclusion
The College Fee Payment System provides a simple and efficient way to manage fee payments digitally.  
It reduces paperwork and improves transparency in college fee management.

---

## 👨‍🎓 Developed For
*Academic / College Project Submission*