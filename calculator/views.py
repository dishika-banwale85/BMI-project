import csv
import io
import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai

def home(request):
    return render(request, 'calculator/home.html')

def about(request):
    return render(request, 'calculator/about.html')

def calculator_view(request):
    # Context variables
    manual_result = None
    diet_plan = None
    file_results = []
    file_description = ""

    # Refresh (GET request) returns a clean slate
    if request.method == 'GET':
        return render(request, 'calculator/calculator.html')

    elif request.method == 'POST':
        # --- FEATURE 1: MANUAL FORM SUBMISSION ---
        if 'manual_submit' in request.POST:
            name = request.POST.get('name', 'User')
            age = int(request.POST.get('age', 20))
            weight = float(request.POST.get('weight', 0))
            height = float(request.POST.get('height', 1))

            # Calculation
            bmi = round(weight / ((height / 100) ** 2), 2)

            if bmi < 18.5:
                category = 'Underweight'
                diet_plan = {
                    "title": "Caloric Surplus Protocol",
                    "points": ["Increase daily calories with nutrient-dense foods.", "Focus on lean proteins and healthy fats.", "Incorporate structured resistance training."]
                }
            elif 18.5 <= bmi < 24.9:
                category = 'Healthy'
                diet_plan = {
                    "title": "Maintenance & Wellness Strategy",
                    "points": ["Maintain balanced macronutrient portions.", "Prioritize fiber-rich vegetables and whole grains.", "Stay consistent with active physical movement."]
                }
            elif 25 <= bmi < 29.9:
                category = 'Overweight'
                diet_plan = {
                    "title": "Sustainable Deficit Program",
                    "points": ["Prioritize protein to protect active muscle mass.", "Incorporate higher volumes of low-calorie whole foods.", "Reduce daily portions of refined processed sugars."]
                }
            else:
                category = 'Unhealthy (Obese)'
                diet_plan = {
                    "title": "Therapeutic Lifestyle Adjustment",
                    "points": ["Focus on strict structural plate portions.", "Incorporate safe, low-impact exercise habits.", "Eliminate trans fats and sugary corn syrup additives."]
                }

            manual_result = {
                'name': name, 'age': age, 'bmi_value': bmi, 'category': category
            }

        # --- FEATURE 2: FILE UPLOAD HANDLING ---
        elif 'file_submit' in request.FILES:
            uploaded_file = request.FILES['file_submit']
            
            # Read file data as text stream safely
            file_data = uploaded_file.read().decode('utf-8')
            csv_data = csv.reader(io.StringIO(file_data))
            
            rows_to_process = []
            for row in csv_data:
                if not row or len(row) < 4:
                    continue
                
                cleaned_row = [item.strip() for item in row]
                
                if "name" in cleaned_row[0].lower() or "age" in cleaned_row[1].lower():
                    continue
                    
                rows_to_process.append(cleaned_row)
            
            for row in rows_to_process[:10]:
                try:
                    name = row[0]
                    height = float(row[2]) 
                    weight = float(row[3]) 
                    
                    if weight <= 0 or height <= 0:
                        continue
                        
                    height_in_meters = height / 100
                    bmi = round(weight / (height_in_meters ** 2), 2)
                    
                    if bmi < 18.5: 
                        cat = 'Underweight'
                    elif 18.5 <= bmi < 24.9: 
                        cat = 'Healthy'
                    elif 25 <= bmi < 29.9: 
                        cat = 'Overweight'
                    else: 
                        cat = 'Unhealthy (Obese)'
                    
                    file_results.append({
                        'name': name, 'bmi_value': bmi, 'category': cat
                    })
                except (ValueError, IndexError):
                    continue

            if file_results:
                total_people = len(file_results)
                healthy_count = sum(1 for p in file_results if p['category'] == 'Healthy')
                file_description = f"Batch processing execution complete. Analyzed metric profiles for {total_people} profile records. Out of these profiles, {healthy_count} are registering within normal healthy benchmarks."
   
    return render(request, 'calculator/calculator.html', {
        'manual_result': manual_result,
        'diet_plan': diet_plan,
        'file_results': file_results,
        'file_description': file_description
    })

def specialists(request):
    doctors = [
        {
            "name": "Dr. Ananya Sharma",
            "role": "Clinical Nutritionist & Weight Optimization Expert",
            "experience": "12+ Years",
            "email": "dr.ananya@vitalityhub.com",
            "phone": "+91 98765 43210",
            "specialty": "Metabolic Disorders & Strategic Weight Management",
            "bio": "Specializes in customizing medical nutrition strategies for insulin resistance, metabolic recovery, and thyroid management."
        },
        {
            "name": "Dr. Vikram Malhotra",
            "role": "Sports Nutritionist & Lean Mass Performance Coach",
            "experience": "8+ Years",
            "email": "dr.vikram@vitalityhub.com",
            "phone": "+91 87654 32109",
            "specialty": "Athletic Conditioning, Nutrient Timing, & Muscle Gain",
            "bio": "Helps health-conscious individuals and elite athletes hit strength indices via high-protein nutrient-dense optimization."
        },
        {
            "name": "Dr. Priya Nair",
            "role": "Holistic Dietitian & Gut Health Researcher",
            "experience": "10+ Years",
            "email": "dr.priya@vitalityhub.com",
            "phone": "+91 76543 21098",
            "specialty": "Microbiome Health, Plant-Based Nutrition, & Mindful Eating",
            "bio": "Passionate about correcting gut inflammation, food sensitivities, and digestive health using natural whole-food protocols."
        }
    ]
    return render(request, 'calculator/specialists.html', {'doctors': doctors})

def chat_view(request):
    """Renders the main chatbot template."""
    return render(request, 'calculator/chat.html')

@csrf_exempt
def chat_ask(request):
    """Handles real-time requests from the chat interface safely."""
    if request.method == 'POST':
        try:
            # 1. Safely read JSON from the frontend
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'reply': 'Please type a valid message.'})
            
            # 2. EXPLICITLY read the key and pass it to the client to prevent silent crashes
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                return JsonResponse({'reply': "System Alert: API Key is missing. Please ensure GEMINI_API_KEY is saved in your Render Environment settings."})
                
            client = genai.Client(api_key=api_key)
            
            system_instruction = (
                "You are the VitalityHub AI Health Assistant. You are friendly, professional, "
                "and informative. Provide helpful, structured advice regarding diet, BMI, fitness, "
                "and general health metrics. Always add a professional medical disclaimer when appropriate."
            )
            
            # 3. Generate content
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config={'system_instruction': system_instruction}
            )
            
            if response and hasattr(response, 'text'):
                return JsonResponse({'reply': response.text})
            else:
                return JsonResponse({'reply': "The assistant generated an empty reply object. Please retry."})
                
        except Exception as e:
            # Safely capture any error and print it to the chat bubble instead of crashing!
            return JsonResponse({'reply': f"AI Service Notice: {str(e)}"})
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)