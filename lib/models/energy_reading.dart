import 'package:intl/intl.dart';

class EnergyReading {
  final DateTime timestamp;
  final double power;
  final double voltage;
  final double current;
  final String predictedAppliance;
  final int energyScore;
  final bool isAnomaly;
  final String? anomalyInsight;
  final double estimatedBill;

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

  double get powerInKwh => power / 1000;

  double get costToday {
    return powerInKwh * 0.45;
  }

  double get carbonEmission => powerInKwh * 0.95;

  double get differencePercentage => -14.0;

  factory EnergyReading.fromJson(Map<String, dynamic> json) {
    DateTime parsedTimestamp;

    try {
      final rawTimestamp = json['timestamp']?.toString() ?? "";
      final fixedTimestamp = rawTimestamp.replaceFirst(" ", "T");
      parsedTimestamp = DateTime.parse(fixedTimestamp);
    } catch (e) {
      parsedTimestamp = DateTime.now();
    }

    final powerValue = (json['power'] as num?)?.toDouble() ?? 0.0;

    return EnergyReading(
      timestamp: parsedTimestamp,
      power: powerValue,
      voltage: (json['voltage'] as num?)?.toDouble() ?? 0.0,
      current: (json['current'] as num?)?.toDouble() ?? 0.0,
      predictedAppliance:
          json['predicted_appliance']?.toString() ?? "Unknown",
      energyScore: (json['energy_score'] as num?)?.toInt() ?? 0,
      isAnomaly: json['is_anomaly'] as bool? ?? false,
      anomalyInsight: json['anomaly_insight']?.toString(),
      estimatedBill:
          (json['estimated_bill'] as num?)?.toDouble() ??
          ((powerValue / 1000) * 0.45 * 24 * 30),
    );
  }

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

  String get formattedTimestamp => DateFormat('hh:mm a').format(timestamp);

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