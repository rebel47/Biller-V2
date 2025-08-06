import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/user_model.dart';

class AuthService extends ChangeNotifier {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  User? get currentUser => _auth.currentUser;
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  UserModel? _currentUserModel;
  UserModel? get currentUserModel => _currentUserModel;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  // Sign in with Google
  Future<UserModel?> signInWithGoogle() async {
    try {
      _setLoading(true);
      _clearError();

      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        _setLoading(false);
        return null; // User cancelled
      }

      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      final UserCredential userCredential =
          await _auth.signInWithCredential(credential);

      if (userCredential.user != null) {
        final userModel = await _createOrUpdateUser(userCredential.user!);
        _currentUserModel = userModel;
        _setLoading(false);
        return userModel;
      }

      _setLoading(false);
      return null;
    } catch (e) {
      _setError('Failed to sign in with Google: ${e.toString()}');
      _setLoading(false);
      return null;
    }
  }

  // Sign in with email and password
  Future<UserModel?> signInWithEmailAndPassword(
      String email, String password) async {
    try {
      _setLoading(true);
      _clearError();

      final UserCredential userCredential =
          await _auth.signInWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );

      if (userCredential.user != null) {
        final userModel = await _getUserModel(userCredential.user!.uid);
        _currentUserModel = userModel;
        _setLoading(false);
        return userModel;
      }

      _setLoading(false);
      return null;
    } on FirebaseAuthException catch (e) {
      String errorMessage;
      switch (e.code) {
        case 'user-not-found':
          errorMessage = 'No user found for that email.';
          break;
        case 'wrong-password':
          errorMessage = 'Wrong password provided.';
          break;
        case 'invalid-email':
          errorMessage = 'The email address is not valid.';
          break;
        case 'user-disabled':
          errorMessage = 'This user has been disabled.';
          break;
        default:
          errorMessage = 'An error occurred: ${e.message}';
      }
      _setError(errorMessage);
      _setLoading(false);
      return null;
    } catch (e) {
      _setError('An unexpected error occurred: ${e.toString()}');
      _setLoading(false);
      return null;
    }
  }

  // Create account with email and password
  Future<UserModel?> createUserWithEmailAndPassword(
    String email,
    String password,
    String name,
  ) async {
    try {
      _setLoading(true);
      _clearError();

      final UserCredential userCredential =
          await _auth.createUserWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );

      if (userCredential.user != null) {
        // Update display name
        await userCredential.user!.updateDisplayName(name);

        final userModel = await _createOrUpdateUser(userCredential.user!);
        _currentUserModel = userModel;
        _setLoading(false);
        return userModel;
      }

      _setLoading(false);
      return null;
    } on FirebaseAuthException catch (e) {
      String errorMessage;
      switch (e.code) {
        case 'weak-password':
          errorMessage = 'The password provided is too weak.';
          break;
        case 'email-already-in-use':
          errorMessage = 'The account already exists for that email.';
          break;
        case 'invalid-email':
          errorMessage = 'The email address is not valid.';
          break;
        default:
          errorMessage = 'An error occurred: ${e.message}';
      }
      _setError(errorMessage);
      _setLoading(false);
      return null;
    } catch (e) {
      _setError('An unexpected error occurred: ${e.toString()}');
      _setLoading(false);
      return null;
    }
  }

  // Sign out
  Future<void> signOut() async {
    try {
      _setLoading(true);
      await _googleSignIn.signOut();
      await _auth.signOut();
      _currentUserModel = null;
      _setLoading(false);
    } catch (e) {
      _setError('Failed to sign out: ${e.toString()}');
      _setLoading(false);
    }
  }

  // Create or update user in Firestore
  Future<UserModel> _createOrUpdateUser(User firebaseUser) async {
    final now = DateTime.now();
    final username = _generateUsername(firebaseUser.email ?? '');

    // Check if user already exists
    final existingUser = await _getUserModel(firebaseUser.uid);
    if (existingUser != null) {
      return existingUser;
    }

    // Create new user
    final userModel = UserModel(
      id: '', // Will be set when added to Firestore
      username: username,
      email: firebaseUser.email ?? '',
      name: firebaseUser.displayName ?? '',
      firebaseUid: firebaseUser.uid,
      photoUrl: firebaseUser.photoURL,
      createdAt: now,
      updatedAt: now,
    );

    // Add to Firestore
    final docRef = await _firestore.collection('users').add(userModel.toFirestore());
    
    return userModel.copyWith(id: docRef.id);
  }

  // Get user model from Firestore
  Future<UserModel?> _getUserModel(String firebaseUid) async {
    try {
      final querySnapshot = await _firestore
          .collection('users')
          .where('firebase_uid', isEqualTo: firebaseUid)
          .limit(1)
          .get();

      if (querySnapshot.docs.isNotEmpty) {
        return UserModel.fromFirestore(querySnapshot.docs.first);
      }
      return null;
    } catch (e) {
      debugPrint('Error getting user model: $e');
      return null;
    }
  }

  // Generate username from email
  String _generateUsername(String email) {
    final parts = email.split('@');
    if (parts.isNotEmpty) {
      return parts[0].toLowerCase().replaceAll(RegExp(r'[^a-zA-Z0-9]'), '');
    }
    return 'user${DateTime.now().millisecondsSinceEpoch}';
  }

  // Helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _errorMessage = error;
    notifyListeners();
  }

  void _clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Send password reset email
  Future<bool> sendPasswordResetEmail(String email) async {
    try {
      _setLoading(true);
      _clearError();

      await _auth.sendPasswordResetEmail(email: email.trim());
      _setLoading(false);
      return true;
    } on FirebaseAuthException catch (e) {
      String errorMessage;
      switch (e.code) {
        case 'user-not-found':
          errorMessage = 'No user found for that email.';
          break;
        case 'invalid-email':
          errorMessage = 'The email address is not valid.';
          break;
        default:
          errorMessage = 'An error occurred: ${e.message}';
      }
      _setError(errorMessage);
      _setLoading(false);
      return false;
    } catch (e) {
      _setError('An unexpected error occurred: ${e.toString()}');
      _setLoading(false);
      return false;
    }
  }
}