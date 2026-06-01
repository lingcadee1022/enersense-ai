import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:enersense/models/energy_reading.dart';
import 'package:enersense/models/recommendation.dart';
import 'package:enersense/models/appliance_usage.dart';
import 'package:enersense/models/behavior_pattern.dart';
import 'package:enersense/models/chat_message.dart';

class ApiService {
  late String baseUrl;
  final http.Client httpClient;

  ApiService({String? baseUrl, http.Client? client})
      : baseUrl = baseUrl ?? 'http://localhost:8000',
        httpClient = client ?? http.Client();

  // Set base URL dynamically (for settings screen)
  void setBaseUrl(String url) {
    baseUrl = url;
  }

  // Health check
  Future<bool> healthCheck() async {
    try {
      final response = await httpClient
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  // Get live energy usage
  Future<EnergyReading> getLiveUsage() async {
    try {
      final response = await httpClient
          .get(Uri.parse('$baseUrl/api/v1/live-usage'))
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return EnergyReading.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load live usage');
      }
    } catch (e) {
      print('Error fetching live usage: $e');
      // Return mock data for demo
      return _getMockEnergyReading();
    }
  }

  // Get appliance breakdown
  Future<List<ApplianceUsage>> getApplianceBreakdown() async {
    try {
      final response = await httpClient
          .get(Uri.parse('$baseUrl/appliances'))
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data
            .map((item) => ApplianceUsage.fromJson(item as Map<String, dynamic>))
            .toList();
      } else {
        throw Exception('Failed to load appliances');
      }
    } catch (e) {
      print('Error fetching appliances: $e');
      // Return mock data for demo
      return _getMockAppliances();
    }
  }

