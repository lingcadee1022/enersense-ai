/// Household Profile Model
/// Represents the household information and preferences of a user

class HouseholdProfile {
  final String householdSize;
  final String homeType;
  final List<String> appliances;
  final String occupancy;
  final double monthlyBudget;
  final String? createdAt;
  final String? updatedAt;

  HouseholdProfile({
    required this.householdSize,
    required this.homeType,
    required this.appliances,
    required this.occupancy,
    required this.monthlyBudget,
    this.createdAt,
    this.updatedAt,
  });

  /// Create a HouseholdProfile from JSON (API response)
  factory HouseholdProfile.fromJson(Map<String, dynamic> json) {
    return HouseholdProfile(
      householdSize: json['household_size'] as String? ?? '2-3 People',
      homeType: json['home_type'] as String? ?? 'Apartment / Condo',
      appliances: json['appliances'] != null
          ? List<String>.from(json['appliances'] as List)
          : ['Refrigerator', 'Television'],
      occupancy: json['occupancy'] as String? ?? 'All Day',
      monthlyBudget:
          (json['monthly_budget'] as num?)?.toDouble() ?? 150.0,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
    );
  }

  /// Convert HouseholdProfile to JSON (API request)
  Map<String, dynamic> toJson() {
    return {
      'household_size': householdSize,
      'home_type': homeType,
      'appliances': appliances,
      'occupancy': occupancy,
      'monthly_budget': monthlyBudget,
    };
  }

  /// Create a copy with updated fields
  HouseholdProfile copyWith({
    String? householdSize,
    String? homeType,
    List<String>? appliances,
    String? occupancy,
    double? monthlyBudget,
    String? createdAt,
    String? updatedAt,
  }) {
    return HouseholdProfile(
      householdSize: householdSize ?? this.householdSize,
      homeType: homeType ?? this.homeType,
      appliances: appliances ?? this.appliances,
      occupancy: occupancy ?? this.occupancy,
      monthlyBudget: monthlyBudget ?? this.monthlyBudget,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// Create a default household profile
  static HouseholdProfile createDefault() {
    return HouseholdProfile(
      householdSize: '2-3 People',
      homeType: 'Apartment / Condo',
      appliances: ['Refrigerator', 'Television'],
      occupancy: 'All Day',
      monthlyBudget: 150.0,
    );
  }

  @override
  String toString() {
    return 'HouseholdProfile('
        'householdSize: $householdSize, '
        'homeType: $homeType, '
        'appliances: $appliances, '
        'occupancy: $occupancy, '
        'monthlyBudget: $monthlyBudget)';
  }
}
