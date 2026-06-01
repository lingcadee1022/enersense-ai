import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:enersense/providers/profile_provider.dart';
import 'package:enersense/theme.dart';
import 'package:enersense/widgets/household_profile_section.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: _buildGlassAppBar(context),
      body: _buildGradientBackground(
        child: Consumer<ProfileProvider>(
          builder: (context, profileProvider, child) {
            if (profileProvider.isLoading || profileProvider.profile == null) {
              return _buildLoadingState();
            }

            final profile = profileProvider.profile!;

            return SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(16, 100, 16, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Household Profile Card at the TOP
                  HouseholdProfileCard(),
                  SizedBox(height: 28),
                  _buildSectionHeader('AI personalization', ''),
                  SizedBox(height: 16),
                  _buildComfortCard(context, profile),
                  SizedBox(height: 16),
                  _buildAutomationCard(context, profile),
                  SizedBox(height: 16),
                  _buildLearningCard(profile),
                  SizedBox(height: 28),
                  _buildSectionHeader('Eco score', ''),
                  SizedBox(height: 16),
                  _buildEcoScoreCard(context, profile, profileProvider),
                  SizedBox(height: 28),
                  _buildSectionHeader('Achievements', ''),
                  SizedBox(height: 16),
                  _buildAchievementBadges(profile),
                  SizedBox(height: 28),

                  _buildAlertsCard(context),
                  SizedBox(height: 28),
                  _buildConnectedAppliancesCard(context),
                  SizedBox(height: 28),
                  _buildHouseholdMembersCard(context),
                  SizedBox(height: 28),
                  _buildNotificationSettingsCard(context),
                  SizedBox(height: 28),
                  _buildExportDataCard(context),
                  SizedBox(height: 28),
                  _buildSupportCard(context),
                  SizedBox(height: 20),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  PreferredSizeWidget _buildGlassAppBar(BuildContext context) {
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
                      'Profile',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(
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
                          Icons.person_outline,
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
      child: CircularProgressIndicator(
        valueColor:
            AlwaysStoppedAnimation<Color>(AppTheme.primaryBlue),
      ),
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textDark,
          ),
        ),
      ],
    );
  }

  Widget _buildComfortCard(BuildContext context, dynamic profile) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Comfort vs saving',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 16),
            Slider(
              value: profile.comfortLevel,
              onChanged: (value) {
                (context).read<ProfileProvider>().updateComfortLevel(value);
              },
              min: 0,
              max: 100,
              divisions: 10,
              activeColor: AppTheme.primaryBlue,
              inactiveColor: Colors.white.withOpacity(0.2),
              label: profile.comfortPreference,
            ),
            SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Save more',
                  style: TextStyle(fontSize: 12, color: AppTheme.textGrey),
                ),
                Text(
                  profile.comfortPreference,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.primaryBlue,
                  ),
                ),
                Text(
                  'Comfort',
                  style: TextStyle(fontSize: 12, color: AppTheme.textGrey),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAutomationCard(BuildContext context, dynamic profile) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Automation suggestions',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                SizedBox(height: 4),
                Text(
                  'Get smart recommendations',
                  style: TextStyle(fontSize: 12, color: AppTheme.textGrey),
                ),
              ],
            ),
            Switch(
              value: profile.automationEnabled,
              onChanged: (_) =>
                  (context).read<ProfileProvider>().toggleAutomation(),
              activeTrackColor:
                  AppTheme.primaryBlue.withOpacity(0.3),
              activeThumbColor: AppTheme.primaryBlue,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLearningCard(dynamic profile) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Learning status',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 8),
            Text(
              'Improved from ${profile.feedbackSignals} feedback signals',
              style: TextStyle(fontSize: 12, color: AppTheme.textGrey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEcoScoreCard(BuildContext context, dynamic profile,
      ProfileProvider profileProvider) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 100,
                  height: 100,
                  child: CircularProgressIndicator(
                    value: profile.ecoScore / 100,
                    strokeWidth: 8,
                    backgroundColor: Colors.white.withOpacity(0.2),
                    valueColor: AlwaysStoppedAnimation<Color>(
                      AppTheme.successGreen,
                    ),
                  ),
                ),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      profileProvider.formattedEcoScore,
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.successGreen,
                      ),
                    ),
                    Text(
                      'Eco Hero progress',
                      style: TextStyle(fontSize: 11, color: AppTheme.textGrey),
                    ),
                  ],
                ),
              ],
            ),
            SizedBox(height: 16),
            Text(
              'CO₂ reduction: 42 kg this month',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAchievementBadges(dynamic profile) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        ...profile.badges.map((badge) {
          return _buildGlassContainer(
            borderRadius: 20,
            glassColor: _getBadgeColor(badge).withOpacity(0.3),
            borderColor: _getBadgeColor(badge).withOpacity(0.4),
            child: Padding(
              padding:
                  EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    _getBadgeIcon(badge),
                    style: TextStyle(fontSize: 14),
                  ),
                  SizedBox(width: 4),
                  Text(
                    badge,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textDark,
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildAlertsCard(BuildContext context) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Alerts',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 12),
            _buildAlertItem(
              Icons.notifications,
              'Daily insights',
              'Enabled',
              Colors.green,
            ),
            _buildAlertItem(
              Icons.warning,
              'Anomaly alerts',
              'Enabled',
              Colors.green,
            ),
            _buildAlertItem(
              Icons.trending_down,
              'Savings tips',
              'Enabled',
              Colors.green,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertItem(
    IconData icon,
    String title,
    String status,
    Color statusColor,
  ) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 18, color: AppTheme.textGrey),
          SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: TextStyle(fontSize: 13, color: AppTheme.textDark),
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: statusColor.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Text(
              status,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: statusColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConnectedAppliancesCard(BuildContext context) {
    final applianceList = [
      {'name': 'Air Conditioner', 'status': 'Connected', 'usage': '2.5 kW'},
      {'name': 'Refrigerator', 'status': 'Connected', 'usage': '0.8 kW'},
      {'name': 'Washing Machine', 'status': 'Connected', 'usage': '2.2 kW'},
      {'name': 'Television', 'status': 'Connected', 'usage': '0.3 kW'},
    ];

    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Connected Appliances',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 12),
            ...applianceList.map((appliance) {
              return Padding(
                padding: EdgeInsets.only(bottom: 10),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          appliance['name']!,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            color: AppTheme.textDark,
                          ),
                        ),
                        Text(
                          appliance['usage']!,
                          style: TextStyle(
                            fontSize: 11,
                            color: AppTheme.textGrey,
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.successGreen.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                          color: AppTheme.successGreen.withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: Text(
                        appliance['status']!,
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.successGreen,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildHouseholdMembersCard(BuildContext context) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Household Members',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppTheme.primaryBlue.withOpacity(0.2),
                    border: Border.all(
                      color: AppTheme.primaryBlue.withOpacity(0.3),
                    ),
                  ),
                  child: Center(
                    child: Icon(
                      Icons.add,
                      size: 14,
                      color: AppTheme.primaryBlue,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMemberAvatar('You', 'Admin', Colors.blue),
                _buildMemberAvatar('Sarah', 'Member', Colors.pink),
                _buildMemberAvatar('John', 'Member', Colors.green),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMemberAvatar(String name, String role, Color color) {
    return Column(
      children: [
        Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withOpacity(0.2),
            border: Border.all(
              color: color.withOpacity(0.3),
              width: 2,
            ),
          ),
          child: Center(
            child: Text(
              name[0],
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ),
        SizedBox(height: 8),
        Text(
          name,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: AppTheme.textDark,
          ),
        ),
        Text(
          role,
          style: TextStyle(
            fontSize: 9,
            color: AppTheme.textGrey,
          ),
        ),
      ],
    );
  }

  Widget _buildNotificationSettingsCard(BuildContext context) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Notification Preferences',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 12),
            _buildNotificationToggle(
              'Push Notifications',
              'Real-time alerts',
              true,
            ),
            _buildNotificationToggle(
              'Email Digest',
              'Weekly summaries',
              true,
            ),
            _buildNotificationToggle(
              'SMS Alerts',
              'Critical anomalies',
              false,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationToggle(
    String title,
    String subtitle,
    bool value,
  ) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.textDark,
                ),
              ),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 11,
                  color: AppTheme.textGrey,
                ),
              ),
            ],
          ),
          Switch(
            value: value,
            onChanged: (_) {},
            activeThumbColor: AppTheme.primaryBlue,
            activeTrackColor: AppTheme.primaryBlue.withOpacity(0.3),
          ),
        ],
      ),
    );
  }

  Widget _buildExportDataCard(BuildContext context) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Data Management',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () {},
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryBlue.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: AppTheme.primaryBlue.withOpacity(0.3),
                          ),
                        ),
                        child: Column(
                          children: [
                            Icon(
                              Icons.download,
                              color: AppTheme.primaryBlue,
                              size: 20,
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Export CSV',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: AppTheme.primaryBlue,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () {},
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.successGreen.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: AppTheme.successGreen.withOpacity(0.3),
                          ),
                        ),
                        child: Column(
                          children: [
                            Icon(
                              Icons.share,
                              color: AppTheme.successGreen,
                              size: 20,
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Share Report',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: AppTheme.successGreen,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportCard(BuildContext context) {
    return _buildGlassContainer(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Support & Settings',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            SizedBox(height: 12),
            _buildSupportOption(
              Icons.help_outline,
              'Help Center',
              'FAQs and guides',
            ),
            _buildSupportOption(
              Icons.info_outline,
              'About App',
              'Version 1.0.0',
            ),
            _buildSupportOption(
              Icons.privacy_tip_outlined,
              'Privacy Policy',
              'Data protection',
            ),
            _buildSupportOption(
              Icons.logout,
              'Logout',
              'Sign out of account',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportOption(
    IconData icon,
    String title,
    String subtitle,
  ) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {},
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: EdgeInsets.symmetric(vertical: 8, horizontal: 8),
          child: Row(
            children: [
              Icon(
                icon,
                size: 18,
                color: AppTheme.primaryBlue,
              ),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.textDark,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 11,
                        color: AppTheme.textGrey,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                size: 18,
                color: AppTheme.textGrey,
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

  String _getBadgeIcon(String badge) {
    switch (badge) {
      case 'Energy Saver':
        return '💰';
      case 'Peak Shifter':
        return '⏰';
      case 'Eco Hero':
        return '🌱';
      default:
        return '⭐';
    }
  }

  Color _getBadgeColor(String badge) {
    switch (badge) {
      case 'Energy Saver':
        return Color(0xFFFFC107);
      case 'Peak Shifter':
        return AppTheme.primaryBlue;
      case 'Eco Hero':
        return AppTheme.successGreen;
      default:
        return Color(0xFF9C27B0);
    }
  }
}
