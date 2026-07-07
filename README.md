# A Full-Stack Machine Learning System for Fraud Detection in ERP Order-to-Cash (O2C) Processes
This project is the practical implementation of a Bachelor's Thesis (TFG). It features an auditing system to simulate, inject, and detect financial and operational anomalies within a company's Order-to-Cash (O2C) cycle using unsupervised Machine Learning algorithms and an interactive web dashboard.

## System Architecture
* Backend: REST API built with **Python** and **Flask**, responsible for synthetic log generation, fraud pattern injection, and executing the Machine Learning models (Isolation Forest and Local Outlier Factor).
* Frontend: Interactive Dashboard developed with **Vue.js**, **PrimeVue** (UI component library), and **Chart.js** (visual analytics).

## The project has been developed under the following environment:
* Python 3.13.1
* Node.js v22.13.1

## 1- Starting the Python Backend
1. Open a terminal in the project's root directory (where "api.py" is located).
2. Create and set up the virtual environment:

*Create the virtual environment:*

```bash
python -m venv .venv
```

*Activate the virtual environment (Windows):*

```powershell
.venv\Scripts\activate
```

*Install the project dependencies:*

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
python api.py
```

The local server will be listening at: http://localhost:5000

## 2- Deploying the frontend
1. Open another terminal and write the following: 
```bash
cd fraud-dashboard
npm install
npm run dev
```

The web interface will deploy at: http://localhost:5173
