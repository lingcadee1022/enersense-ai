#!/usr/bin/env python3
"""
EnerSense AI - Quick Start Demo
Demonstrates the complete AI/ML pipeline
"""

import sys
from datetime import datetime
from appliance_classifier import predict_appliance, get_energy_score
from anomaly_detection import analyze_reading
from recommendation_engine import get_recommendations, get_appliance_insights, get_daily_summary
from recommendation_engine import add_reading as add_rec_reading
from forecasting import forecast_monthly, get_peak_hours
from forecasting import add_reading as add_forecast_reading


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def demo_appliance_prediction():
    """Demo 1: Appliance Prediction"""
    print_header("1. APPLIANCE PREDICTION (NILM)")
    
    test_cases = [
        {"power": 50, "voltage": 240, "current": 0.2, "label": "Lighting"},
        {"power": 1500, "voltage": 240, "current": 6.25, "label": "Air Conditioner"},
        {"power": 100, "voltage": 240, "current": 0.42, "label": "Refrigerator"},
        {"power": 800, "voltage": 240, "current": 3.33, "label": "Television"},
        {"power": 2000, "voltage": 240, "current": 8.33, "label": "Oven"},
        {"power": 1200, "voltage": 240, "current": 5.0, "label": "Washing Machine"},
    ]
    
    print("\nPredicting appliances from power signatures:\n")
    for case in test_cases:
        predicted = predict_appliance(case['power'], case['voltage'], case['current'])
        energy_score = get_energy_score(case['power'])
        
        status = "✓" if predicted == case['label'] else "⚠"
        print(f"{status} Power: {case['power']}W, Current: {case['current']}A")
        print(f"  Expected: {case['label']:<20} Predicted: {predicted:<20} Score: {energy_score}")


def demo_anomaly_detection():
    """Demo 2: Anomaly Detection"""
    print_header("2. ANOMALY DETECTION")
    
    # Add normal readings
    normal_readings = [1200, 1250, 1300, 1280, 1350]
    
    print("\nAdding normal AC usage readings:")
    for power in normal_readings:
        analyze_reading(power, "Air Conditioner")
        print(f"  • {power}W")
    
    # Test anomaly
    print("\nTesting anomaly detection:")
    anomalous_power = 3500  # Much higher than normal
    result = analyze_reading(anomalous_power, "Air Conditioner")
    
    print(f"\n  Input: {anomalous_power}W")
    print(f"  Is Anomaly: {result['is_anomaly']}")
    print(f"  Insight: {result.get('insight', 'No insight')}")


def demo_energy_scoring():
    """Demo 3: Energy Scoring"""
    print_header("3. ENERGY SCORING")
    
    appliances = [
        {"name": "Lighting", "power": 50},
        {"name": "Refrigerator", "power": 100},
        {"name": "Television", "power": 800},
        {"name": "Air Conditioner", "power": 1500},
        {"name": "Oven", "power": 2500},
    ]
    
    print("\nEnergy scores by appliance:\n")
    for appliance in appliances:
        score = get_energy_score(appliance['power'])
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        print(f"{appliance['name']:<20} {score:>3}/100 [{bar}]")


def demo_recommendations():
    """Demo 4: Recommendations"""
    print_header("4. RECOMMENDATION ENGINE")
    
    # Simulate usage patterns
    usage_data = [
        (50, "Lighting"),
        (1500, "Air Conditioner"),
        (100, "Refrigerator"),
        (800, "Television"),
        (2000, "Oven"),
        (1200, "Washing Machine"),
        (1500, "Air Conditioner"),
    ]
    
    print("\nSimulating user energy consumption:\n")
    for power, appliance in usage_data:
        add_rec_reading(power, appliance)
        add_forecast_reading(power)
        print(f"  • {power}W - {appliance}")
    
    print("\n" + "-"*60)
    print("AI-Generated Recommendations:")
    print("-"*60 + "\n")
    
    recommendations = get_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['recommendation']}")
        if 'potential_savings' in rec:
            print(f"   💰 {rec['potential_savings']}\n")


def demo_appliance_breakdown():
    """Demo 5: Appliance Breakdown"""
    print_header("5. APPLIANCE USAGE BREAKDOWN")
    
    insights = get_appliance_insights()
    
    print("\nAppliance consumption analysis:\n")
    print(f"{'Appliance':<20} {'Avg Power':<12} {'Readings':<10} {'Total (W)':<12}")
    print("-" * 55)
    
    for insight in insights:
        print(f"{insight['appliance']:<20} {insight['avg_power']:>10.0f}W {insight['readings']:>8} {insight['total_consumption']:>10.0f}W")


def demo_forecasting():
    """Demo 6: Energy Forecasting"""
    print_header("6. ENERGY FORECASTING")
    
    forecast = forecast_monthly()
    peak_hours = get_peak_hours()
    
    print("\nMonthly Forecast:")
    print(f"  • Estimated Daily:   {forecast['estimated_daily_kwh']:.2f} kWh")
    print(f"  • Estimated Monthly: {forecast['estimated_monthly_kwh']:.2f} kWh")
    print(f"  • Estimated Cost:    RM {forecast['estimated_monthly_cost']:.2f}")
    print(f"  • Rate:              RM {forecast['cost_per_kwh']:.2f}/kWh")
    
    print(f"\nPeak Usage Hours: {', '.join(map(str, peak_hours))}")


def demo_daily_summary():
    """Demo 7: Daily Summary"""
    print_header("7. DAILY SUMMARY")
    
    summary = get_daily_summary()
    
    print("\nDaily Summary:")
    print(f"  • Total Readings:      {summary['total_readings']}")
    print(f"  • Total Power:         {summary['total_power']:.0f} W")
    print(f"  • Average Power:       {summary['average_power']:.0f} W")
    print(f"  • Recommendations:     {summary['recommendations_count']}")
    
    if summary.get('top_recommendations'):
        print("\n  Top Recommendations:")
        for rec in summary['top_recommendations'][:2]:
            if 'recommendation' in rec:
                print(f"    - {rec['recommendation']}")


def main():
    """Run all demos"""
    print("\n" + "█"*60)
    print("  EnerSense AI/ML - Complete System Demo")
    print("  Version 1.0.0")
    print("█"*60)
    
    try:
        demo_appliance_prediction()
        demo_energy_scoring()
        demo_anomaly_detection()
        demo_recommendations()
        demo_appliance_breakdown()
        demo_forecasting()
        demo_daily_summary()
        
        print_header("✓ DEMO COMPLETE")
        print("\nNext Steps:")
        print("  1. Train models: python model_training.py")
        print("  2. Start API:    python api_service.py")
        print("  3. Test API:     curl http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
