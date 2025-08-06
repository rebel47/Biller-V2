# 📱 Biller Mobile App

A modern, minimalistic Flutter mobile application that complements the existing Biller-V2 web application. The app provides a seamless mobile experience for expense tracking with Firebase integration.

![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Material Design](https://img.shields.io/badge/Material%20Design%203-757575?style=for-the-badge&logo=material-design&logoColor=white)

## ✨ Features

### 📊 Dashboard
- Overview of monthly expenses and recent bills
- Quick stats and spending insights
- Quick access to upload and analytics features
- Personalized greeting with user profile

### 📸 Upload Bills
- **Camera Integration**: Capture bills directly from the camera
- **Gallery Support**: Select images from device gallery
- **Manual Entry**: Add expense details manually
- **Category Selection**: Organize expenses by categories
- **Date Selection**: Set custom expense dates

### 📋 My Bills
- **Complete Bill Management**: View all uploaded bills
- **Advanced Filtering**: Filter by category, date, and search terms
- **Bulk Operations**: Select and delete multiple bills
- **Real-time Updates**: Live synchronization with Firebase
- **Search Functionality**: Find bills quickly

### 📈 Analytics
- **Spending Trends**: Monthly and multi-month analysis
- **Category Breakdown**: Visual pie charts for spending by category
- **Top Expenses**: Highest spending items
- **Interactive Charts**: Beautiful, responsive charts using FL Chart
- **Period Selection**: View data for different time periods

### 👤 Profile
- **User Management**: View and edit profile information
- **Statistics Overview**: Personal spending statistics
- **App Settings**: Notifications, security, and preferences
- **Data Export**: Download expense data
- **Sign Out**: Secure logout functionality

### 🔐 Authentication
- **Google Sign-In**: OAuth integration with Google
- **Email/Password**: Traditional email authentication
- **Firebase Auth**: Secure authentication with Firebase
- **Profile Sync**: Automatic profile synchronization

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Flutter 3.24+ with Material Design 3
- **Backend**: Firebase (Firestore, Auth, Storage)
- **State Management**: Provider pattern
- **Charts**: FL Chart for analytics
- **Image Handling**: Image picker and caching
- **Authentication**: Firebase Auth with Google Sign-In

### Project Structure
```
mobile_app/
├── lib/
│   ├── constants/          # App-wide constants and themes
│   │   └── app_theme.dart
│   ├── models/            # Data models
│   │   ├── bill_model.dart
│   │   └── user_model.dart
│   ├── screens/           # UI screens
│   │   ├── auth/         # Authentication screens
│   │   ├── home/         # Main app screens
│   │   └── splash_screen.dart
│   ├── services/         # Business logic and API calls
│   │   ├── auth_service.dart
│   │   └── firestore_service.dart
│   ├── widgets/          # Reusable UI components
│   ├── firebase_options.dart
│   └── main.dart
├── android/              # Android-specific configuration
├── ios/                  # iOS-specific configuration
├── assets/              # Images, fonts, and other assets
└── pubspec.yaml         # Dependencies and configuration
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.1.0 or higher
- Dart SDK 3.0.0 or higher
- Android Studio / Xcode for device testing
- Firebase account for backend services
- Google Cloud account for authentication

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rebel47/Biller-V2.git
   cd Biller-V2/mobile_app
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Firebase Setup**
   
   a. **Create a Firebase project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or use existing one
   - Enable Firestore Database
   - Enable Authentication (Email/Password and Google)
   - Enable Firebase Storage

   b. **Configure Firebase for Flutter**
   ```bash
   # Install Firebase CLI
   npm install -g firebase-tools
   
   # Login to Firebase
   firebase login
   
   # Install FlutterFire CLI
   dart pub global activate flutterfire_cli
   
   # Configure Firebase for your Flutter app
   flutterfire configure
   ```

   c. **Update Firebase configuration**
   - Replace the placeholder values in `lib/firebase_options.dart` with your actual Firebase configuration

4. **Google Sign-In Setup**
   
   **For Android:**
   - Download `google-services.json` from Firebase Console
   - Place it in `android/app/` directory
   
   **For iOS:**
   - Download `GoogleService-Info.plist` from Firebase Console
   - Add it to your iOS project in Xcode

5. **Update permissions**
   
   The necessary permissions are already configured in:
   - `android/app/src/main/AndroidManifest.xml` (Camera, Storage, Internet)
   - `ios/Runner/Info.plist` (when you set up iOS)

### Running the App

1. **Check Flutter installation**
   ```bash
   flutter doctor
   ```

2. **Run on Android/iOS**
   ```bash
   # For Android
   flutter run
   
   # For iOS
   flutter run -d ios
   
   # For specific device
   flutter devices
   flutter run -d <device-id>
   ```

3. **Build for release**
   ```bash
   # Android APK
   flutter build apk --release
   
   # iOS
   flutter build ios --release
   ```

## 🔧 Configuration

### Firebase Configuration

1. **Firestore Database Rules**
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId} {
         allow read, write: if request.auth != null && request.auth.uid == resource.data.firebase_uid;
       }
       match /bills/{billId} {
         allow read, write: if request.auth != null && request.auth.uid == resource.data.firebase_uid;
       }
     }
   }
   ```

2. **Firebase Storage Rules**
   ```javascript
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /bills/{userId}/{allPaths=**} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
     }
   }
   ```

### Environment Variables

Create a `.env` file in the project root (optional, for additional configuration):

```env
# App Configuration
APP_NAME=Biller
APP_VERSION=1.0.0

# Firebase Configuration (already in firebase_options.dart)
# These are handled by FlutterFire automatically
```

## 📱 App Screens

### Authentication Flow
1. **Splash Screen**: App initialization and loading
2. **Login Screen**: Email/password and Google sign-in
3. **Register Screen**: Create new account with email

### Main App Flow
1. **Dashboard**: Overview and quick stats
2. **Upload Bill**: Camera capture and manual entry
3. **My Bills**: Complete bill management
4. **Analytics**: Charts and spending insights  
5. **Profile**: User settings and account management

## 🎨 Design System

### Colors
- **Primary**: #6366F1 (Indigo)
- **Secondary**: #10B981 (Emerald)
- **Success**: #10B981 (Emerald)
- **Warning**: #F59E0B (Amber)
- **Error**: #EF4444 (Red)
- **Info**: #3B82F6 (Blue)

### Typography
- **Font Family**: Inter
- **Weights**: Regular (400), Medium (500), SemiBold (600), Bold (700)

### Components
- **Material Design 3**: Latest Material Design components
- **Custom Widgets**: Reusable components for consistency
- **Responsive Design**: Adapts to different screen sizes

## 🔒 Security

- **Firebase Authentication**: Secure user authentication
- **Firestore Rules**: Database security rules
- **Storage Rules**: File upload security
- **Input Validation**: All forms have proper validation
- **Secure Storage**: Sensitive data handled securely

## 🧪 Testing

```bash
# Run unit tests
flutter test

# Run integration tests
flutter drive --target=test_driver/app.dart

# Run widget tests
flutter test test/widget_test.dart
```

## 📦 Dependencies

### Core Dependencies
- **flutter**: Flutter SDK
- **firebase_core**: Firebase core functionality
- **firebase_auth**: Authentication
- **cloud_firestore**: Database
- **firebase_storage**: File storage
- **google_sign_in**: Google OAuth

### UI Dependencies
- **material_color_utilities**: Material Design 3 colors
- **fl_chart**: Charts and analytics
- **cached_network_image**: Image caching
- **image_picker**: Camera and gallery access

### State Management
- **provider**: State management solution

### Utilities
- **intl**: Internationalization and date formatting
- **shared_preferences**: Local storage
- **path_provider**: File system paths

## 🚀 Deployment

### Android Deployment
1. **Build Release APK**
   ```bash
   flutter build apk --release
   ```

2. **Build App Bundle (for Play Store)**
   ```bash
   flutter build appbundle --release
   ```

### iOS Deployment
1. **Build for iOS**
   ```bash
   flutter build ios --release
   ```

2. **Archive in Xcode** for App Store submission

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Flutter best practices
- Use consistent naming conventions
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Configuration Issues**
   - Ensure `google-services.json` (Android) and `GoogleService-Info.plist` (iOS) are in the correct locations
   - Verify Firebase configuration in `lib/firebase_options.dart`

2. **Camera/Gallery Access Issues**
   - Check permissions in `AndroidManifest.xml`
   - Ensure camera permissions are granted on device

3. **Google Sign-In Issues**
   - Verify SHA-1 fingerprint in Firebase Console
   - Check Google Services configuration

4. **Build Issues**
   ```bash
   # Clean and rebuild
   flutter clean
   flutter pub get
   flutter run
   ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 📞 Contact

**Developer**: Mohammad Ayaz Alam  
**Email**: alam.ayaz47@gmail.com  
**Project Link**: [https://github.com/rebel47/Biller-V2](https://github.com/rebel47/Biller-V2)

## 🙏 Acknowledgments

- [Flutter Team](https://flutter.dev/) for the amazing framework
- [Firebase Team](https://firebase.google.com/) for backend services
- [Material Design](https://material.io/) for design guidelines
- [FL Chart](https://github.com/imaNNeo/fl_chart) for beautiful charts

---

**⭐ If you find this project helpful, please give it a star on GitHub!**

## 📝 Changelog

### Version 1.0.0
- Initial release with core features
- Authentication with Google Sign-In
- Bill upload with camera integration
- Analytics with interactive charts
- Material Design 3 implementation
- Firebase integration
- Responsive design

---

*Made with ❤️ and Flutter*