# backend/services/ml_service.py

import os
import google.generativeai as genai
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv

class MLService:
    def __init__(self):
        """
        Initializes the ML Service by configuring the Gemini API.
        """
        project_root = Path(__file__).parent.parent.parent
        dotenv_path = project_root / '.env'
        load_dotenv(dotenv_path)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found. ML features will be disabled.")
            self.model = None
            return
        
        genai.configure(api_key=api_key)

        # Use the latest available Gemini Flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.class_labels = ['organic', 'paper', 'plastic', 'metal', 'glass', 'cardboard']
        self.recyclable_map = {
            'paper': True, 'plastic': True, 'metal': True, 'glass': True, 'cardboard': True,
            'organic': False
        }
        
        # --- THIS IS THE FIX ---
        # Replaced the emoji with simple text for Windows compatibility.
        print("[OK] ML Service initialized with Gemini model: 'gemini-2.5-flash'.")

    def classify_waste(self, image_path, weight, waste_type):
        """
        Classifies waste by sending an image and a prompt to the Gemini API.
        Falls back to a default classification if API fails.
        """
        # If model is not available, return default classification
        if not self.model:
            return {
                'predicted_category': waste_type or 'plastic',
                'confidence': 0.5,
                'recyclable': True,
                'waste_type': waste_type,
                'impact': { 'co2_saved_kg': 0.0 }
            }
            
        try:
            img = Image.open(image_path)
            prompt = f"""
            Analyze the image and classify the primary waste item into one of the following categories:
            {', '.join(self.class_labels)}.
            
            Provide your answer as a single word in lowercase from the list above. For example: plastic
            """
            response = self.model.generate_content([prompt, img])
            predicted_category = response.text.strip().lower()

            if predicted_category not in self.class_labels:
                print(f"Warning: Gemini returned an unexpected category: '{predicted_category}', defaulting to 'plastic'")
                predicted_category = 'plastic' 

            is_recyclable = self.recyclable_map.get(predicted_category, False)

            return {
                'predicted_category': predicted_category,
                'confidence': 0.99,
                'waste_type': waste_type,
                'recyclable': is_recyclable,
                'impact': { 'co2_saved_kg': 0.0 }
            }
        except Exception as e:
            print(f"ERROR during Gemini API call: {e}")
            print("Falling back to default classification...")
            import traceback
            traceback.print_exc()
            
            # Fallback to a default classification
            return {
                'predicted_category': 'plastic',
                'confidence': 0.50,
                'waste_type': waste_type,
                'recyclable': True,
                'impact': { 'co2_saved_kg': 0.0 }
            }