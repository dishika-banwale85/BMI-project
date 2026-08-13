from django.shortcuts import render
from .models import BmiRecord

def index(request):
    result = None

    # 1. Check if the user has a session. If not, create one silently.
    if not request.session.session_key:
        request.session.create()
    
    # Store their unique browser key in a variable
    user_session = request.session.session_key

    if request.method == 'POST':
        name = request.POST.get('name')
        age = int(request.POST.get('age'))
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))

        # Calculate BMI
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

        # 2. Save the calculation WITH their unique session key attached
        result = BmiRecord.objects.create(
            name=name, age=age, weight=weight, height=height, 
            bmi_value=bmi, category=category, session_key=user_session
        )

    # 3. Fetch history, but ONLY grab records matching their session key
    history = BmiRecord.objects.filter(session_key=user_session).order_by('-created_at')[:5]

    context = {
        'result': result,
        'history': history,
    }
    return render(request, 'calculator/index.html', context)