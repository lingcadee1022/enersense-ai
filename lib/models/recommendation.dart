class Recommendation {
  final String id;
  final String title;
  final String description;
  final double savingsAmount; // in RM/week or RM/month
  final String savingsPeriod; // "week" or "month"
  final String type; // "behavior", "automation", "appliance", "timing"
  bool accepted;
  bool rejected;
  final DateTime createdAt;

  Recommendation({
    required this.id,
    required this.title,
    required this.description,
    required this.savingsAmount,
    required this.savingsPeriod,
    required this.type,
    this.accepted = false,
    this.rejected = false,
    required this.createdAt,
  });

  // Parse from API response
  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      id: json['id'] as String? ?? 'rec_${DateTime.now().millisecondsSinceEpoch}',
      title: json['title'] as String? ?? 'Recommendation',
      description: json['description'] as String? ?? '',
      savingsAmount: (json['savings_amount'] as num?)?.toDouble() ?? 0.0,
      savingsPeriod: json['savings_period'] as String? ?? 'week',
      type: json['type'] as String? ?? 'behavior',
      accepted: json['accepted'] as bool? ?? false,
      rejected: json['rejected'] as bool? ?? false,
      createdAt: DateTime.tryParse((json['created_at'] as String?) ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'savings_amount': savingsAmount,
      'savings_period': savingsPeriod,
      'type': type,
      'accepted': accepted,
      'rejected': rejected,
      'created_at': createdAt.toIso8601String(),
    };
  }

  // Display formatted savings
  String get formattedSavings => 'RM ${savingsAmount.toStringAsFixed(0)}/$savingsPeriod';

  // Status string
  String get status {
    if (accepted) return 'Accepted';
    if (rejected) return 'Rejected';
    return 'Pending';
  }

  // Icon based on type
  String get typeIcon {
    switch (type) {
      case 'automation':
        return '⚙️';
      case 'appliance':
        return '💡';
      case 'timing':
        return '⏰';
      case 'behavior':
      default:
        return '📊';
    }
  }
}
