import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:enersense/theme.dart';
import 'package:enersense/services/api_service.dart';
import 'package:enersense/providers/energy_provider.dart';
import 'package:enersense/providers/chat_provider.dart';
import 'package:enersense/providers/insights_provider.dart';
import 'package:enersense/providers/savings_provider.dart';
import 'package:enersense/providers/profile_provider.dart';
import 'package:enersense/screens/home_screen.dart';
import 'package:enersense/screens/chat_screen.dart';
import 'package:enersense/screens/insights_screen.dart';
import 'package:enersense/screens/savings_screen.dart';
import 'package:enersense/screens/profile_screen.dart';
import 'package:enersense/widgets/bottom_nav_bar.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EnerSense AI',
      theme: AppTheme.lightTheme(),
      home: MultiProvider(
        providers: [
          // API Service
          Provider<ApiService>(create: (_) => ApiService()),
          // Energy Provider
          ChangeNotifierProxyProvider<ApiService, EnergyProvider>(
            create: (context) => EnergyProvider(
              apiService: context.read<ApiService>(),
            ),
            update: (context, apiService, previous) =>
                previous ?? EnergyProvider(apiService: apiService),
          ),
          // Chat Provider
          ChangeNotifierProxyProvider<ApiService, ChatProvider>(
            create: (context) => ChatProvider(
              apiService: context.read<ApiService>(),
            ),
            update: (context, apiService, previous) =>
                previous ?? ChatProvider(apiService: apiService),
          ),
          // Insights Provider
          ChangeNotifierProxyProvider<ApiService, InsightsProvider>(
            create: (context) => InsightsProvider(
              apiService: context.read<ApiService>(),
            ),
            update: (context, apiService, previous) =>
                previous ?? InsightsProvider(apiService: apiService),
          ),
          // Savings Provider
          ChangeNotifierProxyProvider<ApiService, SavingsProvider>(
            create: (context) => SavingsProvider(
              apiService: context.read<ApiService>(),
            ),
            update: (context, apiService, previous) =>
                previous ?? SavingsProvider(apiService: apiService),
          ),
          // Profile Provider
          ChangeNotifierProvider<ProfileProvider>(
            create: (_) => ProfileProvider(),
          ),
        ],
        child: const MainApp(),
      ),
    );
  }
}

class MainApp extends StatefulWidget {
  const MainApp({super.key});

  @override
  State<MainApp> createState() => _MainAppState();
}

class _MainAppState extends State<MainApp> {
  int _selectedIndex = 0;

  late List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _screens = [
      HomeScreen(),
      ChatScreen(),
      InsightsScreen(),
      SavingsScreen(),
      ProfileScreen(),
    ];
  }

  void _onNavBarTap(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavBar(
        currentIndex: _selectedIndex,
        onTap: _onNavBarTap,
      ),
    );
  }
}
