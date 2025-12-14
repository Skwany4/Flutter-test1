import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'main_panel.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // Kontrolery do pobierania tekstu
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  // Stan ładowania
  bool _isLoading = false;

  // ADRES IP (Dla Chrome/Windows ustaw 127.0.0.1, dla Emulatora 10.0.2.2)
  final String _baseUrl = 'http://127.0.0.1:8000';

  Future<void> _login() async {
    // 1. Walidacja wstępna
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Wpisz email i hasło")),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // 2. Wysłanie zapytania do Flaska
      final response = await http.post(
        Uri.parse('$_baseUrl/token'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': _emailController.text, // Backend oczekuje 'username'
          'password': _passwordController.text,
        },
      );

      if (response.statusCode == 200) {
        // 3. Sukces - Parsowanie tokena (opcjonalne zapisanie go)
        final data = jsonDecode(response.body);
        print("Token: ${data['access_token']}");

        if (mounted) {
          // Przejście do Panelu Głównego
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => const MainPanel(),
            ),
          );
        }
      } else {
        // Błąd logowania (np. złe hasło)
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text("Błędny login lub hasło"),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      // Błąd połączenia (np. serwer wyłączony)
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Błąd połączenia: $e"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // Funkcja pomocnicza do szybkiej rejestracji (podpięta pod Zapomniałem hasła dla testów)
  Future<void> _quickRegister() async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': _emailController.text,
          'password': _passwordController.text,
        }),
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Rejestracja: ${response.body}")),
        );
      }
    } catch (e) {
      print(e);
    }
  }

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
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black26,
                    blurRadius: 15,
                    offset: Offset(0, 5),
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
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 30),
                  // --- POLE EMAIL ---
                  TextField(
                    controller: _emailController, // Dodano kontroler
                    decoration: InputDecoration(
                      labelText: "Email",
                      prefixIcon: const Icon(
                        Icons.email,
                        color: Color(0xff1b263b),
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      filled: true,
                      fillColor: const Color(
                        0xff778da9,
                      ).withOpacity(0.1),
                    ),
                  ),
                  const SizedBox(height: 20),
                  // --- POLE HASŁO ---
                  TextField(
                    controller: _passwordController, // Dodano kontroler
                    obscureText: true,
                    decoration: InputDecoration(
                      labelText: "Hasło",
                      prefixIcon: const Icon(
                        Icons.lock,
                        color: Color(0xff1b263b),
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      filled: true,
                      fillColor: const Color(
                        0xff778da9,
                      ).withOpacity(0.1),
                    ),
                  ),
                  const SizedBox(height: 30),
                  // --- PRZYCISK LOGOWANIA ---
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _login, // Podpięta logika
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xff415a77), // dusk-blue
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
                        elevation: 5,
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              height: 24,
                              width: 24,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : const Text(
                              "Zaloguj się",
                              style: TextStyle(fontSize: 18, color: Colors.white),
                            ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  TextButton(
                    // Dla wygody testowania podpiąłem tu rejestrację
                    // Jeśli przytrzymasz przycisk - zarejestruje użytkownika
                    onPressed: () {}, 
                    child: const Text(
                      "Zapomniałem hasła",
                      style: TextStyle(
                        color: Color(0xff1b263b),
                        fontSize: 12,
                      ),
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