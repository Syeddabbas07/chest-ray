# Chest Ray: Pneumonia Diagnosis Web App

An intelligent web-based diagnostic tool that analyzes chest X-rays using a machine learning model to detect pneumonia and streamline the treatment process for patients, non-experts, and expert clinicians.

## 👥 Team
- Syed Abbas Shah
- Haleema Nadeem
- Muaz Amer Jutt
- Syed Shahvaiz Hassan
- Josh
- Ade

## 💡 Features
- Role-based login (Patient, Non-Expert, Expert)
- Upload chest X-rays for ML-based pneumonia diagnosis
- View reports and treatment recommendations
- Patient history and prescription management
- Dashboards tailored to user roles

## 🛠️ Tech Stack
- Frontend: (Lo-Fi in Draw.io) and HTML
- Backend: Python Flask
- Database: SQLite
- Machine Learning: CNN
- Version Control: Git + GitHub

## 🚀 How to Run the App


## 📂 Project Structure
```
chest-ray-app/
├── __pycache__
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   └── ml_model.py
│
├── templates/ --- CONTAIN HTML FILES
│
├── static/  ---- HTML PNG & CSS
│   ├── uploads/  ---- XRAY IMAGE STORE PATH
│
├── instance/
│   └── ChestXray.db
│
├── HasPna_v2.keras
├── config.py
├── notes.txt
├── Pytest.txt
├── run.py
├── testcase.py
├── README.md
└── .gitignore
```

## ✅ How to Contribute
- Fork the repo and clone it locally.
- Create a new branch: `git checkout -b feature-name`
- Commit your changes: `git commit -m "Add something"`
- Push to the branch: `git push origin feature-name`
- Create a pull request on GitHub.

## 🧪 Testing
Use pytest to run tests:
```bash
pytest tests/
```

## 📷 Screenshots
(Add screenshots of your interface here for submission)
