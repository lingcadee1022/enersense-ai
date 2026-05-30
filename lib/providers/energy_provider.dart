import 'package:flutter/material.dart';
import 'package:enersense/models/energy_reading.dart';
import 'package:enersense/services/api_service.dart';

class EnergyProvider extends ChangeNotifier {
  final ApiService apiService;
  EnergyReading? _currentReading;
  bool _isLoading = false;
  String? _error;

  EnergyProvider({required this.apiService});

  EnergyReading? get currentReading => _currentReading;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Fetch live usage
  Future<void> fetchLiveUsage() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _currentReading = await apiService.getLiveUsage();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Initialize with auto-refresh (5 seconds)
  void startAutoRefresh() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 5));
      if (_isLoading == false) {
        try {
          _currentReading = await apiService.getLiveUsage();
        } catch (e) {
          print('Auto-refresh failed: $e');
        }
        notifyListeners();
      }
      return true; // Continue polling
    });
  }

  // Get cost today
  double get costToday => _currentReading?.costToday ?? 0.0;

  // Get carbon emissions
  double get carbonEmission => _currentReading?.carbonEmission ?? 0.0;

  // Get formatted values
  String get formattedPower => _currentReading?.formattedPower ?? '-- kWh';
  String get formattedBill => 'RM ${_currentReading?.estimatedBill.toStringAsFixed(2) ?? "0.00"}';
  String get formattedCost => 'RM ${costToday.toStringAsFixed(2)}';
  String get formattedCarbon => '${carbonEmission.toStringAsFixed(1)} kg';
}
