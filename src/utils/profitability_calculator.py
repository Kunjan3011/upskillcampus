"""
Profitability Calculator Module

Calculates profitability index for crops based on predicted yield,
market price, and cultivation cost.
"""

from typing import Dict, Optional


def calculate_profitability_index(
    predicted_yield: float,
    market_price: float,
    cost: float,
    unit: str = "Quintals/Hectare"
) -> Dict[str, float]:
    """
    Calculate profitability index and related metrics.
    
    Formula: Profitability Index = (Predicted Yield × Market Price) ÷ Cost
    
    Args:
        predicted_yield: Predicted crop yield
        market_price: Current market price per unit
        cost: Total cost of cultivation
        unit: Unit of measurement (default: Quintals/Hectare)
    
    Returns:
        Dictionary containing:
        - profitability_index: Main metric (>1 = profitable)
        - expected_revenue: Total expected revenue
        - expected_profit: Net profit
        - profit_margin: Profit margin percentage
        - recommendation: Text recommendation
    """
    if cost <= 0:
        raise ValueError("Cost must be greater than zero")
    
    if predicted_yield < 0:
        raise ValueError("Predicted yield cannot be negative")
    
    # Calculate expected revenue
    expected_revenue = predicted_yield * market_price
    
    # Calculate profitability index
    profitability_index = expected_revenue / cost if cost > 0 else 0
    
    # Calculate expected profit
    expected_profit = expected_revenue - cost
    
    # Calculate profit margin percentage
    profit_margin = (expected_profit / cost) * 100 if cost > 0 else 0
    
    # Generate recommendation
    if profitability_index > 1.5:
        recommendation = "Highly Profitable - Strongly Recommended"
    elif profitability_index > 1.2:
        recommendation = "Profitable - Recommended"
    elif profitability_index > 1.0:
        recommendation = "Marginally Profitable - Consider"
    elif profitability_index > 0.8:
        recommendation = "Low Profitability - Risky"
    else:
        recommendation = "Loss-Making - Not Recommended"
    
    return {
        "profitability_index": round(profitability_index, 2),
        "predicted_yield": round(predicted_yield, 2),
        "unit": unit,
        "expected_revenue": round(expected_revenue, 2),
        "cost": round(cost, 2),
        "expected_profit": round(expected_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "recommendation": recommendation
    }


def compare_crops_profitability(
    crops_data: list[Dict[str, float]]
) -> list[Dict]:
    """
    Compare profitability of multiple crops.
    
    Args:
        crops_data: List of dictionaries with keys:
                   'crop', 'predicted_yield', 'market_price', 'cost'
    
    Returns:
        Sorted list of crops by profitability index (descending)
    """
    results = []
    
    for crop_data in crops_data:
        crop_name = crop_data.get('crop', 'Unknown')
        yield_val = crop_data.get('predicted_yield', 0)
        price = crop_data.get('market_price', 0)
        cost = crop_data.get('cost', 0)
        
        profitability = calculate_profitability_index(
            predicted_yield=yield_val,
            market_price=price,
            cost=cost
        )
        
        profitability['crop'] = crop_name
        results.append(profitability)
    
    # Sort by profitability index (descending)
    results.sort(key=lambda x: x['profitability_index'], reverse=True)
    
    # Add rank
    for idx, result in enumerate(results, 1):
        result['rank'] = idx
    
    return results


if __name__ == "__main__":
    # Example usage
    example = calculate_profitability_index(
        predicted_yield=50.0,
        market_price=2000.0,
        cost=80000.0
    )
    print("Example Profitability Calculation:")
    print(example)
    
    # Example comparison
    crops = [
        {'crop': 'Rice', 'predicted_yield': 50, 'market_price': 2000, 'cost': 80000},
        {'crop': 'Wheat', 'predicted_yield': 45, 'market_price': 1800, 'cost': 70000},
        {'crop': 'Cotton', 'predicted_yield': 15, 'market_price': 6500, 'cost': 75000}
    ]
    
    print("\nCrop Comparison:")
    comparison = compare_crops_profitability(crops)
    for crop in comparison:
        print(f"{crop['rank']}. {crop['crop']}: Index = {crop['profitability_index']}")








