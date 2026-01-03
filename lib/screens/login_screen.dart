import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'main_panel.dart';
import 'admin_panel.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  final AuthService _authService = AuthService();

  // Uniwersalna funkcja zwracająca poprawny adres backendu zależnie od platformy
  String backendBase() {
    // Web: używamy localhost (upewnij się, że serwer jest dostępny z przeglądarki)
    if (kIsWeb) return 'http://127.0.0.1:8000';
    // Android emulator (AVD) ma specjalny adres 10.0.2.2
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    // iOS simulator i desktop mogą używać localhost
    if (Platform.isIOS) return 'http://127.0.0.1:8000';
    // Fallback (np. Windows/macOS/Linux) - localhost
    return 'http://127.0.0.1:8000';
  }

  Future<void> _login() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Wpisz email i hasło")));
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final userCred = await _authService.signIn(
        _emailController.text.trim(),
        _passwordController.text.trim(),
      );

      final idToken = await userCred.user!.getIdToken();

      // Wywołanie backendu z poprawnym adresem zależnym od platformy
      final response = await http.get(
        Uri.parse('${backendBase()}/me'),
        headers: {'Authorization': 'Bearer $idToken'},
      );

      if (response.statusCode == 200) {
        // Parsujemy odpowiedź aby sprawdzić rolę i przekierować admina bezpośrednio
        try {
          final Map<String, dynamic> profile =
              jsonDecode(response.body) as Map<String, dynamic>;
          final role = (profile['role'] as String?) ?? 'worker';
          if (role == 'admin') {
            if (mounted) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const AdminPanel()),
              );
            }
            return;
          }
        } catch (_) {
          // jeśli parsowanie się nie uda, fallback do MainPanel
        }

        // Domyślnie przejdź do panelu użytkownika
        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const MainPanel()),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Błąd serwera: ${response.statusCode}")),
        );
      }
    } on FirebaseAuthException catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Błąd logowania: ${e.message}")));
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Błąd: $e")));
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // Usuń możliwość rejestracji w UI — konta będzie tworzył admin (później)
  // Jeśli masz w services/auth_service.register(), zostaw metodę w serwisie, ale nie udostępniaj jej w UI.

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color(0xff0d1b2a),
              Color(0xff1b263b),
              Color(0xff415a77),
              Color(0xff778da9),
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
                color: const Color(0xffe0e1dd).withOpacity(0.9),
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
                      color: Color(0xff0d1b2a),
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 30),
                  TextField(
                    controller: _emailController,
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
                      fillColor: const Color(0xff778da9).withOpacity(0.1),
                    ),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: _passwordController,
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
                      fillColor: const Color(0xff778da9).withOpacity(0.1),
                    ),
                  ),
                  const SizedBox(height: 30),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _login,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xff415a77),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
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
                              style: TextStyle(
                                fontSize: 18,
                                color: Colors.white,
                              ),
                            ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  // Usuń przycisk rejestracji — użytkownicy nie mogą sami tworzyć kont
                  TextButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Konta tworzy admin')),
                      );
                    },
                    child: const Text(
                      'Zapomniałem hasła',
                      style: TextStyle(color: Color(0xff1b263b)),
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
