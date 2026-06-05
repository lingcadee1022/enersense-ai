import 'dart:math';

import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class LineChartHelper {
  // Create a line chart for hourly usage trends
  static LineChart buildHourlyChart(List<double> values) {
    final sanitizedValues = values
        .map((value) => value.isFinite && value >= 0 ? value : 0.0)
        .toList();
    final maxValue = sanitizedValues.isNotEmpty
        ? sanitizedValues.reduce(max)
        : 5.0;
    final yMax = max(12.0, maxValue * 1.3);

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true, drawVerticalLine: true),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                const titles = ['6A', '9A', '12P', '3P', '6P', '9P', '12A'];
                int index = value.toInt();
                if (index >= 0 && index < titles.length) {
                  return Text(
                    titles[index],
                    style: TextStyle(fontSize: 11, color: Colors.grey),
                  );
                }
                return Text('');
              },
              interval: 1,
            ),
          ),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                return Text(
                  '${value.toInt()}A',
                  style: TextStyle(fontSize: 11, color: Colors.grey),
                );
              },
              interval: 5,
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: _generateSpots(values),
            isCurved: true,
            color: Color(0xFF00BCD4),
            barWidth: 3,
            dotData: FlDotData(show: true),
            belowBarData: BarAreaData(
              show: true,
              color: Color(0xFF00BCD4).withOpacity(0.2),
            ),
          ),
        ],
        minX: 0,
        maxX: max(6, sanitizedValues.length - 1).toDouble(),
        minY: 0,
        maxY: yMax,
      ),
    );
  }

  static List<FlSpot> _generateSpots(List<double> values) {
    final spots = <FlSpot>[];
    for (int i = 0; i < values.length && i < 7; i++) {
      spots.add(FlSpot(i.toDouble(), values[i]));
    }
    return spots;
  }
}

class PieChartHelper {
  // Create a donut chart for appliance breakdown
  static PieChart buildApplianceChart(
    List<Map<String, dynamic>> applianceData,
  ) {
    final sections = <PieChartSectionData>[];

    final colors = [
      Color(0xFF00BCD4),
      Color(0xFF2196F3),
      Color(0xFFFF9800),
      Color(0xFF4CAF50),
      Color(0xFF9C27B0),
    ];

    for (int i = 0; i < applianceData.length; i++) {
      final data = applianceData[i];
      final value = (data['percentage'] as num).toDouble();

      sections.add(
        PieChartSectionData(
          color: colors[i % colors.length],
          value: value,
          title: '${value.toStringAsFixed(0)}%',
          radius: 60,
          titleStyle: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
      );
    }

    return PieChart(
      PieChartData(
        sections: sections,
        centerSpaceRadius: 40,
        sectionsSpace: 0,
      ),
    );
  }
}

class BarChartHelper {
  // Create a bar chart for savings over time
  static BarChart buildSavingsChart(List<double> monthlySavings) {
    final barGroups = <BarChartGroupData>[];

    for (int i = 0; i < monthlySavings.length; i++) {
      barGroups.add(
        BarChartGroupData(
          x: i,
          barRods: [
            BarChartRodData(
              toY: monthlySavings[i],
              color: Color(0xFF4CAF50),
              width: 12,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(4),
                topRight: Radius.circular(4),
              ),
            ),
          ],
        ),
      );
    }

    return BarChart(
      BarChartData(
        barGroups: barGroups,
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final months = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8'];
                int index = value.toInt();
                if (index >= 0 && index < months.length) {
                  return Text(months[index], style: TextStyle(fontSize: 10));
                }
                return Text('');
              },
            ),
          ),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
      ),
    );
  }
}
