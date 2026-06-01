import 'package:flutter/material.dart';
import 'package:enersense/models/household_profile.dart';
import 'package:enersense/services/api_service.dart';

class HouseholdProfileProvider extends ChangeNotifier {
  final ApiService _apiService;

  HouseholdProfile? _profile;
  bool _isLoading = false;
  String? _error;
  bool _isSaving = false;

  HouseholdProfileProvider({required ApiService apiService})
      : _apiService = apiService {
    _loadProfile();
  }

  // Getters
  HouseholdProfile? get profile => _profile;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isSaving => _isSaving;

  /// Load household profile from API
  Future<void> _loadProfile() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _profile = await _apiService.getHouseholdProfile();
    } catch (e) {
      _error = e.toString();
      _profile = HouseholdProfile.createDefault();
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Save household profile to API
  Future<bool> saveProfile(HouseholdProfile profile) async {
    _isSaving = true;
    _error = null;
    notifyListeners();

    try {
      final success = await _apiService.saveHouseholdProfile(profile);
      if (success) {
        _profile = profile;
        _error = null;
        _isSaving = false;
        notifyListeners();
        return true;
      } else {
        throw Exception('Failed to save household profile');
      }
    } catch (e) {
      _error = e.toString();
      _isSaving = false;
      notifyListeners();
      return false;
    }
  }

  /// Refresh profile from API
  Future<void> refreshProfile() async {
    await _loadProfile();
  }

  /// Update household size
  void updateHouseholdSize(String size) {
    if (_profile != null) {
      _profile = _profile!.copyWith(householdSize: size);
      notifyListeners();
    }
  }

  /// Update home type
  void updateHomeType(String type) {
    if (_profile != null) {
      _profile = _profile!.copyWith(homeType: type);
      notifyListeners();
    }
  }

  /// Update appliances list
  void updateAppliances(List<String> appliances) {
    if (_profile != null) {
      _profile = _profile!.copyWith(appliances: appliances);
      notifyListeners();
    }
  }

  /// Update occupancy
  void updateOccupancy(String occupancy) {
    if (_profile != null) {
      _profile = _profile!.copyWith(occupancy: occupancy);
      notifyListeners();
    }
  }

  /// Update monthly budget
  void updateMonthlyBudget(double budget) {
    if (_profile != null) {
      _profile = _profile!.copyWith(monthlyBudget: budget);
      notifyListeners();
    }
  }

  /// Add appliance to list
  void addAppliance(String appliance) {
    if (_profile != null && !_profile!.appliances.contains(appliance)) {
      final updated = [..._profile!.appliances, appliance];
      _profile = _profile!.copyWith(appliances: updated);
      notifyListeners();
    }
  }

  /// Remove appliance from list
  void removeAppliance(String appliance) {
    if (_profile != null && _profile!.appliances.contains(appliance)) {
      final updated = _profile!.appliances
          .where((a) => a != appliance)
          .toList();
      _profile = _profile!.copyWith(appliances: updated);
      notifyListeners();
    }
  }

  /// Toggle appliance selection
  void toggleAppliance(String appliance) {
    if (_profile != null) {
      if (_profile!.appliances.contains(appliance)) {
        removeAppliance(appliance);
      } else {
        addAppliance(appliance);
      }
    }
  }
}
