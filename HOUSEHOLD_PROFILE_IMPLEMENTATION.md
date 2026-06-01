# Household Profile Feature - Implementation Guide

## Overview
A complete "Household Profile" section has been successfully added to the EnerSense AI Flutter app. This feature allows users to input and manage their household information, appliances, and electricity budget preferences.

## Architecture

### Backend (Python/FastAPI)

#### 1. **Models** (`backend/api/models.py`)
Added two Pydantic models:

- **`HouseholdProfileRequest`**: Request model for receiving household profile data from the client
  - `household_size`: String (Household size category)
  - `home_type`: String (Type of home)
  - `appliances`: List[String] (Selected appliances)
  - `occupancy`: String (Typical occupancy period)
  - `monthly_budget`: float (Monthly budget in RM)

- **`HouseholdProfileResponse`**: Response model for sending household profile data to client
  - All fields from request + `created_at` and `updated_at` timestamps

#### 2. **Database Operations** (`backend/db/mongo.py`)
Added three new methods to `MongoDBClient`:

- **`insert_household_profile(profile_doc)`**: Inserts a new household profile into the database
- **`get_household_profile(user_id)`**: Retrieves household profile for a user
- **`update_household_profile(user_id, profile_data)`**: Updates existing household profile

Also added:
- Index on `household_profiles.user_id` (unique)
- Health check includes `household_profiles_count`

#### 3. **API Endpoints** (`backend/api/profile.py`) - NEW FILE
Created complete profile endpoints:

**GET `/api/v1/profile`**
- Returns user's household profile
- Returns default profile if not found
- Handles errors gracefully

**POST `/api/v1/profile`**
- Saves or updates household profile
- Validates appliances list is not empty
- Validates monthly budget is positive
- Returns success confirmation with timestamp

#### 4. **Router Registration** (`backend/main.py`)
- Imported profile router
- Registered profile router in FastAPI app
- Now accessible at `/api/v1/profile`

### Frontend (Flutter/Dart)

#### 1. **Data Model** (`lib/models/household_profile.dart`) - NEW FILE
`HouseholdProfile` model with:
- Properties for all household information
- `fromJson()` factory for parsing API responses
- `toJson()` for serializing to API requests
- `copyWith()` for immutable updates
- `createDefault()` factory for default values

#### 2. **API Service** (`lib/services/api_service.dart`)
Added two new methods:

- **`getHouseholdProfile()`**: Fetches household profile from API
  - Falls back to default profile if network fails
  
- **`saveHouseholdProfile(profile)`**: Sends profile to API for saving
  - Returns boolean success status

#### 3. **State Management** (`lib/providers/household_profile_provider.dart`) - NEW FILE
`HouseholdProfileProvider` (extends ChangeNotifier) with:

**Core Methods:**
- `saveProfile(profile)`: Saves profile and handles UI state
- `refreshProfile()`: Reloads from API

**Update Methods:**
- `updateHouseholdSize(size)`
- `updateHomeType(type)`
- `updateAppliances(appliances)`
- `updateOccupancy(occupancy)`
- `updateMonthlyBudget(budget)`
- `addAppliance(appliance)` / `removeAppliance(appliance)` / `toggleAppliance(appliance)`

**State Properties:**
- `profile`: Current household profile
- `isLoading`: Loading state for initial load
- `isSaving`: Loading state for save operation
- `error`: Error message if any

#### 4. **UI Widget** (`lib/widgets/household_profile_section.dart`) - NEW FILE
`HouseholdProfileSection` stateful widget with:

**Form Fields:**
1. **Household Size Dropdown**
   - Options: 1 Person, 2-3 People, 4-5 People, 6+ People

2. **Home Type Dropdown**
   - Options: Apartment/Condo, Terrace House, Semi-Detached, Detached House

3. **Main Appliances Multi-select Checkboxes**
   - Air Conditioner
   - Water Heater
   - Refrigerator
   - Washing Machine
   - Television
   - Electric Oven
   - Desktop PC
   - Validation: At least one appliance required

4. **Typical Occupancy Dropdown**
   - Options: Morning, Afternoon, Evening, Night, All Day

5. **Monthly Electricity Budget TextField**
   - Numeric input with "RM" prefix
   - Validation: Positive numbers only
   - Error message display

**Features:**
- Material Design UI with modern card layout
- Rounded corners (16dp)
- Glass morphism effect (semi-transparent white background)
- Responsive for mobile screens
- Loading indicator on Save button during API call
- Success/error snackbars for user feedback
- Form validation with inline error messages
- State management integration

#### 5. **Main App Integration** (`lib/main.dart`)
- Added import for `HouseholdProfileProvider`
- Added `HouseholdProfileProvider` to MultiProvider setup
- Uses `ChangeNotifierProxyProvider` pattern with ApiService dependency

#### 6. **Profile Screen Integration** (`lib/screens/profile_screen.dart`)
- Imported `HouseholdProfileSection` widget
- Added household profile section to profile page
- Positioned after Achievements section
- Displayed within scrollable content area with proper spacing

