from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import openai
import os 
from .models import Chat
from django.utils import timezone
openai_api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = openai_api_key
# Create your views here.


def askOpenAI(message):
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=message,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    # print(response)
    answer = response.choices[0].text.strip()
    return answer


def chatbot(request):
    chats = Chat.objects.filter(user=request.user.id)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = askOpenAI(message)
        if request.user.is_authenticated:
            chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now)
            chat.save()
            return JsonResponse({'message': message, 'response': response})
        else:    
            return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html',{'chats':chats})


def registerUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                login(request, user)
                return redirect('chatbot')
            except:
                error_message = "Error creating account"
            return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "password don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')


def loginUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chatbot')
        else:
            error_message = "Invaild username or password"
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('chatbot')
