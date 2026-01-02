import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class MainPanel extends StatefulWidget {
  const MainPanel({super.key});

  @override
  State<MainPanel> createState() => _MainPanelState();
}

class _MainPanelState extends State<MainPanel> {
  // Tymczasowe dane - fallback jeśli brak połączenia / brak zleceń
  final List<Map<String, String>> sampleTasks = const [
    {
      'title': 'Tytuł zlecenia A',
      'termin': '2025-12-20',
      'adres': 'Ulica 1, Miasto',
    },
    {
      'title': 'Tytuł zlecenia B',
      'termin': '2025-12-21',
      'adres': 'Ulica 2, Miasto',
    },
    {
      'title': 'Tytuł zlecenia C',
      'termin': '2025-12-22',
      'adres': 'Ulica 3, Miasto',
    },
  ];

  // false = Aktualne zlecenia, true = Dostępne zlecenia
  bool showAvailable = false;

  // Firebase
  final _firestore = FirebaseFirestore.instance;
  final _auth = FirebaseAuth.instance;

  // profil użytkownika
  String? role;
  String? trade;
  bool loadingProfile = true;
  String displayNameFromProfile = 'Imię';

  // tracking assignments to avoid double clicks (per-item)
  final Set<String> _assigningIds = {};

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  String backendBase() {
    if (kIsWeb) return 'http://127.0.0.1:8000';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    if (Platform.isIOS) return 'http://127.0.0.1:8000';
    return 'http://127.0.0.1:8000';
  }

  Future<void> _load_profile_updateRoleFallback() async {
    // kept for potential future adjustments
  }

  Future<void> _loadProfile() async {
    final user = _auth.currentUser;
    if (user == null) {
      setState(() {
        role = 'worker';
        trade = null;
        displayNameFromProfile = 'Imię';
        loadingProfile = false;
      });
      return;
    }
    try {
      final doc = await _firestore.collection('users').doc(user.uid).get();
      if (doc.exists) {
        final data = doc.data()!;
        setState(() {
          // only two roles in DB: 'admin' and 'worker' (fallback to 'worker')
          role = (data['role'] as String?) == 'admin' ? 'admin' : 'worker';
          trade = (data['trade'] as String?) ?? null;
          displayNameFromProfile =
              (data['displayName'] as String?) ?? user.displayName ?? 'Imię';
          loadingProfile = false;
        });
      } else {
        setState(() {
          role = 'worker';
          trade = null;
          displayNameFromProfile = user.displayName ?? 'Imię';
          loadingProfile = false;
        });
      }
    } catch (e) {
      // jeśli błąd - użyj domyślnych wartości
      setState(() {
        role = 'worker';
        trade = null;
        displayNameFromProfile = _auth.currentUser?.displayName ?? 'Imię';
        loadingProfile = false;
      });
    }
  }

  Future<void> assignOrderViaBackend(String orderId) async {
    if (_assigningIds.contains(orderId)) return;
    final user = _auth.currentUser;
    if (user == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Zaloguj się najpierw')),
      );
      return;
    }

    _assigningIds.add(orderId);
    setState(() {}); // to refresh UI for button disabling

