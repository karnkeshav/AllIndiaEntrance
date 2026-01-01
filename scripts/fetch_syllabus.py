import os
import json
import google.generativeai as genai

# Configure API
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp') # Using a fast, smart model

# The Prompt
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

def generate_content():
    print("Contacting Gemini...")
    response = model.generate_content(PROMPT)
    
    # Clean output just in case
    text = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(text)
        
        # Ensure directory exists
        os.makedirs("data", exist_ok=True)
        
        # Write file
        with open("data/syllabus_data.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("Success! Syllabus data generated.")
        
    except json.JSONDecodeError as e:
        print("Error decoding JSON from Gemini:", e)
        print("Raw response:", text)
        raise

if __name__ == "__main__":
    generate_content()
