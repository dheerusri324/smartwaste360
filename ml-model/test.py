# ==========================
# test.py (30→7 mapping)
# ==========================

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array # type: ignore

# GPU setup (optional)
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print("✅ GPU detected and memory growth set")
    except RuntimeError as e:
        print(e)
else:
    print("⚠️ No GPU detected. Using CPU.")

# Load model
model = tf.keras.models.load_model("mobilenet_waste_classifier.h5")

# Original 30 classes (model output)
class_30 = [
    'aerosol_cans', 'aluminum_food_cans', 'aluminum_soda_cans', 'cardboard_boxes',
    'cardboard_packaging', 'clothing', 'coffee_grounds', 'disposable_plastic_cutlery',
    'eggshells', 'food_waste', 'glass_beverage_bottles', 'glass_cosmetic_containers',
    'glass_food_jars', 'magazines', 'newspaper', 'office_paper', 'paper_cups',
    'plastic_cup_lids', 'plastic_detergent_bottles', 'plastic_food_containers',
    'plastic_shopping_bags', 'plastic_soda_bottles', 'plastic_straws',
    'plastic_trash_bags', 'plastic_water_bottles', 'shoes', 'steel_food_cans',
    'styrofoam_cups', 'styrofoam_food_containers', 'tea_bags'
]

# 7 merged classes
class_labels = ["organic", "paper", "plastic", "glass", "metal", "textile", "others"]

# Mapping 30 → 7
merge_mapping = {
    "organic": ["coffee_grounds", "food_waste", "eggshells", "tea_bags"],
    "paper": ["cardboard_boxes", "cardboard_packaging", "magazines", "newspaper", "office_paper", "paper_cups"],
    "plastic": ["plastic_cup_lids", "plastic_detergent_bottles", "plastic_food_containers",
                "plastic_shopping_bags", "plastic_soda_bottles", "plastic_straws",
                "plastic_trash_bags", "plastic_water_bottles", "disposable_plastic_cutlery"],
    "glass": ["glass_beverage_bottles", "glass_cosmetic_containers", "glass_food_jars"],
    "metal": ["aerosol_cans", "aluminum_food_cans", "aluminum_soda_cans", "steel_food_cans"],
    "textile": ["clothing", "shoes", "styrofoam_cups", "styrofoam_food_containers"],
    "others": []  # any leftover classes
}

# Recyclable info and impact formulas
category_info = {
    "organic": {
        "recyclable": False,
        "recommendation": "Send to Composting or Biogas Plant",
        "impact": lambda w: {
            "compost_yield_kg": round(w * 0.25, 2),
            "biogas_yield_m3": round(w * 0.08, 2),
            "co2_saved_kg": round(w * 0.5, 2)
        }
    },
    "paper": {
        "recyclable": True,
        "recommendation": "Send to Paper Recycling",
        "impact": lambda w: {
            "recycled_kg": w,
            "co2_saved_kg": round(w * 1.5, 2)
        }
    },
    "plastic": {
        "recyclable": True,
        "recommendation": "Send to Plastic Recycling Center",
        "impact": lambda w: {
            "recycled_kg": w,
            "co2_saved_kg": round(w * 2.5, 2)
        }
    },
    "glass": {
        "recyclable": True,
        "recommendation": "Send to Glass Recycling",
        "impact": lambda w: {
            "recycled_kg": w,
            "co2_saved_kg": round(w * 1.0, 2)
        }
    },
    "metal": {
        "recyclable": True,
        "recommendation": "Send to Metal Recycling",
        "impact": lambda w: {
            "recycled_kg": w,
            "co2_saved_kg": round(w * 1.0, 2)
        }
    },
    "textile": {
        "recyclable": True,
        "recommendation": "Donate or Textile Recycling",
        "impact": lambda w: {
            "recycled_kg": w,
            "co2_saved_kg": round(w * 2.0, 2)
        }
    },
    "others": {
        "recyclable": False,
        "recommendation": "Dispose as General Waste",
        "impact": lambda w: {"co2_saved_kg": 0}
    }
}

def predict_and_recommend(img_path, weight_kg=1.0, waste_type="dry"):
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # 30-class prediction
    predictions = model.predict(img_array, verbose=0)[0]
    predicted_30_index = np.argmax(predictions)
    predicted_30_class = class_30[predicted_30_index]

    # Map to 7 merged classes
    predicted_class = None
    for merged_class, originals in merge_mapping.items():
        if predicted_30_class in originals:
            predicted_class = merged_class
            break
    if predicted_class is None:
        predicted_class = "others"

    confidence = predictions[predicted_30_index]

    info = category_info[predicted_class]

    result = {
        "predicted_category": predicted_class,
        "original_classes": merge_mapping.get(predicted_class, []),
        "confidence": round(confidence * 100, 2),
        "recyclable": info["recyclable"],
        "recommendation": info["recommendation"],
        "impact": info["impact"](weight_kg),
        "waste_type": waste_type
    }
    return result

if __name__ == "__main__":
    # Example usage
    img_path = "C:/Users/dheer/PycharmProjects/SmartWaste360/image2.jpg"  # <-- replace this
    weight_kg = 0.5  # example weight
    waste_type = "dry"  # "dry" or "wet"

    output = predict_and_recommend(img_path, weight_kg, waste_type)
    if output["predicted_category"] == "organic":
        output["waste_type"] = "wet"
    print("✅ Prediction Result:")
    print(output)