    try {
      final idToken = await user.getIdToken();
      final url = Uri.parse('${backendBase()}/orders/$orderId/assign');

      final resp = await http.post(
        url,
        headers: {
          'Authorization': 'Bearer $idToken',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({}), // worker assigns themself -> empty body is fine
      );

      if (resp.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Pomyślnie zapisano do zlecenia')),
        );
      } else if (resp.statusCode == 403) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Brak uprawnień: ${resp.body}')),
        );
      } else if (resp.statusCode == 404) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Zlecenie nie istnieje: ${resp.body}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Błąd serwera: ${resp.statusCode} ${resp.body}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Błąd przy zapisie: $e')),
      );
    } finally {
      _assigningIds.remove(orderId);
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    const bg = Color(0xFF1F2A30);
    const panel = Color(0xFF2F3B42);
    const innerPanel = Color(0xFF222A2F);

    // Lokalny Theme tylko dla drzewa tego ekranu:
    final localTheme = Theme.of(context).copyWith(
      textTheme: Theme.of(
        context,
      ).textTheme.apply(bodyColor: Colors.white, displayColor: Colors.white),
      primaryTextTheme: Theme.of(context).primaryTextTheme.apply(
        bodyColor: Colors.white,
        displayColor: Colors.white,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: panel,
        foregroundColor: Colors.white,
        iconTheme: IconThemeData(color: Colors.white),
        titleTextStyle: TextStyle(color: Colors.white, fontSize: 20),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          foregroundColor: Colors.white, // tekst przycisków na biało
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(foregroundColor: Colors.white),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        hintStyle: TextStyle(color: Colors.white70),
        labelStyle: TextStyle(color: Colors.white70),
      ),
    );

    // Jeśli profil się jeszcze ładuje - pokaz loader
    if (loadingProfile) {
      return Theme(
        data: localTheme,
        child: const Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }

    return Theme(
      data: localTheme,
      child: Scaffold(
        backgroundColor: bg,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              children: [
                // Nagłówek z profilem i przyciskami widoku
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: panel,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      // Profil użytkownika (lewa część)
                      Expanded(
                        flex: 3,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            vertical: 12,
                            horizontal: 12,
                          ),
                          decoration: BoxDecoration(
                            color: innerPanel,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              // Use initials avatar here
                              InitialsAvatar(
                                name: displayNameFromProfile,
                                radius: 26,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      displayNameFromProfile,
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      _auth.currentUser?.email ??
                                          'email@domena',
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Zawód: ${trade ?? 'nie ustawiono'}',
                                      style: const TextStyle(
                                        color: Colors.white70,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(width: 12),

                      // Przyciski: Aktualne / Dostępne
                      Expanded(
                        flex: 1,
                        child: Column(
                          children: [
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () {
                                  setState(() {
                                    showAvailable = false;
                                  });
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: showAvailable
                                      ? const Color(0xFF2B3740)
                                      : const Color(0xFF3A4B53),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 12,
                                    horizontal: 8,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Aktualne zlecenia'),
                              ),
                            ),
                            const SizedBox(height: 8),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () {
                                  setState(() {
                                    showAvailable = true;
                                  });
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: showAvailable
                                      ? const Color(0xFF3A4B53)
                                      : const Color(0xFF2B3740),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 12,
                                    horizontal: 8,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Dostępne zlecenia'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 14),

                // Główna sekcja z listą zleceń
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: panel,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: showAvailable
                          ? _buildAvailableList()
                          : _buildCurrentList(),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Widok: Aktualne zlecenia (kafelki mają: Opis + Raport)
  // Zmodyfikowane: tylko dwie role w systemie: 'admin' i 'worker'.
  // - admin: widzi wszystkie zlecenia
  // - worker: widzi tylko zlecenia, do których jest przypisany (assignedTo == jego uid)
  Widget _buildCurrentList() {
    final currentUser = _auth.currentUser;
    if (currentUser == null) {
      // fallback: pokaż sampleTasks
      return ListView(
        children: [
          const SizedBox(height: 12),
          for (var t in sampleTasks)
            TaskCard(
              title: t['title'] ?? '',
              termin: t['termin'] ?? '',
              adres: t['adres'] ?? '',
              onOpis: () => _openOpisScreen(
                title: t['title'] ?? '',
                description: '',
                tools: const [],
                showSaveButton: false,
                orderId: null,
              ),
              onRight: () => _openReportScreen(title: t['title'] ?? ''),
              rightButtonLabel: 'Raport',
            ),
        ],
      );
    }

    // Admin: pokazujemy wszystkie zlecenia realtime
    if (role == 'admin') {
      return StreamBuilder<QuerySnapshot>(
        stream: _firestore
            .collection('orders')
            .orderBy('created_at', descending: true)
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.hasError) return Text('Błąd: ${snapshot.error}');
          if (snapshot.connectionState == ConnectionState.waiting)
            return const Center(child: CircularProgressIndicator());
          final docs = snapshot.data!.docs;
          if (docs.isEmpty) {
            return ListView(
              children: [
                const SizedBox(height: 12),
                for (var t in sampleTasks)
                  TaskCard(
                    title: t['title'] ?? '',
                    termin: t['termin'] ?? '',
                    adres: t['adres'] ?? '',
                    onOpis: () => _openOpisScreen(
                      title: t['title'] ?? '',
                      description: '',
                      tools: const [],
                      showSaveButton: false,
                      orderId: null,
                    ),
                    onRight: () => _openReportScreen(title: t['title'] ?? ''),
                    rightButtonLabel: 'Raport',
                  ),
              ],
            );
          }
          return ListView.builder(
            itemCount: docs.length,
            itemBuilder: (context, i) {
              final raw = docs[i].data() as Map<String, dynamic>;
              final title = raw['title'] as String? ?? '';
              String termin = '';
              if (raw['termin'] != null) {
                termin = raw['termin'].toString();
              } else if (raw['created_at'] is Timestamp) {
                final ts = raw['created_at'] as Timestamp;
                termin = ts.toDate().toIso8601String().split('T').first;
              }
              final adres = raw['location'] as String? ?? '';
              final description = raw['description'] as String? ?? '';
              final tools = (raw['tools'] as List<dynamic>?)
                      ?.map((e) => e.toString())
                      .toList() ??
                  <String>[];

              return TaskCard(
                title: title,
                termin: termin,
                adres: adres,
                onOpis: () => _openOpisScreen(
                  title: title,
                  description: description,
                  tools: tools,
                  showSaveButton: false,
                  orderId: docs[i].id,
                ),
                onRight: () => _openReportScreen(title: title),
                rightButtonLabel: 'Raport',
              );
            },
          );
        },
      );
    }

    // Worker: pokaż tylko zlecenia przypisane do zalogowanego użytkownika (assignedTo == uid)
    return StreamBuilder<QuerySnapshot>(
      stream: _firestore
          .collection('orders')
          .where('assignedTo', isEqualTo: currentUser.uid)
          .orderBy('created_at', descending: true)
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.hasError) return Text('Błąd: ${snapshot.error}');
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final docs = snapshot.data!.docs;
        if (docs.isEmpty) {
          return const Center(
            child: Text('Brak aktualnych zleceń przypisanych do Ciebie'),
          );
        }
        return ListView.builder(
          itemCount: docs.length,
          itemBuilder: (context, i) {
            final raw = docs[i].data() as Map<String, dynamic>;
            final title = raw['title'] as String? ?? '';
            String termin = '';
            if (raw['termin'] != null) {
              termin = raw['termin'].toString();
            } else if (raw['created_at'] is Timestamp) {
              final ts = raw['created_at'] as Timestamp;
              termin = ts.toDate().toIso8601String().split('T').first;
            }
            final adres = raw['location'] as String? ?? '';
            final description = raw['description'] as String? ?? '';
            final tools = (raw['tools'] as List<dynamic>?)
                    ?.map((e) => e.toString())
                    .toList() ??
                <String>[];

            return TaskCard(
              title: title,
              termin: termin,
              adres: adres,
              onOpis: () => _openOpisScreen(
                title: title,
                description: description,
                tools: tools,
                showSaveButton: false,
                orderId: docs[i].id,
              ),
              onRight: () => _openReportScreen(title: title),
              rightButtonLabel: 'Raport',
            );
          },
        );
      },
    );
  }

  // Widok: Dostępne zlecenia (kafelki mają: Opis + Zapisz się)
  // Pokazujemy zlecenia o status 'open' i trade == user.trade
  Widget _buildAvailableList() {
    if (trade == null || trade!.isEmpty) {
      return const Center(
        child: Text('Nie ustawiono branży. Skontaktuj się z administratorem.'),
      );
    }

    return StreamBuilder<QuerySnapshot>(
      stream: _firestore
          .collection('orders')
          .where('status', isEqualTo: 'open')
          .where('trade', isEqualTo: trade)
          .orderBy('created_at', descending: true)
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.hasError) return Text('Błąd: ${snapshot.error}');
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final docs = snapshot.data!.docs;
        if (docs.isEmpty) return const Center(child: Text('Brak dostępnych zleceń'));
        return ListView.builder(
          itemCount: docs.length,
          itemBuilder: (context, index) {
            final raw = docs[index].data() as Map<String, dynamic>;
            final id = docs[index].id;
            final title = raw['title'] as String? ?? '';
            String termin = '';
            if (raw['termin'] != null) {
              termin = raw['termin'].toString();
            } else if (raw['created_at'] is Timestamp) {
              final ts = raw['created_at'] as Timestamp;
              termin = ts.toDate().toIso8601String().split('T').first;
            }
            final adres = raw['location'] as String? ?? '';
            final description = raw['description'] as String? ?? '';
            final tools = (raw['tools'] as List<dynamic>?)
                    ?.map((e) => e.toString())
                    .toList() ??
                <String>[];

            final isAssigning = _assigningIds.contains(id);

            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: TaskCard(
                title: title,
                termin: termin,
                adres: adres,
                onOpis: () => _openOpisScreen(
                  title: title,
                  description: description,
                  tools: tools,
                  showSaveButton: true,
                  orderId: id,
                ),
                onRight: () async {
                  // wywołujemy backendowy endpoint, żeby uniknąć ograniczeń reguł Firestore
                  await assignOrderViaBackend(id);
                },
                rightButtonLabel: 'Zapisz się',
                isLoading: isAssigning,
              ),
            );
          },
        );
      },
    );
  }

  void _openOpisScreen({
    required String title,
    required String description,
    required List<String> tools,
    required bool showSaveButton,
    required String? orderId,
  }) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DescriptionScreen(
          title: title,
          description: description,
          tools: tools,
          showSaveButton: showSaveButton,
          onSave: orderId == null
              ? null
              : () async {
                  Navigator.of(context).pop(); // zamknij szczegóły przed przypisaniem
                  await assignOrderViaBackend(orderId);
                },
        ),
      ),
    );
  }

  void _openReportScreen({required String title}) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => ReportScreen(title: title)),
    );
  }

  void _showSnack(String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }
}

