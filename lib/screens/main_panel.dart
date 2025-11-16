import 'package:flutter/material.dart';

class MainPanel extends StatelessWidget {
  const MainPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Główny panel")),
      body: const Center(
        child: Text(
          "Tutaj będzie główny panel użytkownika",
          style: TextStyle(fontSize: 18),
          textAlign: null,
        ),
      ),
    );
  }
}
