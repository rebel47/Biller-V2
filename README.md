# 💰 Biller - AI-Powered Expense Management System

**Biller** is a modern, intelligent expense tracking application that leverages AI to automate receipt processing and provide real-time financial insights. Built with Streamlit and powered by Google's Gemini Vision API, it offers an intuitive interface for managing personal or business expenses with automated categorization and detailed analytics.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)

## ✨ Features

### 🤖 AI-Powered Receipt Processing
- **Automated Text Extraction**: Uses Google's Gemini Vision API to extract text from receipt images
- **Intelligent Categorization**: Automatically categorizes expenses into predefined categories
- **Real-time Processing**: Instant analysis of uploaded receipt images
- **Multi-format Support**: Supports PNG, JPEG, HEIC image formats

### 🔐 Secure Authentication
- **User Registration & Login**: Secure user authentication system
- **Encrypted Password Storage**: Safe storage of user credentials
- **Session Management**: Persistent login sessions with remember me option
- **Profile Management**: Update personal information and credentials

### 📊 Financial Analytics
- **Real-time Expense Tracking**: Live updates of spending data
- **Monthly Summaries**: Track spending patterns month by month
- **Category-wise Analysis**: Breakdown expenses by categories
- **Interactive Visualizations**: Beautiful charts and graphs using Plotly
- **Spending Trends**: Historical expense analysis and insights

### 💾 Data Management
- **Cloud Storage**: Secure data storage using Firebase Firestore
- **Manual Entry**: Add expenses manually when receipts aren't available
- **Bulk Operations**: Delete multiple expenses at once
- **Data Export**: Easy access to your financial data

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Clean Interface**: Modern, minimalistic design
- **Dark/Light Themes**: Beautiful gradient designs
- **Intuitive Navigation**: Easy-to-use sidebar navigation

## 🛠️ Tech Stack

