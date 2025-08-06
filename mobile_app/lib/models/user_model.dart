import 'package:cloud_firestore/cloud_firestore.dart';

class UserModel {
  final String id;
  final String username;
  final String email;
  final String name;
  final String firebaseUid;
  final String? photoUrl;
  final DateTime createdAt;
  final DateTime updatedAt;

  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.name,
    required this.firebaseUid,
    this.photoUrl,
    required this.createdAt,
    required this.updatedAt,
  });

  // Create from Firestore document
  factory UserModel.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    
    return UserModel(
      id: doc.id,
      username: data['username'] ?? '',
      email: data['email'] ?? '',
      name: data['name'] ?? '',
      firebaseUid: data['firebase_uid'] ?? '',
      photoUrl: data['photoUrl'],
      createdAt: (data['created_at'] as Timestamp).toDate(),
      updatedAt: (data['updated_at'] as Timestamp).toDate(),
    );
  }

  // Convert to Firestore document
  Map<String, dynamic> toFirestore() {
    return {
      'username': username,
      'email': email,
      'name': name,
      'firebase_uid': firebaseUid,
      'photoUrl': photoUrl,
      'created_at': Timestamp.fromDate(createdAt),
      'updated_at': Timestamp.fromDate(updatedAt),
    };
  }

  // Create a copy with updated fields
  UserModel copyWith({
    String? id,
    String? username,
    String? email,
    String? name,
    String? firebaseUid,
    String? photoUrl,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      name: name ?? this.name,
      firebaseUid: firebaseUid ?? this.firebaseUid,
      photoUrl: photoUrl ?? this.photoUrl,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'UserModel(id: $id, username: $username, email: $email, name: $name, firebaseUid: $firebaseUid)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is UserModel &&
      other.id == id &&
      other.username == username &&
      other.email == email &&
      other.name == name &&
      other.firebaseUid == firebaseUid &&
      other.photoUrl == photoUrl;
  }

  @override
  int get hashCode {
    return id.hashCode ^
      username.hashCode ^
      email.hashCode ^
      name.hashCode ^
      firebaseUid.hashCode ^
      photoUrl.hashCode;
  }
}