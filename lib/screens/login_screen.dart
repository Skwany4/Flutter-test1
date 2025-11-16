import 'package:flutter/material.dart';
import 'main_panel.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color(0xff0d1b2a), // ink-black
              Color(0xff1b263b), // prussian-blue
              Color(0xff415a77), // dusk-blue
              Color(0xff778da9), // dusty-denim
              //   Color(0xffe0e1dd), // alabaster-grey
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Container(
              padding: const EdgeInsets.all(30),
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: const Color(
                  0xffe0e1dd,
                ).withOpacity(0.9), // alabaster-grey
                borderRadius: BorderRadius.circular(25),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black26,
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(height: 20),
                  const Text(
                    "System zarządzania zleceniami",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xff0d1b2a), // ink-black
                    ),
                  ),
                  const SizedBox(height: 30),
                  TextField(
                    decoration: InputDecoration(
                      labelText: "Email",
                      prefixIcon: const Icon(
                        Icons.email,
                        color: Color(0xff1b263b),
                      ), // prussian-blue
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      filled: true,
                      fillColor: const Color(
                        0xff778da9,
                      ).withOpacity(0.1), // lekki odcień dusty-denim
                    ),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    obscureText: true,
                    decoration: InputDecoration(
                      labelText: "Hasło",
                      prefixIcon: const Icon(
                        Icons.lock,
                        color: Color(0xff1b263b),
                      ), // prussian-blue
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      filled: true,
                      fillColor: const Color(
                        0xff778da9,
                      ).withOpacity(0.1), // lekki odcień dusty-denim
                    ),
                  ),
                  const SizedBox(height: 30),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const MainPanel(),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xff415a77), // dusk-blue
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
                        elevation: 5,
                      ),
                      child: const Text(
                        "Zaloguj się",
                        style: TextStyle(fontSize: 18, color: Colors.white),
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  TextButton(
                    onPressed: () {},
                    child: const Text(
                      "Zapomniałem hasła",
                      style: TextStyle(
                        color: Color(0xff1b263b),
                      ), // prussian-blue
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
