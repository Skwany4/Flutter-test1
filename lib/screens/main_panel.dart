import 'package:flutter/material.dart';

class MainPanel extends StatefulWidget {
  const MainPanel({super.key});

  @override
  State<MainPanel> createState() => _MainPanelState();
}

class _MainPanelState extends State<MainPanel> {
  // Tymczasowe dane - później zastąpisz danymi z bazy
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

  @override
  Widget build(BuildContext context) {
    const bg = Color(0xFF1F2A30);
    const panel = Color(0xFF2F3B42);
    const innerPanel = Color(0xFF222A2F);

    return Scaffold(
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

              // Nagłówek sekcji dla Dostępnych zleceń
              if (showAvailable)
                Align(
                  alignment: Alignment.centerLeft,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6.0),
                    child: Text(
                      'Dostępne Zlecenia',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.85),
                        fontSize: 16,
                      ),
                    ),
                  ),
                ),

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
    );
  }

  // Widok: Aktualne zlecenia (kafelki mają: Opis + Raport)
  Widget _buildCurrentList() {
    return ListView(
      children: [
        Center(
          child: Text(
            'Tutaj będą Twoje aktualne zlecenia',
            style: TextStyle(color: Colors.white.withOpacity(0.8)),
          ),
        ),
        const SizedBox(height: 12),
        for (var t in sampleTasks)
          TaskCard(
            title: t['title'] ?? '',
            termin: t['termin'] ?? '',
            adres: t['adres'] ?? '',
            onOpis: () =>
                _openOpisScreen(title: t['title'] ?? '', showSaveButton: false),
            onRight: () => _openReportScreen(title: t['title'] ?? ''),
            rightButtonLabel: 'Raport',
          ),
      ],
    );
  }

  // Widok: Dostępne zlecenia (kafelki mają: Opis + Zapisz się)
  Widget _buildAvailableList() {
    return ListView.builder(
      itemCount: sampleTasks.length,
      itemBuilder: (context, index) {
        final t = sampleTasks[index];
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: TaskCard(
            title: t['title'] ?? '',
            termin: t['termin'] ?? '',
            adres: t['adres'] ?? '',
            onOpis: () =>
                _openOpisScreen(title: t['title'] ?? '', showSaveButton: true),
            onRight: () => _showSnack('Zapisano chęć do zlecenia'),
            rightButtonLabel: 'Zapisz się',
          ),
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

    return Scaffold(
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
                              padding: const EdgeInsets.symmetric(vertical: 12),
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

    return Scaffold(
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
    );
  }
}

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
                    Expanded(child: Text(termin)),
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
                    Expanded(child: Text(adres)),
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
