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

# 2. Model Chain Strategy
MODEL_CHAIN = [
  "gemini-2.5-flash",          # Priority
  "gemini-flash-latest",       # Backup
  "gemini-2.0-flash",          # Backup
  "gemini-1.5-flash",          # Stable Fallback
  "gemini-1.5-pro"             # Slow but smart fallback
]

# 3. The UPDATED Prompt with Detailed Arts & Commerce Structure
PROMPT = """
Act as an educational authority for Indian Entrance Exams (2025-26). 
Generate a comprehensive JSON object for the "Phase 1: Undergraduate" roadmap.

The JSON must follow this exact schema structure (but you must populate the content):

{
  "Science": {
    "Engineering": {
      "master": { 
        "name": "JEE Main", 
        "description": "The national standard for engineering (NCERT Class 11/12).",
        "syllabus": { "Physics": [], "Maths": [], "Chemistry": [] } 
      },
      "satellites": [
        { "name": "BITSAT", "deviation": "Adds English & Logical Reasoning. Speed-focused." },
        { "name": "VITEEE", "deviation": "Easier difficulty, includes Aptitude." },
        { "name": "WBJEE", "deviation": "Higher weightage on Maths, specific to West Bengal colleges." }
      ]
    },
    "Medical": {
      "master": { 
        "name": "NEET UG", 
        "description": "Single entrance for MBBS/BDS/Ayush.",
        "syllabus": { "Biology": [], "Physics": [], "Chemistry": [] }
      },
      "satellites": [
        { "name": "AIIMS Paramedical", "deviation": "Specific to Nursing/Paramedical courses." },
        { "name": "IAT (IISER)", "deviation": "For Pure Science research. Includes Maths for bio students too." }
      ]
    }
  },
  "Commerce": {
    "University_General": {
      "master": {
         "name": "CUET (Commerce Domain)",
         "description": "For B.Com (Hons) & Eco (Hons) in Central Universities.",
         "syllabus": { "Accountancy": [], "Economics": [], "Business Studies": [], "Applied Mathematics": [] }
      },
      "satellites": []
    },
    "Management_Integrated": {
       "master": {
          "name": "IPMAT (Indore)",
          "description": "5-Year Integrated MBA at IIMs. High Maths focus.",
          "syllabus": { "Quantitative Ability (SA)": [], "Quantitative Ability (MCQ)": [], "Verbal Ability": [] }
       },
       "satellites": [
          { "name": "JIPMAT", "deviation": "Easier than Indore. For IIM Jammu/Bodh Gaya." },
          { "name": "NPAT (NMIMS)", "deviation": "Focus on Reasoning & Proficiency. Maths is mandatory." },
          { "name": "SET (Symbiosis)", "deviation": "General Aptitude based." }
       ]
    },
    "Professional_Maths": {
       "master": {
          "name": "CA Foundation",
          "description": "Entry for Chartered Accountancy. Heavy on Accounting & Law.",
          "syllabus": { "Accounting": [], "Business Laws": [], "Quant Aptitude (Maths/Stats/LR)": [], "Economics": [] }
       },
       "satellites": [
          { "name": "ISI Admission Test", "deviation": "For B.Stat. Advanced Pure Maths (Calculus, Number Theory)." },
          { "name": "ACET (Actuarial)", "deviation": "For Actuarial Science. Heavy Statistics & Probability." },
          { "name": "CS EET", "deviation": "Company Secretary. Legal Aptitude & Logic (No Maths)." }
       ]
    }
  },
  "Arts": {
    "Humanities_University": {
       "master": {
          "name": "CUET (Humanities Domain)",
          "description": "Gateway to BA Hons (History, Pol Sci, Geography, etc.) in Central Universities.",
          "syllabus": { "History": [], "Political Science": [], "Sociology": [], "Psychology": [], "General Test": [] }
       },
       "satellites": [
          { "name": "JMI Entrance", "deviation": "Jamia Millia Islamia specific entrance for certain courses." },
          { "name": "Ashoka Aptitude Test (AAT)", "deviation": "Private Liberal Arts. Focus on critical thinking & essays." }
       ]
    },
    "Law_Legal": {
       "master": {
          "name": "CLAT",
          "description": "Common Law Admission Test for National Law Universities (NLUs).",
          "syllabus": { "Legal Reasoning": [], "Logical Reasoning": [], "English Language": [], "Current Affairs/GK": [], "Quantitative Techniques": [] }
       },
       "satellites": [
          { "name": "AILET", "deviation": "For NLU Delhi. Generally tougher, higher focus on critical reasoning." },
          { "name": "SLAT", "deviation": "Symbiosis Law. Easier difficulty, includes WAT (Writing Ability Test)." },
          { "name": "MH-CET Law", "deviation": "State level (Maharashtra). Good for GLC Mumbai and ILS Pune." },
          { "name": "LSAT-India", "deviation": "Purely Analytical & Logical Reasoning (No GK/Maths)." }
       ]
    },
    "Design_Creative": {
       "master": {
          "name": "NID DAT",
          "description": "National Institute of Design - The premier exam for product/graphic design.",
          "syllabus": { "Design Aptitude": [], "Visual Spatial Ability": [], "Sketching/Drawing": [], "Observation Skills": [], "GK & Current Affairs": [] }
       },
       "satellites": [
          { "name": "NIFT Entrance", "deviation": "Fashion focused. Creative Ability Test (CAT) + General Ability Test (GAT)." },
          { "name": "UCEED", "deviation": "IIT Bombay Design. Computer-based, focus on visualization and logic." }
       ]
    },
    "Hospitality_Travel": {
        "master": {
            "name": "NCHMCT JEE",
            "description": "National Council for Hotel Management. Entry to IHMs (Govt).",
            "syllabus": { "Service Sector Aptitude": [], "Numerical Ability": [], "Reasoning": [], "English": [], "GK": [] }
        },
        "satellites": [
            { "name": "e-CHAT", "deviation": "IIHM Hotel Management. Online proctored." }
        ]
    }
  }
}

INSTRUCTIONS:
1. Populate the "syllabus" lists with REAL, high-level chapters (5-8 key topics per subject).
2. Ensure descriptions are accurate for the current academic year.
3. Return ONLY the raw JSON string. Do not use Markdown formatting like ```json.
"""

def generate_content_with_chain():
    if API_KEY == "DUMMY":
        return None

    last_exception = None

    for model_name in MODEL_CHAIN:
        print(f"----------------------------------------")
        print(f"Trying Model: {model_name}...")
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(PROMPT)
            print(f"SUCCESS with {model_name}!")
            return response.text

        except Exception as e:
            error_msg = str(e)
            print(f"FAILED with {model_name}.")
            if "429" in error_msg:
                print(f"  -> Quota exceeded. Retrying next model...")
            else:
                print(f"  -> Error: {error_msg}")
            
            last_exception = e
            time.sleep(1)

    if last_exception:
        print("CRITICAL: All models failed. Returning empty structure.")
        # Return a safe error structure
        return json.dumps({
            "Error": { "master": { "name": "Data Generation Failed", "syllabus": {} }, "satellites": [] }
        })

def main():
    try:
        raw_text = generate_content_with_chain()
        if not raw_text: return

        text = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        
        os.makedirs("data", exist_ok=True)
        with open("data/syllabus_data.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("Data successfully saved.")
        
    except Exception as e:
        print("Final Script Error:", e)
        raise e

if __name__ == "__main__":
    main()
