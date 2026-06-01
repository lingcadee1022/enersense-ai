"""
Profile API endpoints for EnerSense AI.

Endpoints:
- GET /api/v1/profile - Get user's household profile
- POST /api/v1/profile - Save or update user's household profile
"""

import logging
from fastapi import APIRouter, HTTPException, status
from db.mongo import db_client
from api.models import HouseholdProfileRequest, HouseholdProfileResponse, SuccessResponse
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Profile"])

# Default user ID for demo (in production, this would come from JWT token)
DEFAULT_USER_ID = "user_default"


@router.get("/profile", response_model=HouseholdProfileResponse)
async def get_household_profile() -> HouseholdProfileResponse:
    """
    Get the current user's household profile.
    
    Returns:
        HouseholdProfileResponse: User's household profile with all details
        
    Raises:
        HTTPException: If profile not found or database error occurs
    """
    try:
        profile = db_client.get_household_profile(DEFAULT_USER_ID)
        
        if not profile:
            # Return default profile if not found
            logger.info(f"No household profile found for {DEFAULT_USER_ID}, returning default")
            return HouseholdProfileResponse(
                household_size="2-3 People",
                home_type="Apartment / Condo",
                appliances=["Refrigerator", "Television"],
                occupancy="All Day",
                monthly_budget=150.0,
                created_at=datetime.utcnow().isoformat() + "Z",
                updated_at=datetime.utcnow().isoformat() + "Z"
            )
        
        logger.info(f"✓ Retrieved household profile for {DEFAULT_USER_ID}")
        
        return HouseholdProfileResponse(
            household_size=profile.get("household_size", "2-3 People"),
            home_type=profile.get("home_type", "Apartment / Condo"),
            appliances=profile.get("appliances", ["Refrigerator", "Television"]),
            occupancy=profile.get("occupancy", "All Day"),
            monthly_budget=float(profile.get("monthly_budget", 150.0)),
            created_at=profile.get("created_at"),
            updated_at=profile.get("updated_at")
        )
        
    except Exception as e:
        logger.error(f"Error retrieving household profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve household profile: {str(e)}"
        )


@router.post("/profile", response_model=SuccessResponse)
async def save_household_profile(
    profile_data: HouseholdProfileRequest,
) -> SuccessResponse:
    """
    Save or update the user's household profile.
    
    Request body:
    {
        "household_size": "4-5 People",
        "home_type": "Terrace House",
        "appliances": [
            "Air Conditioner",
            "Refrigerator",
            "Television"
        ],
        "occupancy": "Evening",
        "monthly_budget": 200
    }
    
    Response:
    {
        "success": true,
        "message": "Household profile saved successfully",
        "data": {
            "user_id": "user_default",
            "timestamp": "2026-06-01T10:30:00Z"
        }
    }
    
    Args:
        profile_data: HouseholdProfileRequest with household details
        
    Returns:
        SuccessResponse with confirmation and timestamp
        
    Raises:
        HTTPException: If validation fails or database operation fails
    """
    try:
        # Validate appliances list is not empty
        if not profile_data.appliances:
            raise ValueError("At least one appliance must be selected")
        
        # Validate monthly budget is positive
        if profile_data.monthly_budget < 0:
            raise ValueError("Monthly budget must be a positive number")
        
        # Prepare profile document
        profile_doc = {
            "user_id": DEFAULT_USER_ID,
            "household_size": profile_data.household_size,
            "home_type": profile_data.home_type,
            "appliances": profile_data.appliances,
            "occupancy": profile_data.occupancy,
            "monthly_budget": profile_data.monthly_budget,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        
        # Check if profile exists
        existing_profile = db_client.get_household_profile(DEFAULT_USER_ID)
        
        if existing_profile:
            # Update existing profile
            result = db_client.update_household_profile(DEFAULT_USER_ID, profile_doc)
            action = "updated"
        else:
            # Create new profile
            profile_doc["created_at"] = datetime.utcnow().isoformat() + "Z"
            result = db_client.insert_household_profile(profile_doc)
            action = "saved"
        
        logger.info(
            f"✓ Household profile {action} for {DEFAULT_USER_ID}: "
            f"Size={profile_data.household_size}, "
            f"HomeType={profile_data.home_type}, "
            f"Appliances={len(profile_data.appliances)}, "
            f"Budget=RM{profile_data.monthly_budget}"
        )
        
        return SuccessResponse(
            success=True,
            message=f"Household profile {action} successfully",
            data={
                "user_id": DEFAULT_USER_ID,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "action": action
            }
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in household profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error saving household profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save household profile: {str(e)}"
        )
