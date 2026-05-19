class UserProfile {
  final String userId;
  final String name;
  final double comfortLevel; // 0-100, where 0 = save more, 100 = comfort more
  final bool automationEnabled;
  final double ecoScore; // 0-100
  final List<String> badges; // ["Energy Saver", "Peak Shifter", "Eco Hero"]
  final int feedbackSignals; // Number of learning signals from user
  final DateTime lastUpdated;

  UserProfile({
    required this.userId,
    required this.name,
    required this.comfortLevel,
    required this.automationEnabled,
    required this.ecoScore,
    required this.badges,
    required this.feedbackSignals,
    required this.lastUpdated,
  });

  // Get Eco score interpretation
  String get ecoScoreInterpretation {
    if (ecoScore >= 80) return 'Excellent';
    if (ecoScore >= 60) return 'Good';
    if (ecoScore >= 40) return 'Fair';
    return 'Needs Improvement';
  }

  // Get comfort preference label
  String get comfortPreference {
    if (comfortLevel >= 70) return 'Comfort focused';
    if (comfortLevel >= 40) return 'Balanced';
    return 'Savings focused';
  }

  // Parse from API or local storage
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['user_id'] as String? ?? 'user_default',
      name: json['name'] as String? ?? 'User',
      comfortLevel: (json['comfort_level'] as num?)?.toDouble() ?? 50.0,
      automationEnabled: json['automation_enabled'] as bool? ?? true,
      ecoScore: (json['eco_score'] as num?)?.toDouble() ?? 78.0,
      badges: json['badges'] != null
          ? List<String>.from(json['badges'] as List)
          : ['Energy Saver'],
      feedbackSignals: json['feedback_signals'] as int? ?? 18,
      lastUpdated: json['last_updated'] != null ? DateTime.tryParse(json['last_updated'] as String) ?? DateTime.now() : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'name': name,
      'comfort_level': comfortLevel,
      'automation_enabled': automationEnabled,
      'eco_score': ecoScore,
      'badges': badges,
      'feedback_signals': feedbackSignals,
      'last_updated': lastUpdated.toIso8601String(),
    };
  }

  // Default user profile for demo
  static UserProfile createDefault() {
    return UserProfile(
      userId: 'user_default',
      name: 'You',
      comfortLevel: 45.0,
      automationEnabled: true,
      ecoScore: 78.0,
      badges: ['Energy Saver', 'Peak Shifter', 'Eco Hero'],
      feedbackSignals: 18,
      lastUpdated: DateTime.now(),
    );
  }
}
