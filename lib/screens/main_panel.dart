import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

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

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final user = _auth.currentUser;
    if (user == null) {
      setState(() {
        role = 'worker';
        trade = null;
        loadingProfile = false;
      });
      return;
    }
    try {
      final doc = await _firestore.collection('users').doc(user.uid).get();
      if (doc.exists) {
        final data = doc.data()!;
        setState(() {
          role = (data['role'] as String?) ?? 'worker';
          trade = (data['trade'] as String?) ?? null;
          loadingProfile = false;
        });
      } else {
        setState(() {
          role = 'worker';
          trade = null;
          loadingProfile = false;
        });
      }
    } catch (e) {
      // jeśli błąd - użyj domyślnych wartości
      setState(() {
        role = 'worker';
        trade = null;
        loadingProfile = false;
      });
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
                              const CircleAvatar(
                                radius: 26,
                                backgroundImage: AssetImage(
                                  'assets/avatar_placeholder.png',
                                ),
                                backgroundColor: Colors.grey,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      _auth.currentUser?.displayName ?? 'Imię',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      _auth.currentUser?.email ?? 'Nazwisko',
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
  // Pokazujemy zlecenia, gdzie current user jest właścicielem.
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
                showSaveButton: false,
              ),
              onRight: () => _openReportScreen(title: t['title'] ?? ''),
              rightButtonLabel: 'Raport',
            ),
        ],
      );
    }

    return StreamBuilder<QuerySnapshot>(
      stream: _firestore
          .collection('orders')
          .where('ownerUid', isEqualTo: currentUser.uid)
          .orderBy('created_at', descending: true)
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.hasError) return Text('Błąd: ${snapshot.error}');
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final docs = snapshot.data!.docs;
        if (docs.isEmpty) {
          // jeśli brak zleceń, pokazujemy sampleTasks jako fallback
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
                    showSaveButton: false,
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
            // termin/adres mapping - próbujemy pobrać pola termin/location lub created_at
            String termin = '';
            if (raw['termin'] != null) {
              termin = raw['termin'].toString();
            } else if (raw['created_at'] is Timestamp) {
              final ts = raw['created_at'] as Timestamp;
              termin = ts.toDate().toIso8601String().split('T').first;
            }
            final adres = raw['location'] as String? ?? '';
            return TaskCard(
              title: title,
              termin: termin,
              adres: adres,
              onOpis: () =>
                  _openOpisScreen(title: title, showSaveButton: false),
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
        if (docs.isEmpty)
          return const Center(child: Text('Brak dostępnych zleceń'));
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

            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: TaskCard(
                title: title,
                termin: termin,
                adres: adres,
                onOpis: () =>
                    _openOpisScreen(title: title, showSaveButton: true),
                onRight: () async {
                  final user = _auth.currentUser;
                  if (user == null) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Zaloguj się najpierw')),
                    );
                    return;
                  }
                  // przypisz siebie do zlecenia
                  await _firestore.collection('orders').doc(id).update({
                    'assignedTo': user.uid,
                    'status': 'assigned',
                    'updated_at': FieldValue.serverTimestamp(),
                  });
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Zapisano chęć do zlecenia')),
                  );
                },
                rightButtonLabel: 'Zapisz się',
              ),
            );
          },
        );
      },
    );
  }

  void _openOpisScreen({required String title, required bool showSaveButton}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            DescriptionScreen(title: title, showSaveButton: showSaveButton),
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
  final bool showSaveButton;

  const DescriptionScreen({
    super.key,
    required this.title,
    required this.showSaveButton,
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
                              const CircleAvatar(
                                radius: 22,
                                backgroundImage: AssetImage(
                                  'assets/avatar_placeholder.png',
                                ),
                                backgroundColor: Colors.grey,
                              ),
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
                        Container(
                          width: double.infinity,
                          height: 130,
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: darkBox,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'Opis',
                            style: TextStyle(color: Colors.white70),
                          ),
                        ),

                        const SizedBox(height: 12),

                        // Pole "Potrzebne narzędzia"
                        Container(
                          width: double.infinity,
                          height: 110,
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: darkBox,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'Potrzebne narzędzia',
                            style: TextStyle(color: Colors.white70),
                          ),
                        ),

                        const SizedBox(height: 18),

                        // Przycisk Zapisz się (pokazujemy tylko gdy trzeba)
                        if (showSaveButton)
                          SizedBox(
                            width: 160,
                            child: ElevatedButton(
                              onPressed: () {
                                // tutaj dodasz logikę zapisu do zlecenia
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Zapisano się')),
                                );
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
                              const CircleAvatar(
                                radius: 22,
                                backgroundImage: AssetImage(
                                  'assets/avatar_placeholder.png',
                                ),
                                backgroundColor: Colors.grey,
                              ),
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

                        // Pole raportu (w tym przykładzie TextField wieloliniowy)
                        Expanded(
                          child: Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: reportBox,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: TextField(
                              controller: _controller,
                              maxLines: null,
                              expands: true,
                              decoration: const InputDecoration.collapsed(
                                hintText: 'Wpisz treść raportu...',
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 12),

                        // Przycisk Wyślij raport
                        SizedBox(
                          width: 160,
                          child: ElevatedButton(
                            onPressed: _canSend
                                ? () {
                                    // tu w przyszłości wyślesz raport do backendu
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text('Wysłano raport'),
                                      ),
                                    );
                                    Navigator.pop(context);
                                  }
                                : null,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF3A4B53),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                            child: const Text('Wyślij raport'),
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

/// TaskCard (bez zmian, używane w całym pliku)
class TaskCard extends StatelessWidget {
  final String title;
  final String termin;
  final String adres;
  final VoidCallback onOpis;
  final VoidCallback onRight;
  final String rightButtonLabel;

  const TaskCard({
    super.key,
    required this.title,
    required this.termin,
    required this.adres,
    required this.onOpis,
    required this.onRight,
    this.rightButtonLabel = 'Zapisz się',
  });

  @override
  Widget build(BuildContext context) {
    const cardColor = Color(0xFF262E33);
    const innerColor = Color(0xFF1F2629);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          // Lewa: opis krótkie (tytuł, termin, adres)
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Colors.white, // upewniamy się, że tytuł jest biały
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(
                      width: 70,
                      child: Text(
                        'Termin',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        termin,
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(
                      width: 70,
                      child: Text(
                        'Adres',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        adres,
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(width: 12),

          // Prawa: kolumna przycisków (Opis + Raport/Zapisz się)
          Container(
            width: 110,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: innerColor,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Column(
              children: [
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: onOpis,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      backgroundColor: const Color(0xFF3A4B53),
                      textStyle: const TextStyle(fontSize: 14),
                    ),
                    child: const Text('Opis'),
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    onPressed: onRight,
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Colors.white24),
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      foregroundColor: Colors.white,
                    ),
                    child: Text(rightButtonLabel),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
