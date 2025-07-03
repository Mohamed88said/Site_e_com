from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def assistant(request):
    response = ""
    user_message = ""
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        # Réponse simulée IA (à remplacer par appel API réel plus tard)
        if user_message.strip():
            response = f"Vous avez dit : {user_message} (réponse simulée IA)"
        else:
            response = "Veuillez saisir un message."
    return render(request, 'ia/assistant.html', {
        'response': response,
        'user_message': user_message,
    })