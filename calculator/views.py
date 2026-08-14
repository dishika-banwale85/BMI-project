import csv
import io
from django.shortcuts import render

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
            
            # Read file data as text stream
            file_data = uploaded_file.read().decode('utf-8')
            csv_data = csv.reader(io.StringIO(file_data))
            
            # Skip header row if it contains text fields
            first_row = next(csv_data, None)
            
            rows_to_process = []
            if first_row:
                # Basic check: if first row is data (not labels), keep it
                try:
                    float(first_row[1]) # check if weight field is a number
                    rows_to_process.append(first_row)
                except (ValueError, IndexError):
                    pass # It's a header line, skip it safely
            
            # Read remaining rows
            for row in csv_data:
                if row: rows_to_process.append(row)
            
            # Cap at maximum 10 names as requested
            for row in rows_to_process[:10]:
                try:
                    name = row[0].strip()
                    weight = float(row[1])
                    height = float(row[2])
                    
                    bmi = round(weight / ((height / 100) ** 2), 2)
                    
                    if bmi < 18.5: cat = 'Underweight'
                    elif 18.5 <= bmi < 24.9: cat = 'Healthy'
                    elif 25 <= bmi < 29.9: cat = 'Overweight'
                    else: cat = 'Unhealthy (Obese)'
                    
                    file_results.append({
                        'name': name, 'bmi_value': bmi, 'category': cat
                    })
                except (ValueError, IndexError):
                    continue # Skip structural corruptions gracefully

            if file_results:
                total_people = len(file_results)
                healthy_count = sum(1 for p in file_results if p['category'] == 'Healthy')
                file_description = f"Batch processing execution complete. Analyzed metric profiles for {total_people} profile records. Out of these profiles, {healthy_count} are registering within normal healthy benchmarks. The comparative matrix below maps out variations across the entire uploaded data group."

    return render(request, 'calculator/calculator.html', {
        'manual_result': manual_result,
        'diet_plan': diet_plan,
        'file_results': file_results,
        'file_description': file_description
    })