import 'package:cloud_firestore/cloud_firestore.dart';

class BillModel {
  final String id;
  final String username;
  final DateTime date;
  final String category;
  final double amount;
  final String description;
  final String? imageUrl;
  final DateTime createdAt;
  final DateTime updatedAt;

  BillModel({
    required this.id,
    required this.username,
    required this.date,
    required this.category,
    required this.amount,
    required this.description,
    this.imageUrl,
    required this.createdAt,
    required this.updatedAt,
  });

  // Create from Firestore document
  factory BillModel.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    
    return BillModel(
      id: doc.id,
      username: data['username'] ?? '',
      date: (data['date'] as Timestamp).toDate(),
      category: data['category'] ?? 'miscellaneous',
      amount: (data['amount'] ?? 0).toDouble(),
      description: data['description'] ?? '',
      imageUrl: data['imageUrl'],
      createdAt: (data['created_at'] as Timestamp).toDate(),
      updatedAt: (data['updated_at'] as Timestamp).toDate(),
    );
  }

  // Convert to Firestore document
  Map<String, dynamic> toFirestore() {
    return {
      'username': username,
      'date': Timestamp.fromDate(date),
      'category': category,
      'amount': amount,
      'description': description,
      'imageUrl': imageUrl,
      'created_at': Timestamp.fromDate(createdAt),
      'updated_at': Timestamp.fromDate(updatedAt),
    };
  }

  // Create a copy with updated fields
  BillModel copyWith({
    String? id,
    String? username,
    DateTime? date,
    String? category,
    double? amount,
    String? description,
    String? imageUrl,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return BillModel(
      id: id ?? this.id,
      username: username ?? this.username,
      date: date ?? this.date,
      category: category ?? this.category,
      amount: amount ?? this.amount,
      description: description ?? this.description,
      imageUrl: imageUrl ?? this.imageUrl,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'BillModel(id: $id, username: $username, date: $date, category: $category, amount: $amount, description: $description, imageUrl: $imageUrl)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is BillModel &&
      other.id == id &&
      other.username == username &&
      other.date == date &&
      other.category == category &&
      other.amount == amount &&
      other.description == description &&
      other.imageUrl == imageUrl;
  }

  @override
  int get hashCode {
    return id.hashCode ^
      username.hashCode ^
      date.hashCode ^
      category.hashCode ^
      amount.hashCode ^
      description.hashCode ^
      imageUrl.hashCode;
  }
}

// Categories for expenses
enum ExpenseCategory {
  grocery('grocery', 'Grocery', '🛒'),
  utensil('utensil', 'Utensil', '🍴'),
  clothing('clothing', 'Clothing', '👕'),
  transport('transport', 'Transport', '🚗'),
  entertainment('entertainment', 'Entertainment', '🎬'),
  medical('medical', 'Medical', '🏥'),
  education('education', 'Education', '📚'),
  miscellaneous('miscellaneous', 'Miscellaneous', '📦');

  const ExpenseCategory(this.value, this.displayName, this.icon);

  final String value;
  final String displayName;
  final String icon;

  static ExpenseCategory fromString(String value) {
    return ExpenseCategory.values.firstWhere(
      (category) => category.value == value,
      orElse: () => ExpenseCategory.miscellaneous,
    );
  }
}