/// Ekran z opisem zlecenia (pokazywany po kliknięciu "Opis")
class DescriptionScreen extends StatelessWidget {
  final String title;
  final String description;
  final List<String> tools;
  final bool showSaveButton;
  final Future<void> Function()? onSave;

  const DescriptionScreen({
    super.key,
    required this.title,
    required this.description,
    required this.tools,
    required this.showSaveButton,
    this.onSave,
  });

  @override
  Widget build(BuildContext context) {
    const bg = Color(0xFF1F2A30);
    const panel = Color(0xFF2F3B42);
    const innerPanel = Color(0xFF222A2F);
    const darkBox = Color(0xFF16191C);

    // Lokalny Theme dla tego ekranu opisu
    final localTheme = Theme.of(context).copyWith(
      textTheme: Theme.of(
        context,
      ).textTheme.apply(bodyColor: Colors.white, displayColor: Colors.white),
      appBarTheme: const AppBarTheme(
        backgroundColor: panel,
        foregroundColor: Colors.white,
        iconTheme: IconThemeData(color: Colors.white),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        hintStyle: TextStyle(color: Colors.white70),
        labelStyle: TextStyle(color: Colors.white70),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(foregroundColor: Colors.white),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(foregroundColor: Colors.white),
      ),
    );

    final name = FirebaseAuth.instance.currentUser?.displayName ?? '';

    return Theme(
      data: localTheme,
      child: Scaffold(
        backgroundColor: bg,
        appBar: AppBar(
          title: const Text('Opis zlecenia'),
          backgroundColor: panel,
          elevation: 0,
        ),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              children: [
                // Górna karta z profilem i przyciskami (tak jak w widoku głównym)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: panel,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            vertical: 12,
                            horizontal: 12,
                          ),
                          decoration: BoxDecoration(
                            color: innerPanel,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              InitialsAvatar(name: name, radius: 22),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: const [
                                    Text(
                                      'Imię',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    SizedBox(height: 4),
                                    Text('Nazwisko'),
                                    SizedBox(height: 4),
                                    Text(
                                      'Zawód',
                                      style: TextStyle(
                                        color: Colors.white70,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      // przyciski informacyjne - tylko wizualnie
                      Expanded(
                        flex: 1,
                        child: Column(
                          children: [
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: null,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF3A4B53),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 12,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Aktualne zlecenia'),
                              ),
                            ),
                            const SizedBox(height: 8),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: null,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF2B3740),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 12,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Dostępne zlecenia'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 14),

                // Główna karta opisu
                Expanded(
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: panel,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title.isNotEmpty ? title : 'Zlecenie',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Pole "Opis"
                        Expanded(
                          child: Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: darkBox,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: SingleChildScrollView(
                              child: Text(
                                description.isNotEmpty ? description : 'Brak opisu',
                                style: const TextStyle(color: Colors.white70),
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 12),

                        // Pole "Potrzebne narzędzia"
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: darkBox,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: tools.isEmpty
                              ? const Text('Brak narzędzi', style: TextStyle(color: Colors.white70))
                              : Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: tools
                                      .map((t) => Padding(
                                            padding: const EdgeInsets.symmetric(vertical: 2),
                                            child: Text('• $t', style: const TextStyle(color: Colors.white70)),
                                          ))
                                      .toList(),
                                ),
                        ),

                        const SizedBox(height: 18),

                        // Przycisk Zapisz się (pokazujemy tylko gdy trzeba)
                        if (showSaveButton)
                          SizedBox(
                            width: 160,
                            child: ElevatedButton(
                              onPressed: onSave == null
                                  ? null
                                  : () async {
                                      // wywołaj przekazaną funkcję, która przypisze zlecenie
                                      await onSave!();
                                    },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF3A4B53),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                padding: const EdgeInsets.symmetric(
                                  vertical: 12,
                                ),
                              ),
                              child: const Text('Zapisz się'),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Ekran raportu (pokazywany po kliknięciu "Raport")
class ReportScreen extends StatefulWidget {
  final String title;

  const ReportScreen({super.key, required this.title});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  final TextEditingController _controller = TextEditingController();

  bool get _canSend => _controller.text.trim().isNotEmpty;

  @override
  void initState() {
    super.initState();
    _controller.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const bg = Color(0xFF1F2A30);
    const panel = Color(0xFF2F3B42);
    const innerPanel = Color(0xFF222A2F);
    const reportBox = Color(0xFFD9D9D9); // jasny box imitujący pole raportu

    final localTheme = Theme.of(context).copyWith(
      textTheme: Theme.of(
        context,
      ).textTheme.apply(bodyColor: Colors.white, displayColor: Colors.white),
      appBarTheme: const AppBarTheme(
        backgroundColor: panel,
        foregroundColor: Colors.white,
        iconTheme: IconThemeData(color: Colors.white),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        hintStyle: TextStyle(color: Colors.black54),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(foregroundColor: Colors.white),
      ),
    );

    final name = FirebaseAuth.instance.currentUser?.displayName ?? '';

    return Theme(
      data: localTheme,
      child: Scaffold(
        backgroundColor: bg,
        appBar: AppBar(
          title: Text('Raport - ${widget.title}'),
          backgroundColor: panel,
          elevation: 0,
        ),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              children: [
                // Górna karta z profilem i przyciskami (wizualnie)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: panel,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            vertical: 12,
                            horizontal: 12,
                          ),
                          decoration: BoxDecoration(
                            color: innerPanel,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              InitialsAvatar(name: name, radius: 22),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: const [
                                    Text(
                                      'Imię',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    SizedBox(height: 4),
                                    Text('Nazwisko'),
                                    SizedBox(height: 4),
                                    Text(
                                      'Zawód',
                                      style: TextStyle(
                                        color: Colors.white70,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      // przyciski informacyjne - tylko wizualnie
                      Expanded(
                        flex: 1,
                        child: Column(
                          children: [
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: null,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF3A4B53),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 12,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Aktualne zlecenia'),
                              ),
                            ),
                            const SizedBox(height: 8),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: null,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF2B3740),
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 12,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Dostępne zlecenia'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 14),

                // Główna karta raportu
                Expanded(
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: panel,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Column(
                      children: [
                        Text(
                          widget.title.isNotEmpty ? widget.title : 'Zlecenie',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Container(
                          width: double.infinity,
                          height: 220,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: reportBox,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: TextField(
                            controller: _controller,
                            maxLines: null,
                            decoration: const InputDecoration.collapsed(
                              hintText: 'Wpisz raport...',
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            TextButton(
                              onPressed: () {
                                Navigator.pop(context);
                              },
                              child: const Text('Anuluj'),
                            ),
                            ElevatedButton(
                              onPressed: _canSend
                                  ? () {
                                      // tutaj możesz zapisać raport do Firestore lub wysłać go gdzieś
                                      ScaffoldMessenger.of(
                                        context,
                                      ).showSnackBar(
                                        const SnackBar(
                                          content: Text('Wysłano raport'),
                                        ),
                                      );
                                      Navigator.pop(context);
                                    }
                                  : null,
                              child: const Text('Wyślij'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Prosty widget kafelka zlecenia (rekreacja z oryginalnego projektu)
class TaskCard extends StatelessWidget {
  final String title;
  final String termin;
  final String adres;
  final VoidCallback onOpis;
  final VoidCallback onRight;
  final String rightButtonLabel;
  final bool isLoading;

  const TaskCard({
    super.key,
    required this.title,
    required this.termin,
    required this.adres,
    required this.onOpis,
    required this.onRight,
    required this.rightButtonLabel,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    const cardColor = Color(0xFF2B3740);
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 6),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Expanded(
            child: InkWell(
              onTap: onOpis,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Text('Termin: $termin', style: const TextStyle(fontSize: 12)),
                  const SizedBox(height: 4),
                  Text('Adres: $adres', style: const TextStyle(fontSize: 12)),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: isLoading ? null : onRight,
            child: isLoading
                ? const SizedBox(
                    height: 16,
                    width: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : Text(rightButtonLabel),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3A4B53),
            ),
          ),
        ],
      ),
    );
  }
}

/// Widget generujący awatar z inicjałami (deterministyczny kolor na podstawie imienia)
class InitialsAvatar extends StatelessWidget {
  final String name;
  final double radius;

  const InitialsAvatar({
    super.key,
    required this.name,
    this.radius = 20,
  });

  String _getInitials(String input) {
    final trimmed = input.trim();
    if (trimmed.isEmpty) return '?';
    final parts = trimmed.split(RegExp(r'\s+'));
    if (parts.length == 1) {
      final p = parts[0];
      if (p.length >= 2) return p.substring(0, 2).toUpperCase();
      return p.substring(0, 1).toUpperCase();
    } else {
      final a = parts[0].isNotEmpty ? parts[0][0] : '';
      final b = parts[1].isNotEmpty ? parts[1][0] : '';
      return (a + b).toUpperCase();
    }
  }

  Color _backgroundFromName(String input) {
    final hash = input.hashCode;
    final index = hash.abs() % Colors.primaries.length;
    return Colors.primaries[index].shade700;
  }

  @override
  Widget build(BuildContext context) {
    final initials = _getInitials(name.isNotEmpty ? name : (FirebaseAuth.instance.currentUser?.email ?? '?'));
    final bg = _backgroundFromName(name.isNotEmpty ? name : (FirebaseAuth.instance.currentUser?.email ?? '?'));

    return CircleAvatar(
      radius: radius,
      backgroundColor: bg,
      child: Text(
        initials,
        style: TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: radius * 0.6,
        ),
      ),
    );
  }
}