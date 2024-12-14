from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import *
from .models import *
import random  # Import for random question selection

# Home Page
def home(request):
    if request.method == 'POST':
        questions = QuesModel.objects.all()
        score = 0
        correct = 0
        wrong = 0
        total = 0
        
        for q in questions:
            total += 1
            user_answer = str(request.POST.get(q.question, '')).strip().lower()
            correct_answer = str(q.ans).strip().lower()
            
            if correct_answer == user_answer:
                score += 10
                correct += 1
            else:
                wrong += 1
        
        percent = (score / (total * 10)) * 100
        context = {
            'score': score,
            'time': request.POST.get('timer', '0'),
            'correct': correct,
            'wrong': wrong,
            'percent': percent,
            'total': total
        }
        return render(request, 'Quiz/result.html', context)

    else:
        # Fetch multiple questions to display at once
        questions = QuesModel.objects.all()
        context = {'questions': questions}
        return render(request, 'Quiz/home.html', context)


# Add Question (Admin Only)
def addQuestion(request):
    if request.user.is_staff:
        form = addQuestionform()
        if request.method == 'POST':
            form = addQuestionform(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/')
        context = {'form': form}
        return render(request, 'Quiz/addQuestion.html', context)
    else:
        return redirect('home') 


# Register Page
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home') 
    else: 
        form = createuserform()
        if request.method == 'POST':
            form = createuserform(request.POST)
            if form.is_valid():
                user = form.save()
                return redirect('login')
        context = {'form': form}
        return render(request, 'Quiz/register.html', context)


# Login Page
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        context = {}
        return render(request, 'Quiz/login.html', context)


# Logout
def logoutPage(request):
    logout(request)
    return redirect('/')


# Quiz Result Page
def quiz_result(request):
    if request.method == 'POST':
        questions = request.session.get('questions', [])
        correct_answers = 0
        total_questions = len(questions)
        user_answers = request.POST
        
        for question in questions:
            if user_answers.get(question['question']) == question['correct_answer']:
                correct_answers += 1
        
        incorrect_answers = total_questions - correct_answers
        score = correct_answers
        percent = (correct_answers / total_questions) * 100 if total_questions else 0
        time_taken = request.POST.get('timer', '0')

        context = {
            'score': score,
            'percent': round(percent, 2),
            'time': time_taken,
            'correct': correct_answers,
            'wrong': incorrect_answers,
            'total': total_questions,
        }

        return render(request, 'Quiz/result.html', context)

    return HttpResponseRedirect(reverse('home'))
