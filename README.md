# Biller - AI-Powered Expense Management System

## Overview

**Biller** is a modern expense tracking application that leverages AI to automate receipt processing and provide real-time financial insights. Built with Streamlit and powered by Google's Gemini Vision API, it offers an intuitive interface for managing personal or business expenses with automated categorization and detailed analytics.

Last Updated: 2025-02-21 03:09:50 UTC

## Features

- **AI-Powered Receipt Processing**: 
  - Automated text extraction using Google's Gemini Vision API
  - Intelligent expense categorization
  - Real-time amount and date detection

- **Secure Authentication**:
  - User registration and login system
  - Encrypted password storage
  - Session management

- **Financial Analytics**:
  - Real-time expense tracking
  - Monthly and category-wise summaries
  - Interactive visualizations using Plotly
  - Current month and historical expense trends

- **Data Management**:
  - Automated data extraction from receipts
  - Manual entry capability
  - Bulk delete functionality
  - Profile management

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **AI Integration**: Google Gemini Vision API
- **Authentication**: Supabase Auth
- **Visualization**: Plotly
- **Data Processing**: Pandas

## Prerequisites

- Python 3.8+
- Supabase Account
- Google Cloud Account (for Gemini API)
- Required Python packages (see requirements.txt)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rebel47/Biller-Supabase.git
   cd biller
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file with:
   ```plaintext
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GOOGLE_API_KEY=your_gemini_api_key
   ```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    password TEXT NOT NULL
);
```

### Bills Table
```sql
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    FOREIGN KEY (username) REFERENCES users(username)
);
```

## Usage

1. **Start the application**:
   ```bash
   streamlit run main.py
   ```

2. **Register/Login**:
   - Create a new account or login with existing credentials
   - Access your personalized dashboard

3. **Upload Bills**:
   - Navigate to "Upload Bill" tab
   - Choose image upload or manual entry
   - For Image Upload:
     - Upload receipt image
     - Review extracted information
     - Manually adjust amounts if needed
     - Save to database
   - For Manual Entry:
     - Enter date, category, and amount
     - Add description
     - Click save to store

4. **View Analytics**:
   - Check current month expenses
   - View category-wise breakdown
   - Analyze monthly trends
   - Track spending patterns

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework
- [Google Gemini AI](https://ai.google.dev/) for vision API
- [Supabase](https://supabase.com/) for database and authentication
- [Plotly](https://plotly.com/) for visualizations

## Contact

Developed by: rebel47
Project Link: [https://github.com/rebel47/Biller-Supabase](https://github.com/rebel47/Biller-Supabase)
