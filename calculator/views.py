from django.shortcuts import render
from .models import BmiRecord

def index(request):
    result = None

    if request.method == 'POST':
        name = request.POST.get('name')
        age = int(request.POST.get('age'))
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))

        # Calculate BMI: weight (kg) / [height (m)]^2
        height_in_meters = height / 100
        bmi = round(weight / (height_in_meters ** 2), 2)

        # Categorize
        if bmi < 18.5:
            category = 'Underweight'
        elif 18.5 <= bmi < 24.9:
            category = 'Healthy'
        elif 25 <= bmi < 29.9:
            category = 'Overweight'
        else:
            category = 'Unhealthy (Obese)'

        # Save to database
        result = BmiRecord.objects.create(
            name=name, age=age, weight=weight, height=height, 
            bmi_value=bmi, category=category
        )

    # Fetch the latest 5 records, ordered by newest first
    history = BmiRecord.objects.order_by('-created_at')[:5]

    context = {
        'result': result,
        'history': history,
    }
    return render(request, 'calculator/index.html', context)
    