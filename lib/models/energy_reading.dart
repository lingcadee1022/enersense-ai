import 'package:intl/intl.dart';

class EnergyReading {
  final DateTime timestamp;
  final double power; // in Watts
  final double voltage; // in Volts
  final double current; // in Amperes
  final String predictedAppliance;
  final int energyScore; // 0-100
  final bool isAnomaly;
  final String? anomalyInsight;
  final double estimatedBill; // in RM

  EnergyReading({
    required this.timestamp,
    required this.power,
    required this.voltage,
    required this.current,
    required this.predictedAppliance,
    required this.energyScore,
    required this.isAnomaly,
    this.anomalyInsight,
    required this.estimatedBill,
  });

  // Convert power in Watts to kWh
  double get powerInKwh => power / 1000;

  // Cost calculation (RM 0.45 per kWh)
  double get costToday {
    // Assuming this is hourly average, multiply by rate
    return powerInKwh * 0.45;
  }

  // Carbon footprint estimate (kg CO2 per hour, ~0.95 kg CO2 per kWh in Malaysia)
  double get carbonEmission => powerInKwh * 0.95;

  // Difference from yesterday (for demo, 14% less)
  double get differencePercentage => -14.0;

  static double _sanitizeDouble(dynamic value, {double fallback = 0.0}) {
    if (value == null) return fallback;
    final double parsed = (value as num).toDouble();
    if (!parsed.isFinite || parsed.isNegative) return fallback;
    return parsed == -0.0 ? 0.0 : parsed;
  }

  // Parse from API JSON response
  factory EnergyReading.fromJson(Map<String, dynamic> json) {
    return EnergyReading(
      timestamp: DateTime.parse(json['timestamp'] as String),
      power: _sanitizeDouble(json['power']),
      voltage: _sanitizeDouble(json['voltage'], fallback: 240.0),
      current: _sanitizeDouble(json['current']),
      predictedAppliance: json['predicted_appliance'] as String? ?? 'Unknown',
      energyScore: json['energy_score'] as int? ?? 75,
      isAnomaly: json['is_anomaly'] as bool? ?? false,
      anomalyInsight: json['anomaly_insight'] as String?,
      estimatedBill: _sanitizeDouble(json['estimated_bill'], fallback: 218.40),
    );
  }

  // Convert to JSON for API calls
  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'power': power,
      'voltage': voltage,
      'current': current,
      'predicted_appliance': predictedAppliance,
      'energy_score': energyScore,
      'is_anomaly': isAnomaly,
      'anomaly_insight': anomalyInsight,
      'estimated_bill': estimatedBill,
    };
  }

  // Format methods for UI display
  String get formattedTimestamp =>
      DateFormat('hh:mm a').format(timestamp);

  String get formattedPower {
    if (powerInKwh >= 1) {
      return '${powerInKwh.toStringAsFixed(2)} kWh';
    } else {
      return '${power.toStringAsFixed(0)} W';
    }
  }

  String get formattedCost => 'RM ${costToday.toStringAsFixed(2)}';
  String get formattedCarbon => '${carbonEmission.toStringAsFixed(1)} kg';
  String get formattedBill => 'RM ${estimatedBill.toStringAsFixed(2)}';
}