### Frontend
- **[Streamlit](https://streamlit.io/)** - Web application framework
- **[Plotly](https://plotly.com/)** - Interactive data visualizations
- **CSS3** - Custom styling and animations

### Backend
- **[Python 3.8+](https://python.org/)** - Core programming language
- **[Firebase Firestore](https://firebase.google.com/products/firestore)** - NoSQL database
- **[Firebase Auth](https://firebase.google.com/products/auth)** - User authentication
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis

### AI & ML
- **[Google Gemini Vision API](https://ai.google.dev/)** - OCR and text extraction
- **[PIL (Pillow)](https://pillow.readthedocs.io/)** - Image processing
- **[pillow-heif](https://github.com/bigcat88/pillow_heif)** - HEIC image support

### Deployment
- **[Streamlit Cloud](https://streamlit.io/cloud)** - Hosting platform
- **Environment Variables** - Secure configuration management

## 📋 Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or higher
- A Google Cloud Account (for Gemini API)
- A Firebase Account
- Git installed on your machine

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rebel47/Biller-V2.git
cd Biller-V2
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

### 1. Google Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create a new project or select existing one
3. Enable the Gemini API
4. Generate an API key
5. Copy the API key for later use

### 2. Firebase Setup

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Follow the setup wizard

#### Setup Firestore Database
1. In Firebase Console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" for development
4. Select a location for your database

#### Setup Authentication
1. Go to "Authentication" in Firebase Console
2. Click "Get started"
3. Enable "Email/Password" sign-in method

#### Get Firebase Configuration
1. Go to Project Settings (gear icon)
2. In the "General" tab, scroll to "Your apps"
3. Click "Add app" and choose "Web"
4. Register your app and copy the configuration

#### Create Service Account
1. Go to Project Settings → "Service accounts"
2. Click "Generate new private key"
3. Download the JSON file

### 3. Environment Variables

Create a `.env` file in the project root:

```env
# Google API
GOOGLE_API_KEY=your_google_gemini_api_key

# Firebase Web Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
FIREBASE_APP_ID=your_app_id

# Firebase Admin (for local development)
FIREBASE_ADMIN_KEY_PATH=firebase-admin-key.json
```

Place your Firebase service account JSON file in the project root as `firebase-admin-key.json`.

## 🚀 Running the Application

### Local Development

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

### Production Deployment

#### Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Connect your GitHub account
   - Select your repository

3. **Configure Environment Variables**:
   In Streamlit Cloud, go to your app settings and add these secrets:
   
   ```toml
   GOOGLE_API_KEY = "your_google_api_key"
   FIREBASE_API_KEY = "your_firebase_api_key"
   FIREBASE_AUTH_DOMAIN = "your-project.firebaseapp.com"
   FIREBASE_DATABASE_URL = "https://your-project-default-rtdb.firebaseio.com/"
   FIREBASE_PROJECT_ID = "your-project-id"
   FIREBASE_STORAGE_BUCKET = "your-project.appspot.com"
   FIREBASE_MESSAGING_SENDER_ID = "your_messaging_sender_id"
   FIREBASE_APP_ID = "your_app_id"
   FIREBASE_PRIVATE_KEY_ID = "your_private_key_id"
   FIREBASE_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
   your_private_key_content_here
   -----END PRIVATE KEY-----"""
   FIREBASE_CLIENT_EMAIL = "your_service_account_email"
   FIREBASE_CLIENT_ID = "your_client_id"
   ```

4. **Deploy**: Your app will automatically deploy and be available at your Streamlit Cloud URL.

## 📱 Usage

### Getting Started

1. **Register an Account**:
   - Visit the application
   - Click "Register" 
   - Fill in your details and create an account

2. **Login**:
   - Use your email and password to log in
   - Optionally check "Remember me" for persistent sessions

### Managing Expenses

#### Upload Receipt (AI Processing)
1. Go to "Upload Bill" page
2. Select "Scan Receipt" tab
3. Upload an image of your receipt
4. Click "Process with AI"
5. Review and edit the extracted items
6. Save to your database

#### Manual Entry
1. Go to "Upload Bill" page
2. Select "Manual Entry" tab
3. Fill in the expense details:
   - Date
   - Amount
   - Category
   - Description
4. Click "Save Entry"

### Viewing Analytics

#### Dashboard
- View monthly spending overview
- See total expenses and bill counts
- Quick access to recent bills

#### Analytics Page
- Monthly spending trends
- Category-wise breakdown
- Weekly spending patterns
- Top expenses analysis

#### My Bills
- View all your expenses
- Filter by category, date range, or search terms
- Delete multiple bills at once

### Profile Management
- Update personal information
- Change password
- View account statistics

## 📊 Database Schema

### Users Collection
```javascript
{
  id: "auto_generated_id",
  username: "unique_username",
  email: "user@example.com",
  name: "Full Name",
  firebase_uid: "firebase_user_id",
  created_at: "timestamp",
  updated_at: "timestamp"
}
```

### Bills Collection
```javascript
{
  id: "auto_generated_id",
  username: "user_reference",
  date: "YYYY-MM-DD",
  category: "grocery|utensil|clothing|miscellaneous",
  amount: 99.99,
  description: "Item description",
  created_at: "timestamp",
  updated_at: "timestamp"
}
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit Your Changes**:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the Branch**:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comments for complex logic
- Write meaningful commit messages
- Test your changes thoroughly
- Update documentation as needed

## 🐛 Troubleshooting

### Common Issues

#### Firebase Authentication Errors
- Verify your Firebase configuration
- Check if email/password authentication is enabled
- Ensure your domain is authorized in Firebase Console

#### Gemini API Errors
- Verify your Google API key is correct
- Check if you have sufficient API credits
- Ensure the image format is supported

#### Deployment Issues
- Check all environment variables are set correctly
- Verify your requirements.txt includes all dependencies
- Review Streamlit Cloud logs for specific errors

### Getting Help

If you encounter issues:

1. Check the [Issues](https://github.com/rebel47/Biller-V2/issues) page
2. Search for existing solutions
3. Create a new issue with detailed information:
   - Error messages
   - Steps to reproduce
   - Environment details

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Developer**: Mohammad Ayaz Alam  
**Email**: alam.ayaz47@gmail.com  
**Project Link**: [https://github.com/rebel47/Biller-V2](https://github.com/rebel47/Biller-V2)  
**Live Demo**: [https://biller.streamlit.app](https://biller.streamlit.app)

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Google Gemini AI](https://ai.google.dev/) for powerful vision API
- [Firebase](https://firebase.google.com/) for backend services
- [Plotly](https://plotly.com/) for beautiful visualizations
- The open-source community for inspiration and tools

---

**⭐ If you find this project helpful, please give it a star on GitHub!**

## 🔄 Version History

- **v1.0.0** - Initial release with core features
  - AI receipt processing
  - User authentication
  - Basic analytics
  - Responsive UI

---

*Made with ❤️ and ☕ by [Mohammad Ayaz Alam]*