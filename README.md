# 💸 Expense Tracker

A simple, clean, and functional web-based expense tracker built using **Python**, **Flask**, and **SQLite**.

---

## 🚀 Features

- 🧾 Add, edit, and delete your expenses
- 🔐 User registration and login (with secure password hashing)
- 📅 View expenses by date, category, and description
- 📊 Summary view to see spending by category
- 📄 Pagination for viewing expenses
- ✅ Flash messages for clean user feedback
- 🎨 Basic styling with CSS

---

## 🛠️ Tech Stack

- ⚙️ **Backend:** Python + Flask
- 🗃️ **Database:** SQLite
- 🌐 **Frontend:** HTML, CSS (basic styling)
- 🧠 **Security:** Password hashing with Werkzeug

---

## 📂 Project Structure

```
expense-tracker/
├── static/                        # 🧾 Static assets like CSS
│   └── style.css                 # 🎨 Main stylesheet for all HTML pages
│
├── templates/                     # 📄 HTML templates rendered by Flask
│   ├── add_expense.html         # Form to add a new expense
│   ├── edit_expense.html        # Form to edit an existing expense
│   ├── home.html                # Dashboard listing user expenses
│   ├── login.html               # Login page for existing users
│   ├── register.html            # Registration page for new users
│   └── summary.html             # Summary of expenses by category
│
├── users.db                       # 🗄️ SQLite database storing users and expenses
├── app.py                         # 🧠 Main Flask application
└── README.md                      # 📘 Project documentation
```
---
