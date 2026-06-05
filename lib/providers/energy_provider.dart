import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:enersense/models/energy_reading.dart';
import 'package:enersense/services/api_service.dart';

class EnergyProvider extends ChangeNotifier {
  final ApiService apiService;
  EnergyReading? _currentReading;
  bool _isLoading = false;
  String? _error;
  Timer? _refreshTimer;
  final Random _random = Random();
  double _lastKwhValue = 4.2;
  final List<double> _usageTrend = [
    3.9,
    4.4,
    4.8,
    4.2,
    4.6,
    3.7,
    4.5,
  ];

  EnergyProvider({required this.apiService});

  EnergyReading? get currentReading => _currentReading;
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<double> get usageTrend => List.unmodifiable(_usageTrend);
  double get dailyTotalKwh => _usageTrend.fold(0.0, (sum, value) => sum + value);

  // Fetch live usage
  Future<void> fetchLiveUsage() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final reading = await apiService.getLiveUsage();
      _currentReading = reading;
      _error = null;
      _appendUsagePoint(reading.powerInKwh);
    } catch (e) {
      _error = e.toString();
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<void> refreshMockUsage() async {
    _currentReading = _generateMockReading();
    _error = null;
    _isLoading = false;
    notifyListeners();
  }

  void _appendUsagePoint(double value) {
    final normalized = _normalizeValue(value);
    if (_usageTrend.length >= 7) {
      _usageTrend.removeAt(0);
    }
    _usageTrend.add(normalized);
  }

  double _normalizeValue(double value) {
    if (!value.isFinite || value.isNegative) {
      return 0.0;
    }
    if (value == -0.0) {
      return 0.0;
    }
    return value;
  }

  EnergyReading _generateMockReading() {
    final nextKwh = _generateNextKwhValue();
    _appendUsagePoint(nextKwh);

    final powerWatts = (nextKwh * 1000).clamp(0.0, double.infinity);
    final current = (powerWatts / 240.0).clamp(0.0, double.infinity);
    final estimatedBill = nextKwh * 0.45;

    return EnergyReading(
      timestamp: DateTime.now(),
      power: powerWatts,
      voltage: 240.0,
      current: current,
      predictedAppliance: _getPredictedAppliance(nextKwh),
      energyScore: _getEnergyScore(nextKwh),
      isAnomaly: false,
      anomalyInsight: null,
      estimatedBill: estimatedBill,
    );
  }

  double _generateNextKwhValue() {
    final variation = (_random.nextDouble() * 0.6) - 0.3;
    final nextValue = _lastKwhValue + variation;
    _lastKwhValue = nextValue.clamp(3.0, 5.2);
    return _normalizeValue(_lastKwhValue);
  }

  String _getPredictedAppliance(double kwh) {
    if (kwh > 5.0) return 'Air Conditioner';
    if (kwh > 4.4) return 'Washer';
    if (kwh > 4.0) return 'Heater';
    return 'Refrigerator';
  }

  int _getEnergyScore(double kwh) {
    if (kwh > 5.0) return 35;
    if (kwh > 4.5) return 45;
    if (kwh > 4.0) return 55;
    return 65;
  }

  // Initialize with auto-refresh (3 seconds) using frontend mock data
  void startAutoRefresh() {
    _refreshTimer?.cancel();
    _currentReading ??= _generateMockReading();
    notifyListeners();
    _refreshTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      if (_isLoading) return;
      _currentReading = _generateMockReading();
      notifyListeners();
    });
  }

  void stopAutoRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = null;
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
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
