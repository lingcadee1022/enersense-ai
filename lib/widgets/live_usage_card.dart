import 'package:flutter/material.dart';

class LiveUsageCard extends StatelessWidget {
  final String power;
  final String bill;
  final String? difference; // e.g., "-14% vs yesterday"
  final String? alert; // e.g., "AC is top load"
  final bool isAnomaly;
  final String anomalyMessage;

  const LiveUsageCard({
    Key? key,
    required this.power,
    required this.bill,
    this.difference,
    this.alert,
    this.isAnomaly = false,
    this.anomalyMessage = 'Energy hog detected',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24.0),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF1B9688), // Teal
            Color(0xFF26C0B5), // Green
          ],
        ),
        borderRadius: BorderRadius.circular(24.0),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with title and chart icon
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.flash_on, color: Colors.white, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Live household load',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              Icon(Icons.show_chart, color: Colors.white.withOpacity(0.7)),
            ],
          ),
          SizedBox(height: 16),

          // Main power reading
          Text(
            power,
            style: TextStyle(
              color: Colors.white,
              fontSize: 48,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8),

          // Predicted bill
          Text(
            'Predicted bill: $bill this month',
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 14,
            ),
          ),
          SizedBox(height: 16),

          // Tags for difference and alert
          Row(
            children: [
              _buildTag(Icons.trending_down, difference ?? '-14% vs yesterday',
                  Colors.white.withOpacity(0.2)),
              SizedBox(width: 8),
              _buildTag(
                Icons.info_outline,
                alert ?? 'AC is top load',
                Colors.white.withOpacity(0.2),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTag(IconData icon, String text, Color bgColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 14),
          SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
