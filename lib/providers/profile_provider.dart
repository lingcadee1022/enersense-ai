import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:enersense/models/user_profile.dart';

class ProfileProvider extends ChangeNotifier {
  UserProfile? _profile;
  bool _isLoading = false;
  String? _error;
  late SharedPreferences _prefs;

  ProfileProvider() {
    _initProfile();
  }

  UserProfile? get profile => _profile;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Initialize profile from SharedPreferences or create default
  Future<void> _initProfile() async {
    _isLoading = true;
    notifyListeners();

    try {
      _prefs = await SharedPreferences.getInstance();

      // Try to load saved profile
      final profileJson = _prefs.getString('user_profile');
      if (profileJson != null) {
        // _profile = UserProfile.fromJson(jsonDecode(profileJson));
        _profile = UserProfile.createDefault();
      } else {
        _profile = UserProfile.createDefault();
        await _saveProfile();
      }

      _error = null;
    } catch (e) {
      _error = e.toString();
      _profile = UserProfile.createDefault();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Save profile to SharedPreferences
  Future<void> _saveProfile() async {
    if (_profile != null) {
      // await _prefs.setString('user_profile', jsonEncode(_profile!.toJson()));
    }
  }

  // Update comfort level
  void updateComfortLevel(double value) {
    if (_profile != null) {
      _profile = UserProfile(
        userId: _profile!.userId,
        name: _profile!.name,
        comfortLevel: value,
        automationEnabled: _profile!.automationEnabled,
        ecoScore: _profile!.ecoScore,
        badges: _profile!.badges,
        feedbackSignals: _profile!.feedbackSignals,
        lastUpdated: DateTime.now(),
      );
      _saveProfile();
      notifyListeners();
    }
  }

  // Toggle automation
  void toggleAutomation() {
    if (_profile != null) {
      _profile = UserProfile(
        userId: _profile!.userId,
        name: _profile!.name,
        comfortLevel: _profile!.comfortLevel,
        automationEnabled: !_profile!.automationEnabled,
        ecoScore: _profile!.ecoScore,
        badges: _profile!.badges,
        feedbackSignals: _profile!.feedbackSignals,
        lastUpdated: DateTime.now(),
      );
      _saveProfile();
      notifyListeners();
    }
  }

  // Update eco score (simulated - in reality, this comes from backend)
  void updateEcoScore(double newScore) {
    if (_profile != null) {
      _profile = UserProfile(
        userId: _profile!.userId,
        name: _profile!.name,
        comfortLevel: _profile!.comfortLevel,
        automationEnabled: _profile!.automationEnabled,
        ecoScore: newScore.clamp(0, 100),
        badges: _profile!.badges,
        feedbackSignals: _profile!.feedbackSignals,
        lastUpdated: DateTime.now(),
      );
      _saveProfile();
      notifyListeners();
    }
  }

  // Add badge
  void addBadge(String badge) {
    if (_profile != null && !_profile!.badges.contains(badge)) {
      final newBadges = [..._profile!.badges, badge];
      _profile = UserProfile(
        userId: _profile!.userId,
        name: _profile!.name,
        comfortLevel: _profile!.comfortLevel,
        automationEnabled: _profile!.automationEnabled,
        ecoScore: _profile!.ecoScore,
        badges: newBadges,
        feedbackSignals: _profile!.feedbackSignals + 1,
        lastUpdated: DateTime.now(),
      );
      _saveProfile();
      notifyListeners();
    }
  }

  // Get formatted data
  String get formattedEcoScore => '${_profile?.ecoScore.toStringAsFixed(0) ?? "78"}';
  String get ecoScoreInterpretation =>
      _profile?.ecoScoreInterpretation ?? 'Excellent';
  String get comfortPreference => _profile?.comfortPreference ?? 'Balanced';
}