## Data Flow

### Loading Profile
1. App starts → MultiProvider creates providers
2. `HouseholdProfileProvider` initializes → calls `_loadProfile()`
3. API call: GET `/api/v1/profile`
4. Response parsed to `HouseholdProfile` object
5. UI updates via Consumer widget

### Saving Profile
1. User fills form and clicks "Save Profile"
2. Form validation performed (budget positive, appliances selected)
3. `HouseholdProfileProvider.saveProfile()` called
4. API call: POST `/api/v1/profile` with profile data
5. Loading indicator shown
6. On success: snackbar shown, profile updated in state
7. On error: error snackbar shown with error message

## Validation

### Backend
- Appliances list not empty
- Monthly budget >= 0
- HTTP 400 Bad Request for validation failures
- HTTP 500 Internal Server Error for database failures

### Frontend
- Budget must be positive number
- At least one appliance must be selected
- Real-time validation with error messages
- Form submission blocked if validation fails

## State Persistence

**Current Implementation:**
- Profile loaded from API on app startup
- Changes persist in API/Database until next save
- State management maintains in-memory copy

**Future Enhancement (Optional):**
- Add local SharedPreferences caching for offline support
- Implement optimistic UI updates
- Add conflict resolution for concurrent updates

## API Response Examples

### GET /api/v1/profile - Success
```json
{
  "household_size": "4-5 People",
  "home_type": "Terrace House",
  "appliances": [
    "Air Conditioner",
    "Refrigerator",
    "Television"
  ],
  "occupancy": "Evening",
  "monthly_budget": 200.0,
  "created_at": "2026-06-01T10:30:00Z",
  "updated_at": "2026-06-01T10:30:00Z"
}
```

### POST /api/v1/profile - Success
```json
{
  "success": true,
  "message": "Household profile saved successfully",
  "data": {
    "user_id": "user_default",
    "timestamp": "2026-06-01T10:30:00Z",
    "action": "saved"
  }
}
```

## Files Created/Modified

### Created Files:
1. `backend/api/profile.py` - Profile API endpoints
2. `lib/models/household_profile.dart` - Data model
3. `lib/providers/household_profile_provider.dart` - State management
4. `lib/widgets/household_profile_section.dart` - UI widget

### Modified Files:
1. `backend/api/models.py` - Added Pydantic models
2. `backend/db/mongo.py` - Added database operations
3. `backend/main.py` - Registered profile router
4. `lib/services/api_service.dart` - Added API methods
5. `lib/main.dart` - Integrated provider
6. `lib/screens/profile_screen.dart` - Added UI section

## Testing Recommendations

### Manual Testing (Flutter App)
1. Navigate to Profile screen
2. Scroll down to Household Profile section
3. Fill in all fields:
   - Select household size
   - Select home type
   - Select at least one appliance
   - Select occupancy
   - Enter monthly budget (e.g., 200)
4. Click "Save Profile" button
5. Verify success snackbar appears
6. Verify data persists after navigation
7. Test error cases:
   - No appliances selected → error message shown
   - Negative budget → validation error
   - Network error → handled gracefully

### Backend Testing (API Endpoints)
```bash
# Get profile
curl -X GET http://localhost:8000/api/v1/profile

# Save profile
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{
    "household_size": "4-5 People",
    "home_type": "Terrace House",
    "appliances": ["Air Conditioner", "Refrigerator"],
    "occupancy": "Evening",
    "monthly_budget": 200
  }'
```

## Future Enhancements

1. **Appliance Recommendations**: Suggest energy-saving appliances based on current selection
2. **Budget Analysis**: Compare user's budget vs. typical usage patterns
3. **Seasonal Adjustments**: Allow different profiles for different seasons
4. **Family Members**: Add profiles for different household members
5. **Appliance-Specific Settings**: Custom settings for each appliance
6. **Energy Predictions**: Show predicted cost based on appliances and occupancy
7. **Comparison Data**: Show how user's profile compares to similar households

## Troubleshooting

### Profile not loading
- Check backend connection (health check endpoint)
- Verify MongoDB is running and connected
- Check API logs for errors

### Save fails silently
- Enable debug logging in ApiService
- Check network connectivity
- Verify backend is running
- Check MongoDB connection

### Appliances not persisting
- Verify at least one appliance is selected
- Check network request in developer tools
- Verify backend validation passes

## Configuration

### API Base URL
The API base URL can be configured:
```dart
final apiService = ApiService(baseUrl: 'http://your-server:8000');
```

### Database
Household profiles stored in MongoDB collection: `household_profiles`
Index: `household_profiles.user_id` (unique)

## Notes

- Currently uses `DEFAULT_USER_ID = "user_default"` for demo purposes
- In production, replace with actual user ID from authentication system
- Consider adding JWT token validation to profile endpoints
- Current implementation supports single user profile
- Scale to multi-user by parameterizing user_id from auth context
