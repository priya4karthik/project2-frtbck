import json
import urllib.request
import urllib.error

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .forms import UserRegistrationForm
from .models import FormSubmission


def call_gemini(prompt: str) -> str:
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
        return generate_local_suggestions(prompt)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 300, "temperature": 0.4}
    }).encode()

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            return body["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            code = err.get("error", {}).get("code", e.code)
        except Exception:
            code = e.code
        if code in (429, 403):
            # Fall back to local suggestions when rate limited
            return generate_local_suggestions(prompt)
        return generate_local_suggestions(prompt)
    except Exception:
        return generate_local_suggestions(prompt)


def generate_local_suggestions(prompt: str) -> str:
    """
    Offline rule-based suggestions — works 100% without any API key or internet.
    Parses the prompt to extract field values and gives smart feedback.
    """
    lines = {}
    for line in prompt.split('\n'):
        if ':' in line and line.strip().startswith('-'):
            parts = line.split(':', 1)
            key = parts[0].replace('-', '').strip().lower().replace(' ', '_')
            val = parts[1].strip() if len(parts) > 1 else ''
            lines[key] = val

    name       = lines.get('full_name', '')
    email      = lines.get('email', '')
    phone      = lines.get('phone', '')
    occupation = lines.get('occupation', '')
    bio        = lines.get('bio', '')
    city       = lines.get('city', '')

    tips = []

    # Name checks
    if name and name == name.lower():
        tips.append(f'• Capitalise your name properly — try "{name.title()}" instead of "{name}"')
    if name and len(name.split()) < 2:
        tips.append('• Consider providing your full name (first and last name)')

    # Email checks
    if email and not any(d in email for d in ['.com', '.in', '.org', '.net']):
        tips.append('• Double-check your email — it may be missing a valid domain extension')
    if email and email.startswith('test') or email.startswith('abc'):
        tips.append('• Use your real email address for proper registration')

    # Phone checks
    if phone and len(''.join(c for c in phone if c.isdigit())) < 10:
        tips.append('• Your phone number seems short — include all 10 digits plus country code')
    if phone and '+' not in phone:
        tips.append('• Add your country code to the phone number (e.g. +91 for India)')

    # Occupation checks
    if occupation and occupation == occupation.lower() and len(occupation) > 3:
        tips.append(f'• Capitalise your occupation — try "{occupation.title()}"')

    # Bio checks
    if not bio or bio.strip() == 'None' or bio.strip() == '':
        tips.append('• Adding a short bio helps — describe your experience and skills in 2-3 sentences')
    elif len(bio) < 30:
        tips.append('• Your bio is very short — expand it to better showcase your background')
    elif bio and bio[0] == bio[0].lower():
        tips.append('• Start your bio with a capital letter for a professional look')

    # City checks
    if city and city == city.lower():
        tips.append(f'• Capitalise your city name — try "{city.title()}"')

    if not tips:
        tips = [
            '• Your form looks well filled — great job!',
            '• All required fields are properly completed',
            '• Consider adding more detail to your bio if you have not already',
        ]

    return '\n'.join(tips)


def build_suggestion_prompt(data: dict) -> str:
    return f"""Review this registration form and give 4-5 bullet-point suggestions.
Focus on: name formatting, email, phone, bio quality, professionalism. Max 80 words.

- Full Name : {data.get('full_name', '')}
- Email     : {data.get('email', '')}
- Phone     : {data.get('phone', '')}
- DOB       : {data.get('date_of_birth', '')}
- Address   : {data.get('address', '')}
- City      : {data.get('city', '')}
- Occupation: {data.get('occupation', '')}
- Bio       : {data.get('bio', '')}"""


def form_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            ai_text = call_gemini(build_suggestion_prompt(form.cleaned_data))
            submission.ai_suggestions = ai_text
            submission.save()
            return render(request, 'form_app/success.html', {
                'submission': submission,
                'ai_suggestions': ai_text,
            })
        return render(request, 'form_app/form.html', {'form': form})
    return render(request, 'form_app/form.html', {'form': UserRegistrationForm()})


@csrf_exempt
def ai_suggest_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    suggestion = call_gemini(build_suggestion_prompt(data))
    return JsonResponse({'suggestion': suggestion})


def submissions_view(request):
    submissions = FormSubmission.objects.all()
    return render(request, 'form_app/submissions.html', {'submissions': submissions})
