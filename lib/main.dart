import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/main_panel.dart';

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(title: "Test", home: LoginScreen());
  }
}
