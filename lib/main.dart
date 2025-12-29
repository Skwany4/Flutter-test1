import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'screens/login_screen.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Używamy wygenerowanego firebase_options.dart, dzięki temu inicjalizacja działa
  // poprawnie na web/Android/iOS (jeśli wygenerowane opcje są dostępne).
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: "Test",
      debugShowCheckedModeBanner: false,
      home: LoginScreen(),
    );
  }
}
