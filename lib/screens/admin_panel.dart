import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AdminPanel extends StatefulWidget {
  const AdminPanel({super.key});

  @override
  State<AdminPanel> createState() => _AdminPanelState();
}

class _AdminPanelState extends State<AdminPanel> {
  final _auth = FirebaseAuth.instance;

  // CREATE ORDER controllers
  final _orderTitle = TextEditingController();
  final _orderTrade = TextEditingController();
  final _orderDescription = TextEditingController();
  final _orderPrice = TextEditingController();
  final _orderLocation = TextEditingController();
  bool _creatingOrder = false;

  // CREATE USER controllers
  final _userEmail = TextEditingController();
  final _userPassword = TextEditingController();
  final _userDisplayName = TextEditingController();
  final _userTrade = TextEditingController();
  String _userRole = 'worker';
  bool _creatingUser = false;

  // lists
  List<dynamic> _availableOrders = [];
  List<dynamic> _currentOrders = [];
  bool _loadingLists = false;

  String backendBase() {
    if (kIsWeb) return 'http://127.0.0.1:8000';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    if (Platform.isIOS) return 'http://127.0.0.1:8000';
    return 'http://127.0.0.1:8000';
  }

  @override
  void initState() {
    super.initState();
    _loadLists();
  }

  Future<String?> _idToken() async {
    final user = _auth.currentUser;
    if (user == null) return null;
    return await user.getIdToken();
  }

