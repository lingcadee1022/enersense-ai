import 'package:flutter/material.dart';

class ApplianceUsage {
  final String applianceName;
  final double powerUsage; // in Watts
  final double percentage; // 0-100%
  final String icon;
  final int colorValue; // Store as int for serialization

  ApplianceUsage({
    required this.applianceName,
    required this.powerUsage,
    required this.percentage,
    required this.icon,
    required this.colorValue,
  });

  // Get Color object from stored value
  Color get color => Color(colorValue);

  // Format for display
  String get formattedPower => '${(powerUsage / 1000).toStringAsFixed(1)} kWh';
  String get formattedPercentage => '${percentage.toStringAsFixed(0)}%';

  // Parse from API
  factory ApplianceUsage.fromJson(Map<String, dynamic> json) {
    return ApplianceUsage(
      applianceName: json['appliance_name'] as String,
      powerUsage: (json['power_usage'] as num).toDouble(),
      percentage: (json['percentage'] as num).toDouble(),
      icon: _getIconForAppliance(json['appliance_name'] as String),
      colorValue: _getColorValueForAppliance(json['appliance_name'] as String),
    );
  }

  static String _getIconForAppliance(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('ac') || lower.contains('air')) return '❄️';
    if (lower.contains('fridge') || lower.contains('refrigerator')) return '🧊';
    if (lower.contains('heat')) return '🔥';
    if (lower.contains('light') || lower.contains('led')) return '💡';
    if (lower.contains('tv') || lower.contains('television')) return '📺';
    if (lower.contains('wash') || lower.contains('laundry')) return '🧺';
    if (lower.contains('cook') || lower.contains('oven')) return '🍳';
    if (lower.contains('water')) return '💧';
    return '⚡';
  }

  static int _getColorValueForAppliance(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('ac') || lower.contains('air')) return 0xFF00BCD4;
    if (lower.contains('fridge')) return 0xFF2196F3;
    if (lower.contains('heat')) return 0xFFFF9800;
    if (lower.contains('light')) return 0xFFFFC107;
    if (lower.contains('tv')) return 0xFF9C27B0;
    if (lower.contains('wash')) return 0xFF4CAF50;
    if (lower.contains('cook')) return 0xFFFF5722;
    return 0xFF607D8B;
  }
}
