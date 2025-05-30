# 🤖 AIversus: Local AI Chat Application

**AIversus** is a locally-hosted AI chat application that allows users to interact with artificial intelligence in real-time. Built with a lightweight tech stack and designed for efficient local use, AIversus is the perfect sandbox environment for experimenting with conversational AI capabilities.

---

## 🚀 Features

- 💬 **Intelligent Conversations**: AI-driven chatbot responses for dynamic, human-like interactions.
- 🎨 **Lightweight Frontend**: Built with HTML, CSS, and JavaScript for fast and responsive design.
- 🛠️ **Robust Backend**: Python powers the server-side logic for smooth communication.
- 📂 **Hybrid Databases**: Utilizes **MongoDB** for unstructured data (e.g., chat history) and **MySQL** for relational data.
- 💻 **Local Setup**: Entire application runs seamlessly on your local machine.

---

## 🏗️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask/FastAPI/Django)
- **Databases**: MongoDB (NoSQL) and MySQL (Relational)
- **AI Framework**: OpenAI API or custom models
- **Hosting**: Localhost

---

## 📂 Project Structure

```
AIversus/
├── frontend/
│   ├── index.html         # Main webpage
│   ├── style.css          # Styling
│   └── app.js             # Frontend functionality
├── backend/
│   ├── app.py             # Python server
│   ├── api/               # APIs for handling requests
│   └── requirements.txt   # Backend dependencies
├── database/
│   ├── mongodb/           # MongoDB collections and scripts
│   └── mysql/             # MySQL schema and scripts
└── README.md              # Project documentation
```

---

## 🛠️ Installation & Setup

Follow these steps to run the AIversus project locally:

### Prerequisites
- Python 3.8+
- Node.js (for JavaScript dependencies, if needed)
- MongoDB and MySQL installed on your system

### Step 1: Clone the Repository
```bash
git clone https://github.com/Godstaf/AIVersus.git
cd aiversus
```
### Step 2: Set Up the Backend

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables for MongoDB and MySQL in a `.env` file:
   ```env
   MONGO_URI="mongodb://localhost:27017/your_database_name"
   MYSQL_USER="your_mysql_user"
   MYSQL_PASSWORD="your_mysql_password"
   MYSQL_DB="your_mysql_db_name"
   ```
3. Start the backend server:
   ```bash
   python app.py
   ```

### Step 4: Connect Databases
- Ensure MongoDB and MySQL are running locally, and the schemas are correctly configured as per `database/` scripts.

---

## 🤝 Contributing

Contributions are always welcome! Fork the repo, make your changes, and submit a pull request for review.

---

## 📝 License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it.

