import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:enersense/models/household_profile.dart';
import 'package:enersense/providers/household_profile_provider.dart';
import 'package:enersense/theme.dart';

class HouseholdProfileCard extends StatefulWidget {
  const HouseholdProfileCard({super.key});

  @override
  State<HouseholdProfileCard> createState() =>
      _HouseholdProfileCardState();
}

class _HouseholdProfileCardState extends State<HouseholdProfileCard>
    with SingleTickerProviderStateMixin {
  late TextEditingController _budgetController;
  late HouseholdProfile _editingProfile;
  late HouseholdProfile _originalProfile;
  late AnimationController _animationController;
  bool _isEditing = false;

  final List<String> _householdSizeOptions = [
    '1 Person',
    '2-3 People',
    '4-5 People',
    '6+ People',
  ];

  final List<String> _homeTypeOptions = [
    'Apartment / Condo',
    'Terrace House',
    'Semi-Detached',
    'Detached House',
  ];

  final List<String> _applianceOptions = [
    'Air Conditioner',
    'Water Heater',
    'Refrigerator',
    'Washing Machine',
    'Television',
    'Electric Oven',
    'Desktop PC',
  ];

  final List<String> _occupancyOptions = [
    'Morning',
    'Afternoon',
    'Evening',
    'Night',
    'All Day',
  ];

  @override
  void initState() {
    super.initState();
    _budgetController = TextEditingController();
    _editingProfile = HouseholdProfile.createDefault();
    _originalProfile = HouseholdProfile.createDefault();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final provider = context.read<HouseholdProfileProvider>();
    if (provider.profile != null) {
      _editingProfile = provider.profile!;
      _originalProfile = provider.profile!;
      _budgetController.text = _editingProfile.monthlyBudget.toString();
    }
  }

  @override
  void dispose() {
    _budgetController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  void _toggleEdit() {
    setState(() {
      _isEditing = !_isEditing;
    });
    if (_isEditing) {
      _animationController.forward();
    } else {
      _animationController.reverse();
    }
  }

  void _cancelEdit() {
    setState(() {
      _isEditing = false;
      _editingProfile = _originalProfile;
      _budgetController.text = _originalProfile.monthlyBudget.toString();
    });
    _animationController.reverse();
  }

  String? _validateBudget(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter a monthly budget';
    }
    final budget = double.tryParse(value);
    if (budget == null) {
      return 'Please enter a valid number';
    }
    if (budget < 0) {
      return 'Budget must be a positive number';
    }
    return null;
  }

  Future<void> _saveProfile() async {
    // Validate budget
    if (_budgetController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a monthly budget')),
      );
      return;
    }

    final budget = double.tryParse(_budgetController.text);
    if (budget == null || budget < 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid budget amount')),
      );
      return;
    }

    // Validate at least one appliance is selected
    if (_editingProfile.appliances.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one appliance')),
      );
      return;
    }

    // Update budget in profile
    _editingProfile = _editingProfile.copyWith(monthlyBudget: budget);

    // Save to provider and API
    final provider = context.read<HouseholdProfileProvider>();
    final success = await provider.saveProfile(_editingProfile);

    if (mounted) {
      if (success) {
        // Update original profile
        setState(() {
          _originalProfile = _editingProfile;
          _isEditing = false;
        });
        _animationController.reverse();

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✓ Profile saved successfully'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save profile: ${provider.error}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<HouseholdProfileProvider>(
      builder: (context, provider, child) {
        if (provider.profile != null &&
            _originalProfile.householdSize == 'Loading') {
          _originalProfile = provider.profile!;
          _editingProfile = provider.profile!;
          _budgetController.text = provider.profile!.monthlyBudget.toString();
        }

        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.9),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.white.withOpacity(0.3),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.08),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header with title and edit button
                _buildCardHeader(provider),
                const SizedBox(height: 16),

                // Content: Summary or Edit Form
                _isEditing
                    ? _buildEditForm(provider)
                    : _buildSummary(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCardHeader(HouseholdProfileProvider provider) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Household Profile',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textDark,
          ),
        ),
        if (!_isEditing)
          GestureDetector(
            onTap: _toggleEdit,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: AppTheme.primaryBlue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.edit,
                    size: 16,
                    color: AppTheme.primaryBlue,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Edit',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.primaryBlue,
                    ),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildSummary() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSummaryRow('Household Size', _originalProfile.householdSize),
        const SizedBox(height: 12),
        _buildSummaryRow('Home Type', _originalProfile.homeType),
        const SizedBox(height: 12),
        _buildSummaryRow('Occupancy', _originalProfile.occupancy),
        const SizedBox(height: 12),
        _buildSummaryRow('Monthly Budget', 'RM${_originalProfile.monthlyBudget}'),
      ],
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 13,
            color: AppTheme.textGrey,
            fontWeight: FontWeight.w500,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            color: AppTheme.textDark,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildEditForm(HouseholdProfileProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Household Size Dropdown
        _buildDropdownField(
          label: 'Household Size',
          value: _editingProfile.householdSize,
          options: _householdSizeOptions,
          onChanged: (value) {
            setState(() {
              _editingProfile =
                  _editingProfile.copyWith(householdSize: value);
            });
          },
        ),
        const SizedBox(height: 18),

        // Home Type Dropdown
        _buildDropdownField(
          label: 'Home Type',
          value: _editingProfile.homeType,
          options: _homeTypeOptions,
          onChanged: (value) {
            setState(() {
              _editingProfile = _editingProfile.copyWith(homeType: value);
            });
          },
        ),
        const SizedBox(height: 18),

        // Main Appliances Multi-select
        _buildAppliancesSection(),
        const SizedBox(height: 18),

        // Typical Occupancy Dropdown
        _buildDropdownField(
          label: 'Typical Occupancy',
          value: _editingProfile.occupancy,
          options: _occupancyOptions,
          onChanged: (value) {
            setState(() {
              _editingProfile = _editingProfile.copyWith(occupancy: value);
            });
          },
        ),
        const SizedBox(height: 18),

        // Monthly Budget TextField
        _buildBudgetField(),
        const SizedBox(height: 20),

        // Action Buttons
        _buildActionButtons(provider),
      ],
    );
  }

  Widget _buildDropdownField({
    required String label,
    required String value,
    required List<String> options,
    required Function(String) onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: AppTheme.textDark,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(8),
          ),
          child: DropdownButton<String>(
            value: value,
            onChanged: (newValue) {
              if (newValue != null) {
                onChanged(newValue);
              }
            },
            isExpanded: true,
            underline: const SizedBox(),
            items: options.map((String option) {
              return DropdownMenuItem<String>(
                value: option,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Text(
                    option,
                    style: const TextStyle(fontSize: 13),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildAppliancesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Main Appliances',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: AppTheme.textDark,
          ),
        ),
        const SizedBox(height: 10),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(8),
            color: Colors.grey[50],
          ),
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: Column(
              children: _applianceOptions.map((appliance) {
                final isSelected =
                    _editingProfile.appliances.contains(appliance);
                return CheckboxListTile(
                  value: isSelected,
                  onChanged: (bool? newValue) {
                    setState(() {
                      if (newValue == true) {
                        _editingProfile = _editingProfile.copyWith(
                          appliances: [
                            ..._editingProfile.appliances,
                            appliance
                          ],
                        );
                      } else {
                        _editingProfile = _editingProfile.copyWith(
                          appliances: _editingProfile.appliances
                              .where((a) => a != appliance)
                              .toList(),
                        );
                      }
                    });
                  },
                  title: Text(
                    appliance,
                    style: const TextStyle(fontSize: 12),
                  ),
                  contentPadding: EdgeInsets.zero,
                  dense: true,
                  activeColor: AppTheme.primaryBlue,
                );
              }).toList(),
            ),
          ),
        ),
        if (_editingProfile.appliances.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              'Please select at least one appliance',
              style: TextStyle(
                fontSize: 11,
                color: Colors.red[600],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildBudgetField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Monthly Electricity Budget (RM)',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: AppTheme.textDark,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _budgetController,
          keyboardType: TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(
            hintText: 'Enter amount in RM',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: AppTheme.primaryBlue, width: 2),
            ),
            prefixText: 'RM ',
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            isDense: true,
          ),
          onChanged: (value) {
            setState(() {});
          },
        ),
        if (_validateBudget(_budgetController.text) != null)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(
              _validateBudget(_budgetController.text)!,
              style: TextStyle(
                fontSize: 11,
                color: Colors.red[600],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildActionButtons(HouseholdProfileProvider provider) {
    return Row(
      children: [
        // Cancel Button
        Expanded(
          child: OutlinedButton(
            onPressed: provider.isSaving ? null : _cancelEdit,
            style: OutlinedButton.styleFrom(
              side: BorderSide(
                color: Colors.grey[300]!,
                width: 1,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
            child: Text(
              'Cancel',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppTheme.textDark,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),

        // Save Button
        Expanded(
          child: ElevatedButton(
            onPressed: provider.isSaving ? null : _saveProfile,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryBlue,
              disabledBackgroundColor: Colors.grey[300],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              elevation: 0,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
            child: provider.isSaving
                ? SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor:
                          AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Text(
                    'Save',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
          ),
        ),
      ],
    );
  }
}
