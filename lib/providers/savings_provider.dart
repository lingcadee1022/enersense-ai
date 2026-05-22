import 'package:flutter/material.dart';
import 'package:enersense/models/recommendation.dart';
import 'package:enersense/services/api_service.dart';

class SavingsProvider extends ChangeNotifier {
  final ApiService apiService;
  double _totalSaved = 146.0;
  double _monthlyProjection = 1824.0;
  double _estimatedSavings = 17.0;
  List<Recommendation> _recommendations = [];
  bool _isLoading = false;
  String? _error;

  // What-if simulator state
  double _eveningLoadAdjustment = 0.0; // -100 to +100 (percentage)

  SavingsProvider({required this.apiService});

  double get totalSaved => _totalSaved;
  double get monthlyProjection => _monthlyProjection;
  double get estimatedSavings => _estimatedSavings;
  List<Recommendation> get recommendations => _recommendations;
  bool get isLoading => _isLoading;
  String? get error => _error;

  double get eveningLoadAdjustment => _eveningLoadAdjustment;

  // Fetch savings data
  Future<void> fetchSavings({double? adjustment}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await apiService.getSavingsPredictions(
        eveningLoadAdjustment: adjustment,
      );

      _totalSaved = data['total_saved'] ?? 146.0;
      _monthlyProjection = data['monthly_projection'] ?? 1824.0;
      _estimatedSavings = data['estimated_savings'] ?? 17.0;
      _recommendations = data['recommendations'] ?? [];

      _error = null;
    } catch (e) {
      _error = e.toString();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Update what-if slider (real-time)
  void updateEveningLoadAdjustment(double value) {
    _eveningLoadAdjustment = value;
    // Recalculate estimated savings based on adjustment
    _recalculateSavings();
    notifyListeners();
  }

  // Recalculate savings based on what-if slider
  void _recalculateSavings() {
    // Simulate savings calculation
    // Base savings: 17/month, adjust by slider value
    final adjustmentFactor = 1.0 + (_eveningLoadAdjustment / 100.0);
    _estimatedSavings = 17.0 * adjustmentFactor;
    _monthlyProjection = _totalSaved + (_estimatedSavings * 12);
  }

  // Accept recommendation
  void acceptRecommendation(String recId) {
    try {
      final rec = _recommendations.firstWhere((r) => r.id == recId);
      rec.accepted = true;
      rec.rejected = false;
      notifyListeners();

      // Persist to API (for later)
      // await apiService.updateRecommendation(recId, accepted: true);
    } catch (_) {
      // Recommendation not found
    }
  }

  // Reject recommendation
  void rejectRecommendation(String recId) {
    try {
      final rec = _recommendations.firstWhere((r) => r.id == recId);
      rec.rejected = true;
      rec.accepted = false;
      notifyListeners();

      // Persist to API (for later)
      // await apiService.updateRecommendation(recId, rejected: true);
    } catch (_) {
      // Recommendation not found
    }
  }

  // Get pending recommendations (not accepted/rejected)
  List<Recommendation> get pendingRecommendations {
    return _recommendations.where((r) => !r.accepted && !r.rejected).toList();
  }

  // Get appliance ROI data (simulated)
  Map<String, dynamic> getApplianceROI() {
    return {
      'appliance': 'Inverter AC',
      'cost': 'RM 3,500',
      'monthlyOldCost': 280.0,
      'monthlyNewCost': 196.0,
      'monthlySavings': 84.0,
      'paybackMonths': 14,
    };
  }

  // Format methods for UI
  String get formattedTotalSaved => 'RM ${_totalSaved.toStringAsFixed(0)}';
  String get formattedMonthlyProjection =>
      'RM ${_monthlyProjection.toStringAsFixed(0)}';
  String get formattedEstimatedSavings =>
      'RM ${_estimatedSavings.toStringAsFixed(0)}/month';
}
