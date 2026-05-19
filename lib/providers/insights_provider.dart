import 'package:flutter/material.dart';
import 'package:enersense/models/appliance_usage.dart';
import 'package:enersense/models/behavior_pattern.dart';
import 'package:enersense/services/api_service.dart';

class InsightsProvider extends ChangeNotifier {
  final ApiService apiService;
  List<ApplianceUsage> _appliances = [];
  List<BehaviorPattern> _behaviorPatterns = [];
  List<Map<String, dynamic>> _anomalies = [];
  bool _isLoading = false;
  String? _error;

  InsightsProvider({required this.apiService});

  List<ApplianceUsage> get appliances => _appliances;
  List<BehaviorPattern> get behaviorPatterns => _behaviorPatterns;
  List<Map<String, dynamic>> get anomalies => _anomalies;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Fetch all insights
  Future<void> fetchInsights() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Fetch appliances
      _appliances = await apiService.getApplianceBreakdown();

      // Fetch behavior patterns and anomalies
      final insights = await apiService.getInsights();
      _behaviorPatterns = insights['patterns'] ?? [];
      _anomalies = insights['anomalies'] ?? [];

      _error = null;
    } catch (e) {
      _error = e.toString();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Get top appliance by usage
  ApplianceUsage? get topAppliance {
    return _appliances.isEmpty
        ? null
        : _appliances.reduce((a, b) => a.percentage > b.percentage ? a : b);
  }

  // Get total appliances
  int get applianceCount => _appliances.length;

  // Get behavior pattern by category
  List<BehaviorPattern> getBehaviorByCategory(String category) {
    return _behaviorPatterns.where((p) => p.category == category).toList();
  }

  // Get anomalies by severity
  List<Map<String, dynamic>> getAnomaliesBySeverity(String severity) {
    return _anomalies.where((a) => a['severity'] == severity).toList();
  }

  // Detect behavior patterns (learn from sensor data)
  // This integrates with the AI/ML backend's behavior learning
  void updateBehaviorPatterns(Map<String, dynamic> newPattern) {
    // This would be called when new patterns are detected
    // For now, we fetch from the API
    fetchInsights();
  }
}
