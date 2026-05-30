import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:enersense/providers/savings_provider.dart';
import 'package:enersense/widgets/recommendation_card.dart';
import 'package:enersense/widgets/chart_helpers.dart';
import 'package:enersense/theme.dart';

class SavingsScreen extends StatefulWidget {
  const SavingsScreen({super.key});

  @override
  State<SavingsScreen> createState() => _SavingsScreenState();
}

class _SavingsScreenState extends State<SavingsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<SavingsProvider>().fetchSavings();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: _buildGlassAppBar(),
      body: _buildGradientBackground(
        child: Consumer<SavingsProvider>(
          builder: (context, savingsProvider, child) {
            if (savingsProvider.isLoading &&
                savingsProvider.recommendations.isEmpty) {
              return _buildLoadingState();
            }

            return RefreshIndicator(
              onRefresh: () => savingsProvider.fetchSavings(),
              backgroundColor: Colors.white.withOpacity(0.1),
              color: AppTheme.primaryBlue,
              child: SingleChildScrollView(
                physics: AlwaysScrollableScrollPhysics(),
                padding: EdgeInsets.fromLTRB(16, 100, 16, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSavingsIntelligenceCard(savingsProvider),
                    SizedBox(height: 24),
                    _buildWhatIfSimulatorCard(savingsProvider),
                    SizedBox(height: 24),
                    _buildSectionHeader('Smart recommendations',
                        'Your feedback improves future suggestions'),
                    SizedBox(height: 16),
                    ...savingsProvider.pendingRecommendations.map((rec) {
                      return RecommendationCard(
                        recommendation: rec,
                        onAccept: () {
                          context
                              .read<SavingsProvider>()
                              .acceptRecommendation(rec.id);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Recommendation accepted!'),
                              backgroundColor: AppTheme.successGreen,
                            ),
                          );
                        },
                        onReject: () {
                          context
                              .read<SavingsProvider>()
                              .rejectRecommendation(rec.id);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Recommendation rejected'),
                              backgroundColor: Colors.grey,
                            ),
                          );
                        },
                      );
                    }),
                    if (savingsProvider.recommendations
                        .any((r) => r.accepted || r.rejected))
                      Padding(
                        padding: EdgeInsets.only(top: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Previous feedback',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                            SizedBox(height: 12),
                            ...savingsProvider.recommendations
                                .where((r) => r.accepted || r.rejected)
                                .map((rec) {
                              return RecommendationCard(
                                recommendation: rec,
                                onAccept: () {},
                                onReject: () {},
                                isCompact: true,
                              );
                            }),
                          ],
                        ),
                      ),
                    SizedBox(height: 32),
                    _buildApplianceROICard(),
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
                      'Savings',
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
                          Icons.savings_outlined,
                          color: AppTheme.successGreen,
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
            'Loading savings data...',
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

  Widget _buildSavingsIntelligenceCard(SavingsProvider savingsProvider) {
    return _buildGlassContainer(
      width: double.infinity,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppTheme.successGreen.withOpacity(0.2),
                  ),
                  child: Center(
                    child: Icon(Icons.savings,
                        color: AppTheme.successGreen, size: 18),
                  ),
                ),
                SizedBox(width: 12),
                Text(
                  'Savings intelligence',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            Text(
              savingsProvider.formattedTotalSaved,
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppTheme.successGreen,
              ),
            ),
            SizedBox(height: 4),
            Text(
              'Projected yearly savings: ${savingsProvider.formattedMonthlyProjection} with current accepted automations.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            SizedBox(height: 16),
            SizedBox(
              height: 120,
              child: BarChartHelper.buildSavingsChart([
                18.5,
                21.3,
                19.8,
                23.5,
                25.2,
                22.1,
                26.4,
                28.3,
              ]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWhatIfSimulatorCard(SavingsProvider savingsProvider) {
    return _buildGlassContainer(
      width: double.infinity,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'What-if simulator',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Reduce evening load by:',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            SizedBox(height: 16),
            Slider(
              value: savingsProvider.eveningLoadAdjustment,
              onChanged: (value) {
                context
                    .read<SavingsProvider>()
                    .updateEveningLoadAdjustment(value);
              },
              min: -100,
              max: 100,
              divisions: 20,
              label:
                  '${savingsProvider.eveningLoadAdjustment.toStringAsFixed(0)}%',
              activeColor: AppTheme.successGreen,
              inactiveColor: Colors.white.withOpacity(0.2),
            ),
            SizedBox(height: 16),
            Text(
              'Estimated savings: ${savingsProvider.formattedEstimatedSavings}',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppTheme.successGreen,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildApplianceROICard() {
    return _buildGlassContainer(
      width: double.infinity,
      glassColor: AppTheme.primaryBlue.withOpacity(0.08),
      borderColor: AppTheme.primaryBlue.withOpacity(0.3),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Appliance ROI',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
                color: AppTheme.primaryBlue,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'AI replacement analysis',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.textGrey,
              ),
            ),
            SizedBox(height: 12),
            _buildROIRow(
              'Inverter AC',
              'RM 3,500',
              'Payback 14 mo',
              'Replacing the bedroom AC could reduce\ncooling energy by 28%.',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildROIRow(
    String appliance,
    String cost,
    String payback,
    String description,
  ) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                appliance,
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
              ),
              SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(fontSize: 12, color: AppTheme.textGrey),
              ),
            ],
          ),
        ),
        SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              cost,
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 4),
            Text(
              payback,
              style: TextStyle(fontSize: 12, color: AppTheme.textGrey),
            ),
          ],
        ),
      ],
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