  // Get insights (behavior patterns + anomalies)
  Future<Map<String, dynamic>> getInsights() async {
    try {
      final response = await httpClient
          .get(Uri.parse('$baseUrl/api/v1/insights'))
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'patterns': (data['patterns'] as List?)
                  ?.map((p) => BehaviorPattern.fromJson(p as Map<String, dynamic>))
                  .toList() ??
              [],
          'anomalies': data['anomalies'] ?? [],
        };
      } else {
        throw Exception('Failed to load insights');
      }
    } catch (e) {
      print('Error fetching insights: $e');
      // Return mock data for demo
      return _getMockInsights();
    }
  }

  // Get savings predictions and recommendations
  Future<Map<String, dynamic>> getSavingsPredictions(
      {double? eveningLoadAdjustment}) async {
    try {
      final queryParams = <String, String>{};
      if (eveningLoadAdjustment != null) {
        queryParams['evening_adjustment'] = eveningLoadAdjustment.toString();
      }

      final uri = Uri.parse('$baseUrl/forecast').replace(queryParameters: queryParams);
      final response =
          await httpClient.get(uri).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'total_saved': (data['total_saved'] as num?)?.toDouble() ?? 146.0,
          'monthly_projection': (data['monthly_projection'] as num?)?.toDouble() ?? 1824.0,
          'estimated_savings': (data['estimated_savings'] as num?)?.toDouble() ?? 17.0,
          'recommendations': (data['recommendations'] as List?)
                  ?.map((r) => Recommendation.fromJson(r as Map<String, dynamic>))
                  .toList() ??
              [],
        };
      } else {
        throw Exception('Failed to load savings predictions');
      }
    } catch (e) {
      print('Error fetching savings predictions: $e');
      // Return mock data for demo
      return _getMockSavings();
    }
  }

  // Send chat message and get AI response
  // For MVP, we'll use a rule-based system; later integrate with LLM
  Future<ChatMessage> sendChatMessage(String userMessage) async {
    try {
      final payload = jsonEncode({
        'message': userMessage,
        'context': 'energy_assistant',
      });

      final response = await httpClient
          .post(
            Uri.parse('$baseUrl/chat'),
            headers: {'Content-Type': 'application/json'},
            body: payload,
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ChatMessage.fromJson(data);
      } else {
        // Fallback to rule-based response
        return _generateRuleBasedResponse(userMessage);
      }
    } catch (e) {
      print('Error sending chat message: $e');
      // Fallback to rule-based response for offline support
      return _generateRuleBasedResponse(userMessage);
    }
  }

  // ===== Mock Data Generators (for development/offline) =====

  EnergyReading _getMockEnergyReading() {
    return EnergyReading(
      timestamp: DateTime.now(),
      power: 4820.0,
      voltage: 240.0,
      current: 20.08,
      predictedAppliance: 'Air Conditioner',
      energyScore: 42,
      isAnomaly: false,
      anomalyInsight: null,
      estimatedBill: 218.40,
    );
  }

  List<ApplianceUsage> _getMockAppliances() {
    return [
      ApplianceUsage(
        applianceName: 'Air Conditioner',
        powerUsage: 2050.0,
        percentage: 42.5,
        icon: '❄️',
        colorValue: 0xFF00BCD4,
      ),
      ApplianceUsage(
        applianceName: 'Refrigerator',
        powerUsage: 770.0,
        percentage: 16.0,
        icon: '🧊',
        colorValue: 0xFF2196F3,
      ),
      ApplianceUsage(
        applianceName: 'Heater',
        powerUsage: 626.0,
        percentage: 13.0,
        icon: '🔥',
        colorValue: 0xFFFF9800,
      ),
      ApplianceUsage(
        applianceName: 'Lights',
        powerUsage: 480.0,
        percentage: 10.0,
        icon: '💡',
        colorValue: 0xFFFFC107,
      ),
      ApplianceUsage(
        applianceName: 'Others',
        powerUsage: 867.0,
        percentage: 18.0,
        icon: '⚡',
        colorValue: 0xFF607D8B,
      ),
    ];
  }

  Map<String, dynamic> _getMockInsights() {
    return {
      'patterns': [
        BehaviorPattern(
          id: 'pattern_1',
          time: '7 AM',
          category: 'base_load',
          description: 'Fridge + standby',
          detectedAt: DateTime.now(),
        ),
        BehaviorPattern(
          id: 'pattern_2',
          time: '6 PM',
          category: 'peak_routine',
          description: 'Cooking + heater',
          detectedAt: DateTime.now(),
        ),
        BehaviorPattern(
          id: 'pattern_3',
          time: '11 PM',
          category: 'ac_pattern',
          description: 'Bedroom cooling',
          detectedAt: DateTime.now(),
        ),
        BehaviorPattern(
          id: 'pattern_4',
          time: '2 AM',
          category: 'anomaly',
          description: 'Spike detected',
          detectedAt: DateTime.now(),
        ),
      ],
      'anomalies': [
        {
          'title': 'Unusual spike detected',
          'description': 'Kitchen load is 62% above average Tuesday',
          'severity': 'High',
        },
        {
          'title': 'AC running longer',
          'description': 'Bedroom AC has been active for 7h 12m',
          'severity': 'Medium',
        },
        {
          'title': 'Standby waste found',
          'description': 'Entertainment zone idle draw is RM 0.80/day',
          'severity': 'Low',
        },
      ],
    };
  }

  Map<String, dynamic> _getMockSavings() {
    return {
      'total_saved': 146.0,
      'monthly_projection': 1824.0,
      'estimated_savings': 17.0,
      'recommendations': [
        Recommendation(
          id: 'rec_1',
          title: 'Shift laundry to off-peak',
          description:
              'Your washer often runs during 7-9 PM peak window. Shift to RM 8/week',
          savingsAmount: 8.0,
          savingsPeriod: 'week',
          type: 'timing',
          createdAt: DateTime.now(),
        ),
        Recommendation(
          id: 'rec_2',
          title: 'Reduce AC by 1°C',
          description:
              'Night cooling is 34% above baseline. Reduce AC setpoint by 1°C for RM 12/week',
          savingsAmount: 12.0,
          savingsPeriod: 'week',
          type: 'behavior',
          createdAt: DateTime.now(),
        ),
        Recommendation(
          id: 'rec_3',
          title: 'Cut standby power',
          description:
              'TV console and heater draw 0.42 kWh while idle. Use smart plugs for RM 19/month',
          savingsAmount: 19.0,
          savingsPeriod: 'month',
          type: 'automation',
          createdAt: DateTime.now(),
        ),
      ],
    };
  }

  // Rule-based chatbot response for offline/MVP support
  ChatMessage _generateRuleBasedResponse(String userMessage) {
    final lower = userMessage.toLowerCase();
    String response = '';

    if (lower.contains('bill') || lower.contains('expensive') || lower.contains('high')) {
      response =
          'Your evening peak is up 22%, mostly AC and heater overlap. I can automate a comfort-first schedule that avoids peak tariff windows. Would you like me to suggest specific adjustments?';
    } else if (lower.contains('save') || lower.contains('reduce') || lower.contains('cost')) {
      response =
          'Based on your usage patterns, shifting laundry to off-peak hours could save RM 8/week. Also, reducing AC setpoint by 1°C at night saves RM 12/week with minimal comfort impact.';
    } else if (lower.contains('ac') || lower.contains('cool') || lower.contains('temperature')) {
      response =
          'Your AC runs 13+ hours daily. Peak cooling is 11 PM to 2 AM for bedroom. Consider automating a 1°C setpoint increase after midnight to save RM 12/week.';
    } else if (lower.contains('anomaly') || lower.contains('spike') || lower.contains('unusual')) {
      response =
          'I detected a 62% spike in your kitchen load on Tuesday evening—likely simultaneous oven + heater use. These appliances together draw over 3.5 kW. Try staggering them to avoid peak tariffs.';
    } else if (lower.contains('appliance') || lower.contains('which')) {
      response =
          'Your top 3 energy consumers are: 1) Air Conditioner (42% - 13.8 kWh), 2) Refrigerator (16% - 5.4 kWh), 3) Heater (13% - 4.2 kWh). AC is your biggest opportunity for savings.';
    } else if (lower.contains('robot') || lower.contains('automat') || lower.contains('smart')) {
      response =
          'I can automate comfort-first schedules using smart plugs and thermostat settings. This learns your preferences and adjusts in real-time. Would you like to enable automation suggestions?';
    } else {
      response =
          'I can help with: energy bill analysis, appliance breakdown, anomaly detection, savings recommendations, and automation tips. What would you like to know?';
    }

    return ChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      role: 'assistant',
      content: response,
      timestamp: DateTime.now(),
    );
  }
}
