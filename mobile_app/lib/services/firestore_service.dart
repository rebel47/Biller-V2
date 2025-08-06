import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'dart:io';
import '../models/bill_model.dart';

class FirestoreService extends ChangeNotifier {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseStorage _storage = FirebaseStorage.instance;

  List<BillModel> _bills = [];
  List<BillModel> get bills => _bills;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  // Get bills for a specific user
  Stream<List<BillModel>> getBillsStream(String username) {
    return _firestore
        .collection('bills')
        .where('username', isEqualTo: username)
        .orderBy('date', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) => BillModel.fromFirestore(doc)).toList();
    });
  }

  // Get bills for current month
  Future<List<BillModel>> getBillsForMonth(
      String username, DateTime month) async {
    try {
      _setLoading(true);
      _clearError();

      final startOfMonth = DateTime(month.year, month.month, 1);
      final endOfMonth = DateTime(month.year, month.month + 1, 0, 23, 59, 59);

      final querySnapshot = await _firestore
          .collection('bills')
          .where('username', isEqualTo: username)
          .where('date',
              isGreaterThanOrEqualTo: Timestamp.fromDate(startOfMonth))
          .where('date', isLessThanOrEqualTo: Timestamp.fromDate(endOfMonth))
          .orderBy('date', descending: true)
          .get();

      final bills =
          querySnapshot.docs.map((doc) => BillModel.fromFirestore(doc)).toList();

      _setLoading(false);
      return bills;
    } catch (e) {
      _setError('Failed to get bills for month: ${e.toString()}');
      _setLoading(false);
      return [];
    }
  }

  // Add a new bill
  Future<BillModel?> addBill({
    required String username,
    required DateTime date,
    required String category,
    required double amount,
    required String description,
    File? imageFile,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      String? imageUrl;
      if (imageFile != null) {
        imageUrl = await _uploadImage(imageFile, username);
      }

      final now = DateTime.now();
      final bill = BillModel(
        id: '', // Will be set when added to Firestore
        username: username,
        date: date,
        category: category,
        amount: amount,
        description: description,
        imageUrl: imageUrl,
        createdAt: now,
        updatedAt: now,
      );

      final docRef = await _firestore.collection('bills').add(bill.toFirestore());
      final newBill = bill.copyWith(id: docRef.id);

      _setLoading(false);
      return newBill;
    } catch (e) {
      _setError('Failed to add bill: ${e.toString()}');
      _setLoading(false);
      return null;
    }
  }

  // Update a bill
  Future<BillModel?> updateBill(BillModel bill) async {
    try {
      _setLoading(true);
      _clearError();

      final updatedBill = bill.copyWith(updatedAt: DateTime.now());
      
      await _firestore
          .collection('bills')
          .doc(bill.id)
          .update(updatedBill.toFirestore());

      _setLoading(false);
      return updatedBill;
    } catch (e) {
      _setError('Failed to update bill: ${e.toString()}');
      _setLoading(false);
      return null;
    }
  }

  // Delete a bill
  Future<bool> deleteBill(String billId) async {
    try {
      _setLoading(true);
      _clearError();

      await _firestore.collection('bills').doc(billId).delete();

      _setLoading(false);
      return true;
    } catch (e) {
      _setError('Failed to delete bill: ${e.toString()}');
      _setLoading(false);
      return false;
    }
  }

  // Delete multiple bills
  Future<bool> deleteBills(List<String> billIds) async {
    try {
      _setLoading(true);
      _clearError();

      final batch = _firestore.batch();
      for (final billId in billIds) {
        batch.delete(_firestore.collection('bills').doc(billId));
      }

      await batch.commit();

      _setLoading(false);
      return true;
    } catch (e) {
      _setError('Failed to delete bills: ${e.toString()}');
      _setLoading(false);
      return false;
    }
  }

  // Get bills by category
  Future<List<BillModel>> getBillsByCategory(
      String username, String category) async {
    try {
      _setLoading(true);
      _clearError();

      final querySnapshot = await _firestore
          .collection('bills')
          .where('username', isEqualTo: username)
          .where('category', isEqualTo: category)
          .orderBy('date', descending: true)
          .get();

      final bills =
          querySnapshot.docs.map((doc) => BillModel.fromFirestore(doc)).toList();

      _setLoading(false);
      return bills;
    } catch (e) {
      _setError('Failed to get bills by category: ${e.toString()}');
      _setLoading(false);
      return [];
    }
  }

  // Get spending analytics
  Future<Map<String, dynamic>> getSpendingAnalytics(String username) async {
    try {
      _setLoading(true);
      _clearError();

      final now = DateTime.now();
      final startOfMonth = DateTime(now.year, now.month, 1);
      
      // Current month spending
      final currentMonthQuery = await _firestore
          .collection('bills')
          .where('username', isEqualTo: username)
          .where('date', isGreaterThanOrEqualTo: Timestamp.fromDate(startOfMonth))
          .get();

      double currentMonthTotal = 0;
      Map<String, double> categorySpending = {};
      
      for (final doc in currentMonthQuery.docs) {
        final bill = BillModel.fromFirestore(doc);
        currentMonthTotal += bill.amount;
        categorySpending[bill.category] = 
            (categorySpending[bill.category] ?? 0) + bill.amount;
      }

      // Last 6 months spending
      final sixMonthsAgo = DateTime(now.year, now.month - 5, 1);
      final monthlySpending = <String, double>{};
      
      for (int i = 0; i < 6; i++) {
        final month = DateTime(now.year, now.month - i, 1);
        final nextMonth = DateTime(month.year, month.month + 1, 0, 23, 59, 59);
        
        final monthQuery = await _firestore
            .collection('bills')
            .where('username', isEqualTo: username)
            .where('date', isGreaterThanOrEqualTo: Timestamp.fromDate(month))
            .where('date', isLessThanOrEqualTo: Timestamp.fromDate(nextMonth))
            .get();

        double monthTotal = 0;
        for (final doc in monthQuery.docs) {
          final bill = BillModel.fromFirestore(doc);
          monthTotal += bill.amount;
        }

        final monthKey = '${month.year}-${month.month.toString().padLeft(2, '0')}';
        monthlySpending[monthKey] = monthTotal;
      }

      _setLoading(false);
      
      return {
        'currentMonthTotal': currentMonthTotal,
        'categorySpending': categorySpending,
        'monthlySpending': monthlySpending,
      };
    } catch (e) {
      _setError('Failed to get spending analytics: ${e.toString()}');
      _setLoading(false);
      return {
        'currentMonthTotal': 0.0,
        'categorySpending': <String, double>{},
        'monthlySpending': <String, double>{},
      };
    }
  }

  // Upload image to Firebase Storage
  Future<String> _uploadImage(File imageFile, String username) async {
    try {
      final fileName = '${DateTime.now().millisecondsSinceEpoch}.jpg';
      final reference = _storage
          .ref()
          .child('bills')
          .child(username)
          .child(fileName);

      final uploadTask = reference.putFile(imageFile);
      final snapshot = await uploadTask;
      final downloadUrl = await snapshot.ref.getDownloadURL();

      return downloadUrl;
    } catch (e) {
      throw Exception('Failed to upload image: ${e.toString()}');
    }
  }

  // Search bills
  Future<List<BillModel>> searchBills(String username, String query) async {
    try {
      _setLoading(true);
      _clearError();

      final querySnapshot = await _firestore
          .collection('bills')
          .where('username', isEqualTo: username)
          .get();

      final bills = querySnapshot.docs
          .map((doc) => BillModel.fromFirestore(doc))
          .where((bill) =>
              bill.description.toLowerCase().contains(query.toLowerCase()) ||
              bill.category.toLowerCase().contains(query.toLowerCase()))
          .toList();

      bills.sort((a, b) => b.date.compareTo(a.date));

      _setLoading(false);
      return bills;
    } catch (e) {
      _setError('Failed to search bills: ${e.toString()}');
      _setLoading(false);
      return [];
    }
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
}