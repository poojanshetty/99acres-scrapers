import pandas as pd

from src.data_pipeline import add_value_features, clean_raw_properties, price_to_lakhs


def test_price_to_lakhs_converts_crore_and_lakh_values():
    prices = pd.Series(["₹2.4 Cr", "₹75 Lac", "₹1,25,000 Lac"])
    assert price_to_lakhs(prices).tolist() == [240.0, 75.0, 125000.0]


def test_clean_raw_properties_extracts_rating_and_removes_duplicate():
    raw = pd.DataFrame(
        {
            "name": ["Sobha Royal Pavilion\n4.2", "Sobha Royal Pavilion\n4.2", "No Rating Home"],
            "location": [
                "3 BHK Flat in Sarjapur Road, Bangalore",
                "3 BHK Flat in Sarjapur Road, Bangalore",
                "2 BHK Flat in Whitefield, Bangalore",
            ],
            "price": ["₹2.4 Cr", "₹2.4 Cr", "₹75 Lac"],
            "area": ["1,507 sqft", "1,507 sqft", "900 sqft"],
            "bhk": ["3 BHK", "3 BHK", "2 BHK"],
        }
    )

    result = clean_raw_properties(raw)

    assert len(result) == 2
    assert result.loc[0, "name"] == "sobha royal pavilion"
    assert result.loc[0, "ratings"] == 4.2
    assert result.loc[0, "price_lakhs"] == 240.0
    assert result.loc[0, "location"] == "sarjapur road"
    assert pd.isna(result.loc[1, "ratings"])


def test_add_value_features_calculates_price_per_sqft():
    result = add_value_features(pd.DataFrame({"price_lakhs": [100], "area_sqft": [1000]}))
    assert result.loc[0, "price_per_sqft"] == 10000.0
