import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:enersense/providers/insights_provider.dart';
import 'package:enersense/widgets/appliance_list_item.dart';
import 'package:enersense/widgets/chart_helpers.dart';
import 'package:enersense/theme.dart';

class InsightsScreen extends StatefulWidget {
  const InsightsScreen({super.key});

  @override
  State<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<InsightsProvider>().fetchInsights();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: _buildGlassAppBar(),
      body: _buildGradientBackground(
        child: Consumer<InsightsProvider>(
          builder: (context, insightsProvider, child) {
            if (insightsProvider.isLoading &&
                insightsProvider.appliances.isEmpty) {
              return _buildLoadingState();
            }

            return RefreshIndicator(
              onRefresh: () => insightsProvider.fetchInsights(),
              backgroundColor: Colors.white.withOpacity(0.1),
              color: AppTheme.primaryBlue,
              child: SingleChildScrollView(
                physics: AlwaysScrollableScrollPhysics(),
                padding: EdgeInsets.fromLTRB(16, 100, 16, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionHeader('Appliance disaggregation',
                        'Estimated from one smart-meter sensor using NILM'),
                    SizedBox(height: 16),
                    _buildChartCard(insightsProvider),
                    SizedBox(height: 24),
                    ...insightsProvider.appliances.map((appliance) {
                      return ApplianceListItem(
                        icon: appliance.icon,
                        applianceName: appliance.applianceName,
                        percentage: appliance.formattedPercentage,
                        power: appliance.formattedPower,
                        color: appliance.color,
                      );
                    }),
                    SizedBox(height: 32),
                    _buildSectionHeader(
                        'Behavior analytics', 'Routines learned this week'),
                    SizedBox(height: 16),
                    ...insightsProvider.behaviorPatterns.map((pattern) {
                      return _buildPatternCard(pattern);
                    }),
                    SizedBox(height: 32),
                    _buildSectionHeader(
                        'Anomalies detected', 'Recent issues identified'),
                    SizedBox(height: 16),
                    ...insightsProvider.anomalies.map((anomaly) {
                      return _buildAnomalyCard(anomaly);
                    }),
                    SizedBox(height: 20),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  PreferredSizeWidget _buildGlassAppBar() {
    return PreferredSize(
      preferredSize: const Size.fromHeight(60),
      child: ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.7),
              border: Border(
                bottom: BorderSide(
                  color: Colors.white.withOpacity(0.2),
                  width: 1,
                ),
              ),
            ),
            child: SafeArea(
              bottom: false,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Insights',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white.withOpacity(0.2),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: Center(
                        child: Icon(
                          Icons.insights_outlined,
                          color: AppTheme.primaryBlue,
                          size: 18,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGradientBackground({required Widget child}) {
    return Container(
      decoration: BoxDecoration(gradient: AppTheme.lightBackgroundGradient),
      child: child,
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _buildGlassContainer(
            width: 80,
            height: 80,
            borderRadius: 40,
            child: Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(
                  AppTheme.primaryBlue,
                ),
              ),
            ),
          ),
          SizedBox(height: 24),
          Text(
            'Loading insights...',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppTheme.textDark,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        SizedBox(height: 4),
        Text(
          subtitle,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: AppTheme.textGrey,
          ),
        ),
      ],
    );
  }

  Widget _buildChartCard(InsightsProvider insightsProvider) {
    return _buildGlassContainer(
      width: double.infinity,
      height: 280,
      borderRadius: 24,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: insightsProvider.appliances.isEmpty
            ? Center(
                child: Text(
                  'No appliance data',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              )
            : PieChartHelper.buildApplianceChart(
                insightsProvider.appliances
                    .map((a) => {
                          'percentage': a.percentage,
                          'name': a.applianceName,
                        })
                    .toList(),
              ),
      ),
    );
  }

  Widget _buildPatternCard(dynamic pattern) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: _buildGlassContainer(
        width: double.infinity,
        child: Padding(
          padding: EdgeInsets.all(12),
          child: Row(
            children: [
              Text(pattern.categoryIcon, style: TextStyle(fontSize: 24)),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      pattern.time,
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      pattern.description,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textGrey,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnomalyCard(Map<String, dynamic> anomaly) {
    final severity = anomaly['severity'] as String? ?? 'Low';
    final severityColor = severity == 'High'
        ? Colors.red
        : severity == 'Medium'
            ? Colors.orange
            : Colors.yellow.shade700;

    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: _buildGlassContainer(
        width: double.infinity,
        glassColor: severityColor.withOpacity(0.08),
        borderColor: severityColor.withOpacity(0.3),
        child: Padding(
          padding: EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.warning_amber, color: severityColor, size: 20),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      anomaly['title'] ?? 'Unknown anomaly',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textDark,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      anomaly['description'] ?? '',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textGrey,
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(width: 8),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: severityColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  severity,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: severityColor,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGlassContainer({
    double? width,
    double? height,
    double borderRadius = 20,
    Color? glassColor,
    Color? borderColor,
    required Widget child,
  }) {
    final backgroundColor = glassColor ?? Colors.white.withOpacity(0.7);
    final borderCol = borderColor ?? Colors.white.withOpacity(0.2);

    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            color: backgroundColor,
            border: Border.all(
              color: borderCol,
              width: 1.5,
            ),
            borderRadius: BorderRadius.circular(borderRadius),
          ),
          child: child,
        ),
      ),
    );
  }
}
