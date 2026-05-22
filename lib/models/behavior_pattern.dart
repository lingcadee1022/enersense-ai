class BehaviorPattern {
  final String id;
  final String time; // e.g., "7 AM", "6 PM", "11 PM", "2 AM"
  final String category; // "base_load", "peak_routine", "ac_pattern", "anomaly"
  final String description;
  final String? icon;
  final DateTime detectedAt;

  BehaviorPattern({
    required this.id,
    required this.time,
    required this.category,
    required this.description,
    this.icon,
    required this.detectedAt,
  });

  // Get icon based on category
  String get categoryIcon {
    switch (category) {
      case 'base_load':
        return '🏠';
      case 'peak_routine':
        return '📈';
      case 'ac_pattern':
        return '❄️';
      case 'anomaly':
        return '⚠️';
      default:
        return '📊';
    }
  }

  // Get description based on category
  String get categoryLabel {
    switch (category) {
      case 'base_load':
        return 'Base load';
      case 'peak_routine':
        return 'Peak routine';
      case 'ac_pattern':
        return 'AC pattern';
      case 'anomaly':
        return 'Anomaly';
      default:
        return 'Pattern';
    }
  }

  // Parse from API
  factory BehaviorPattern.fromJson(Map<String, dynamic> json) {
    return BehaviorPattern(
      id: json['id'] as String? ?? 'pattern_${DateTime.now().millisecondsSinceEpoch}',
      time: json['time'] as String? ?? 'Unknown',
      category: json['category'] as String? ?? 'anomaly',
      description: json['description'] as String? ?? 'No description',
      icon: json['icon'] as String?,
      detectedAt: DateTime.tryParse((json['detected_at'] as String?) ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'time': time,
      'category': category,
      'description': description,
      'icon': icon,
      'detected_at': detectedAt.toIso8601String(),
    };
  }
}