  Future<void> _loadLists() async {
    setState(() {
      _loadingLists = true;
    });
    try {
      final token = await _idToken();
      if (token == null) throw Exception('Brak tokena');
      final base = backendBase();

      final respAvail = await http.get(
        Uri.parse('$base/admin/orders/available'),
        headers: {'Authorization': 'Bearer $token'},
      );
      final respCurr = await http.get(
        Uri.parse('$base/admin/orders/current'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (respAvail.statusCode == 200) {
        _availableOrders = jsonDecode(respAvail.body) as List<dynamic>;
      } else {
        _availableOrders = [];
      }

      if (respCurr.statusCode == 200) {
        _currentOrders = jsonDecode(respCurr.body) as List<dynamic>;
      } else {
        _currentOrders = [];
      }
    } catch (e) {
      // ignore but show snackbar
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Błąd ładowania list: $e')));
    } finally {
      setState(() {
        _loadingLists = false;
      });
    }
  }

  Future<void> _createOrder() async {
    final title = _orderTitle.text.trim();
    final trade = _orderTrade.text.trim();
    if (title.isEmpty || trade.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Wpisz title i trade')));
      return;
    }
    setState(() => _creatingOrder = true);
    try {
      final token = await _idToken();
      final resp = await http.post(
        Uri.parse('${backendBase()}/admin/orders'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'title': title,
          'trade': trade,
          'description': _orderDescription.text.trim(),
          'price': _orderPrice.text.isEmpty
              ? null
              : double.tryParse(_orderPrice.text),
          'location': _orderLocation.text.trim(),
          'status': 'open',
        }),
      );
      if (resp.statusCode == 201) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Utworzono zlecenie')));
        _orderTitle.clear();
        _orderTrade.clear();
        _orderDescription.clear();
        _orderPrice.clear();
        _orderLocation.clear();
        await _loadLists();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Błąd: ${resp.statusCode} ${resp.body}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Błąd tworzenia zlecenia: $e')));
    } finally {
      setState(() => _creatingOrder = false);
    }
  }

  Future<void> _createUser() async {
    final email = _userEmail.text.trim();
    final password = _userPassword.text.trim();
    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Wpisz email i hasło')));
      return;
    }
    setState(() => _creatingUser = true);
    try {
      final token = await _idToken();
      final resp = await http.post(
        Uri.parse('${backendBase()}/admin/users'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
          'password': password,
          'displayName': _userDisplayName.text.trim(),
          'trade': _userTrade.text.trim(),
          'role': _userRole,
        }),
      );
      if (resp.statusCode == 201) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Utworzono użytkownika')));
        _userEmail.clear();
        _userPassword.clear();
        _userDisplayName.clear();
        _userTrade.clear();
        setState(() {
          _userRole = 'worker';
        });
        await _loadLists();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Błąd: ${resp.statusCode} ${resp.body}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Błąd tworzenia użytkownika: $e')));
    } finally {
      setState(() => _creatingUser = false);
    }
  }

  Future<void> _showReports(String orderId, String title) async {
    final token = await _idToken();
    if (token == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Brak tokena')));
      return;
    }

    final url = Uri.parse('${backendBase()}/admin/orders/$orderId/reports');
    List<dynamic> reports = [];
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );
    try {
      final resp = await http.get(
        url,
        headers: {'Authorization': 'Bearer $token'},
      );
      Navigator.of(context).pop(); // close loading
      if (resp.statusCode == 200) {
        reports = jsonDecode(resp.body) as List<dynamic>;
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Błąd ładowania raportów: ${resp.statusCode} ${resp.body}',
            ),
          ),
        );
        return;
      }
    } catch (e) {
      Navigator.of(context).pop(); // ensure loading closed
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Błąd: $e')));
      return;
    }

    if (reports.isEmpty) {
      showModalBottomSheet(
        context: context,
        builder: (_) => SizedBox(
          height: 200,
          child: Center(child: Text('Brak raportów dla "$title"')),
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        minChildSize: 0.3,
        maxChildSize: 0.95,
        builder: (_, controller) => Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              Text(
                'Raporty — $title',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Expanded(
                child: ListView.builder(
                  controller: controller,
                  itemCount: reports.length,
                  itemBuilder: (_, i) {
                    final r = reports[i];
                    final d = r['data'] as Map<String, dynamic>? ?? {};
                    final author = d['authorName'] ?? d['authorUid'] ?? '—';
                    final created = d['created_at'] ?? '';
                    final text = d['text'] ?? '';
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 6),
                      child: ListTile(
                        title: Text(author),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (created.toString().isNotEmpty)
                              Text(
                                created.toString(),
                                style: const TextStyle(fontSize: 12),
                              ),
                            const SizedBox(height: 6),
                            Text(text),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCreateOrderCard() {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            const Text(
              'Utwórz nowe zlecenie',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _orderTitle,
              decoration: const InputDecoration(labelText: 'Tytuł'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _orderTrade,
              decoration: const InputDecoration(labelText: 'Branża (trade)'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _orderDescription,
              decoration: const InputDecoration(labelText: 'Opis'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _orderPrice,
              decoration: const InputDecoration(labelText: 'Cena'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _orderLocation,
              decoration: const InputDecoration(labelText: 'Lokalizacja'),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _creatingOrder ? null : _createOrder,
                child: _creatingOrder
                    ? const SizedBox(
                        height: 16,
                        width: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('Utwórz zlecenie'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCreateUserCard() {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            const Text(
              'Utwórz użytkownika',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _userEmail,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _userPassword,
              decoration: const InputDecoration(labelText: 'Hasło'),
              obscureText: true,
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _userDisplayName,
              decoration: const InputDecoration(labelText: 'Imię i nazwisko'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _userTrade,
              decoration: const InputDecoration(labelText: 'Branża'),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Text('Rola: '),
                const SizedBox(width: 8),
                DropdownButton<String>(
                  value: _userRole,
                  items: const [
                    DropdownMenuItem(value: 'worker', child: Text('worker')),
                    DropdownMenuItem(value: 'admin', child: Text('admin')),
                  ],
                  onChanged: (v) => setState(() => _userRole = v ?? 'worker'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _creatingUser ? null : _createUser,
                child: _creatingUser
                    ? const SizedBox(
                        height: 16,
                        width: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('Utwórz użytkownika'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvailableList() {
    if (_loadingLists) return const Center(child: CircularProgressIndicator());
    if (_availableOrders.isEmpty)
      return const Center(child: Text('Brak dostępnych zleceń'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Dostępne zlecenia',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        for (var o in _availableOrders)
          Card(
            margin: const EdgeInsets.symmetric(vertical: 6),
            child: ListTile(
              title: Text(o['title'] ?? ''),
              subtitle: Text('${o['trade'] ?? ''} — ${o['location'] ?? ''}'),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(o['status'] ?? ''),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.article_outlined),
                    tooltip: 'Pokaż raporty',
                    onPressed: () => _showReports(
                      o['id'] ?? o['id'].toString(),
                      o['title'] ?? 'Zlecenie',
                    ),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildCurrentList() {
    if (_loadingLists) return const Center(child: CircularProgressIndicator());
    if (_currentOrders.isEmpty) return const Center(child: Text('Brak zadań'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Aktualne zlecenia',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        for (var o in _currentOrders)
          Card(
            margin: const EdgeInsets.symmetric(vertical: 6),
            child: ListTile(
              title: Text(o['title'] ?? ''),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Branża: ${o['trade'] ?? ''}  •  Lokalizacja: ${o['location'] ?? ''}',
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Przypisany: ${o['assignedUser'] != null ? (o['assignedUser']['displayName'] ?? o['assignedUser']['uid']) : '—'}',
                  ),
                ],
              ),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(o['status'] ?? ''),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.article_outlined),
                    tooltip: 'Pokaż raporty',
                    onPressed: () => _showReports(
                      o['id'] ?? o['id'].toString(),
                      o['title'] ?? 'Zlecenie',
                    ),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Panel administratora')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadLists,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                _buildCreateOrderCard(),
                _buildCreateUserCard(),
                const SizedBox(height: 8),
                _buildAvailableList(),
                const SizedBox(height: 12),
                _buildCurrentList(),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
