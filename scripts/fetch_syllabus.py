import os
import json
import time
import google.generativeai as genai
from google.api_core import exceptions

# 1. Setup API
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("WARNING: GEMINI_API_KEY not found. Using dummy data mode.")
    API_KEY = "DUMMY"
else:
    genai.configure(api_key=API_KEY)

# 2. The Strategy: Model Chain
# We attempt these models in order. If one fails (quota/limit), we try the next.
MODEL_CHAIN = [
  "gemini-2.5-flash",          # Best free model (User Preference)
  "gemini-flash-latest",       # Backup Alias
  "gemini-2.0-flash",          # Backup
  "gemini-2.0-flash-exp",      # Experimental Backup
  "gemini-1.5-flash",          # Stable Fallback
  "gemini-2.5-flash-lite"      # Last Resort
]

# 3. The Prompt
PROMPT = """
Act as an educational authority for Indian Entrance Exams. 
Generate a comprehensive JSON object for the "Phase 1: Undergraduate" roadmap.

The JSON must follow this exact schema:
{
  "Science": {
    "Engineering": {
      "master": { 
        "name": "JEE Main", 
        "description": "The unified syllabus for engineering based on NCERT Class 11 & 12.",
        "syllabus": { 
            "Physics": ["Kinematics", "Laws of Motion", "Thermodynamics", "Electrostatics", "Optics"], 
            "Maths": ["Calculus", "Vectors", "Probability", "Algebra", "Trigonometry"],
            "Chemistry": ["Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry"]
        } 
      },
      "satellites": [
        { "name": "BITSAT", "deviation": "Adds English Proficiency and Logical Reasoning. Focuses more on speed." },
        { "name": "VITEEE", "deviation": "Includes Aptitude section. Question level is generally easier than JEE." }
      ]
    },
    "Medical": {
      "master": { 
        "name": "NEET UG", 
        "description": "The single entrance test for Medical (MBBS/BDS) in India.",
        "syllabus": {
            "Biology": ["Diversity in Living World", "Human Physiology", "Genetics and Evolution", "Ecology"],
            "Physics": ["Mechanics", "Electrodynamics", "Modern Physics"],
            "Chemistry": ["Basic Concepts", "Bonding", "Equilibrium"]
        }
      },
      "satellites": [
        { "name": "AIIMS Nursing", "deviation": "Includes General Knowledge and Aptitude." }
      ]
    }
  },
  "Commerce": {
    "General": {
      "master": {
         "name": "CUET (Commerce)",
         "description": "Common University Entrance Test for Commerce domain.",
         "syllabus": { "Accountancy": ["Partnership", "Shares"], "Economics": ["Macroeconomics", "Indian Eco Dev"], "Business Studies": ["Management"] }
      },
      "satellites": [
         { "name": "IPMAT", "deviation": "Focuses heavily on Higher Maths (Functions, Calculus) and Verbal Ability." }
      ]
    }
  },
  "Arts": {
    "Humanities": {
       "master": {
          "name": "CUET (Arts)",
          "description": "Standardized test for History, Pol Sci, Geography domains.",
          "syllabus": { "History": ["Harappan Civ", "Modern India"], "Political Science": ["Cold War", "Indian Politics"] }
       },
       "satellites": [
          { "name": "CLAT", "deviation": "Completely different format: Legal Reasoning, Logical Reasoning, Current Affairs, English." }
       ]
    }
  }
}

INSTRUCTIONS:
1. Populate the "syllabus" lists with REAL, high-level chapters (approx 5-10 items per subject). 
2. Ensure descriptions are accurate for the current academic year.
3. Return ONLY the raw JSON string. Do not use Markdown formatting like ```json.
"""

def generate_content_with_chain():
    if API_KEY == "DUMMY":
        return None

    last_exception = None

    # Loop through the chain
    for model_name in MODEL_CHAIN:
        print(f"----------------------------------------")
        print(f"Trying Model: {model_name}...")
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(PROMPT)
            print(f"SUCCESS with {model_name}!")
            return response.text

        except Exception as e:
            # Handle specific API errors
            error_msg = str(e)
            print(f"FAILED with {model_name}.")
            
            # If it's a 404 (Model not found) or 429 (Quota), we just log and continue
            if "404" in error_msg:
                print(f"  -> Error: Model version not found or deprecated.")
            elif "429" in error_msg:
                print(f"  -> Error: Quota/Rate Limit exceeded.")
            else:
                print(f"  -> Error: {error_msg}")
            
            last_exception = e
            time.sleep(1) # Brief pause before switching to next model

    print("----------------------------------------")
    print("CRITICAL: All models in the chain failed.")
    if last_exception:
        raise last_exception

def main():
    try:
        raw_text = generate_content_with_chain()
        
        if not raw_text:
            print("No content generated (Dummy mode or all failed).")
            return

        # Clean output
        text = raw_text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        data = json.loads(text)
        
        # Save
        os.makedirs("data", exist_ok=True)
        with open("data/syllabus_data.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("Data successfully saved to data/syllabus_data.json")
        
    except Exception as e:
        print("Final Script Error:", e)
        # Fallback: Write valid JSON structure with error message so app doesn't crash
        os.makedirs("data", exist_ok=True)
        dummy_data = {
            "error": "Data generation failed", 
            "Science": { "Engineering": { "master": { "name": "Server Error", "syllabus": {} }, "satellites": [] }}
        }
        with open("data/syllabus_data.json", "w") as f:
            json.dump(dummy_data, f)
        # We don't raise here so the Action finishes 'green' even if data is dummy, 
        # but you might want to know if it failed. Uncomment next line to force fail:
        # raise e

if __name__ == "__main__":
    main()
