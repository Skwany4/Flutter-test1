import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class AuthService {
  final _auth = FirebaseAuth.instance;
  final _firestore = FirebaseFirestore.instance;

  Future<UserCredential> signIn(String email, String password) =>
      _auth.signInWithEmailAndPassword(email: email, password: password);

  Future<UserCredential> register(
    String email,
    String password, {
    String? displayName,
    String? trade,
  }) async {
    final cred = await _auth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
    final uid = cred.user!.uid;
    await _firestore.collection('users').doc(uid).set({
      'email': email,
      'displayName': displayName ?? '',
      'role': 'worker', // domyślnie worker
      'trade': trade ?? '',
      'created_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
    return cred;
  }

  Future<String?> getIdToken() async {
    final user = _auth.currentUser;
    if (user == null) return null;
    return await user.getIdToken();
  }

  Future<DocumentSnapshot> getProfile() async {
    final user = _auth.currentUser!;
    return _firestore.collection('users').doc(user.uid).get();
  }

  Future<void> signOut() => _auth.signOut();
}
