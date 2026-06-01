import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:enersense/providers/energy_provider.dart';
import 'package:enersense/theme.dart';
import 'package:enersense/widgets/chart_helpers.dart';
import 'package:enersense/widgets/anomaly_alert_dialog.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin, WidgetsBindingObserver {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late bool _showAnomalyAlert;

  @override
  void initState() {
    super.initState();
    _showAnomalyAlert = true; // Demo mode: always show by default
    WidgetsBinding.instance.addObserver(this);
    _initializeAnimations();
    Future.microtask(() {
      context.read<EnergyProvider>().fetchLiveUsage();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _animationController.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      // Reset alert to show again when app comes to foreground
      setState(() {
        _showAnomalyAlert = true;
      });
    }
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );

    _slideAnimation = Tween<Offset>(begin: const Offset(0, 0.2), end: Offset.zero)
        .animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutCubic),
    );

    _animationController.forward();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: _buildGlassAppBar(),
      body: _buildGradientBackground(
        child: Stack(
          children: [
            Consumer<EnergyProvider>(
              builder: (context, energyProvider, child) =>
                  _buildContent(context, energyProvider),
            ),
            // Anomaly Alert Dialog Overlay
            Consumer<EnergyProvider>(
              builder: (context, energyProvider, child) {
                final reading = energyProvider.currentReading;
                // Show alert whenever there's an anomaly and it hasn't been dismissed
                final showAlert = _showAnomalyAlert &&
                    reading != null &&
                    reading.isAnomaly;

                return AnomalyAlertDialog(
                  isVisible: showAlert,
                  onResolve: () {
                    setState(() {
                      _showAnomalyAlert = false;
                    });
                  },
                  onIgnore: () {
                    setState(() {
                      _showAnomalyAlert = false;
                    });
                  },
                );
              },
            ),
          ],
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
              color: Colors.white.withValues(alpha: 25),
              border: Border(
                bottom: BorderSide(
                  color: Colors.white.withValues(alpha: 51),
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
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'EnersenseAI',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: Colors.black,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'Energy Insights',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.black26.withValues(alpha: 179),
                          ),
                        ),
                      ],
                    ),
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white.withValues(alpha: 25),
                        border: Border.all(
                          color: AppTheme.borderGrey,
                          width: 1,
                        ),
                      ),
                      child: Center(
                        child: Icon(
                          Icons.settings_outlined,
                          color: AppTheme.textDark,
                          size: 20,
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

  Widget _buildContent(BuildContext context, EnergyProvider energyProvider) {
    if (energyProvider.isLoading && energyProvider.currentReading == null) {
      return _buildLoadingState();
    }

    final reading = energyProvider.currentReading;
    if (reading == null) {
      return _buildErrorState(context, energyProvider);
    }

    return RefreshIndicator(
      onRefresh: () => energyProvider.fetchLiveUsage(),
      backgroundColor: AppTheme.bgLight,
      color: AppTheme.primaryBlue,
      child: SlideTransition(
        position: _slideAnimation,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(16, 100, 16, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLiveUsageGlassCard(reading),
                const SizedBox(height: 20),
                _buildQuickActionsCard(context),
                const SizedBox(height: 24),
                _buildStatsRow(reading),
                const SizedBox(height: 28),
                _buildChartSection(context),
                const SizedBox(height: 28),
                if (reading.isAnomaly) ...[
                  _buildAnomalyAlert(reading),
                  const SizedBox(height: 24),
                ],
                // Attribution text
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Center(
                    child: Text(
                      'by xm.um.com',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textGrey.withValues(alpha: 128),
                        fontWeight: FontWeight.w400,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
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
            child: const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryBlue),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Loading your energy data...',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppTheme.textDark,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, EnergyProvider energyProvider) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildGlassContainer(
              width: 100,
              height: 100,
              borderRadius: 50,
              glassColor: AppTheme.errorRed.withValues(alpha: 25),
              borderColor: AppTheme.errorRed.withValues(alpha: 76),
              child: Center(
                child: Icon(
                  Icons.error_outline,
                  size: 48,
                  color: AppTheme.errorRed,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Unable to Load Data',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: AppTheme.textDark,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Please check your connection and try again',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppTheme.textGrey,
              ),
            ),
            const SizedBox(height: 28),
            _buildGlassButton(
              onPressed: () => energyProvider.fetchLiveUsage(),
              label: 'Try Again',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLiveUsageGlassCard(dynamic reading) {
    return _buildGlassContainer(
      width: double.infinity,
      borderRadius: 30,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Live Usage',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: AppTheme.textDark,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 128),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: AppTheme.borderGrey,
                      width: 1,
                    ),
                  ),
                  child: Text(
                    'Real-time',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: AppTheme.textGrey,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  reading.formattedPower ?? 'N/A',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    color: AppTheme.primaryBlue,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(
                      Icons.trending_down,
                      size: 16,
                      color: AppTheme.successGreen,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${reading.differencePercentage.toStringAsFixed(0)}% vs yesterday',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: AppTheme.successGreen,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),
            Container(
              height: 1,
              color: AppTheme.borderGrey,
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildInfoWidget(
                  context,
                  'Estimated Bill',
                  reading.formattedBill ?? 'N/A',
                  Icons.credit_card,
                  Colors.blue.shade300,
                ),
                _buildInfoWidget(
                  context,
                  'Top Appliance',
                  reading.predictedAppliance ?? 'N/A',
                  Icons.electrical_services,
                  Colors.orange.shade300,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoWidget(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 8),
              Text(
                label,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: AppTheme.textGrey,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              color: AppTheme.textDark,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsRow(dynamic reading) {
    return Row(
      children: [
        Expanded(
          child: FadeTransition(
            opacity: _fadeAnimation,
            child: _buildStatGlassCard(
              context: context,
              value: reading.formattedCost ?? 'N/A',
              label: 'Cost Today',
              subLabel: '-9% vs yesterday',
              icon: Icons.trending_down,
              iconColor: Colors.green.shade300,
              gradientStart: const Color(0xFF00BF6F),
              gradientEnd: const Color(0xFF009E49),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: FadeTransition(
            opacity: _fadeAnimation,
            child: _buildStatGlassCard(
              context: context,
              value: reading.formattedCarbon ?? 'N/A',
              label: 'Carbon',
              subLabel: 'CO₂ tracked',
              icon: Icons.eco,
              iconColor: Colors.cyan.shade300,
              gradientStart: const Color(0xFF00BCD4),
              gradientEnd: const Color(0xFF0097A7),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatGlassCard({
    required BuildContext context,
    required String value,
    required String label,
    required String subLabel,
    required IconData icon,
    required Color iconColor,
    required Color gradientStart,
    required Color gradientEnd,
  }) {
    return _buildGlassContainer(
      borderRadius: 20,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [gradientStart, gradientEnd],
                    ),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Icon(icon, color: Colors.white, size: 18),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: AppTheme.primaryBlue,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: AppTheme.textGrey,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              subLabel,
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: AppTheme.textGrey,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Usage Trend',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            color: AppTheme.textDark,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'NILM estimate from your smart meter',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: AppTheme.textGrey,
          ),
        ),
        const SizedBox(height: 16),
        _buildGlassContainer(
          width: double.infinity,
          height: 240,
          borderRadius: 24,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: LineChartHelper.buildHourlyChart([
              5.2,
              6.1,
              7.8,
              12.5,
              18.3,
              22.1,
              19.5,
            ]),
          ),
        ),
      ],
    );
  }

  Widget _buildAnomalyAlert(dynamic reading) {
    return _buildGlassContainer(
      width: double.infinity,
      borderRadius: 20,
      glassColor: AppTheme.errorRed.withValues(alpha: 25),
      borderColor: AppTheme.errorRed.withValues(alpha: 76),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.errorRed.withValues(alpha: 51),
              ),
              child: Center(
                child: Icon(
                  Icons.warning_rounded,
                  color: AppTheme.errorRed,
                  size: 20,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Anomaly Detected',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: AppTheme.errorRed,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    reading.anomalyInsight ?? 'Unusual pattern detected',
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
    );
  }

  Widget _buildQuickActionsCard(BuildContext context) {
    return SizedBox(
      height: 100,
      child: Row(
        children: [
          Expanded(
            child: _buildQuickActionButton(
              context,
              Icons.eco_outlined,
              'Eco Mode',
              Colors.green,
              () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Eco Mode activated - reducing non-essential loads'),
                  duration: Duration(seconds: 2),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildQuickActionButton(
              context,
              Icons.schedule,
              'Schedule',
              AppTheme.primaryBlue,
              () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Open scheduling assistant in Chat'),
                  duration: Duration(seconds: 2),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildQuickActionButton(
              context,
              Icons.flash_on,
              'Top Load',
              Colors.orange,
              () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Managing top appliance - AC optimized'),
                  duration: Duration(seconds: 2),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton(
    BuildContext context,
    IconData icon,
    String label,
    Color color,
    VoidCallback onPressed,
  ) {
    return _buildGlassContainer(
      borderRadius: 16,
      glassColor: color.withValues(alpha: 20),
      borderColor: color.withValues(alpha: 51),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(height: 6),
              Text(
                label,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: AppTheme.textDark,
                  fontWeight: FontWeight.w600,
                  fontSize: 11,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper Methods
  Widget _buildGlassContainer({
    double? width,
    double? height,
    double borderRadius = 20,
    Color? glassColor,
    Color? borderColor,
    required Widget child,
  }) {
    final backgroundColor = glassColor ?? Colors.white.withValues(alpha: 179);
    final borderCol = borderColor ?? AppTheme.borderGrey;

    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
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

  Widget _buildGlassButton({
    required VoidCallback onPressed,
    required String label,
  }) {
    return _buildGlassContainer(
      width: double.infinity,
      height: 50,
      borderRadius: 25,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          child: Center(
            child: Text(
              label,
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: AppTheme.primaryBlue,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
