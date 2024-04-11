from business.models.user import User
from django.http import JsonResponse
import json


def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(username=username, password=password).first()
        if user:
            request.session['username'] = user.username
            return JsonResponse({'user_id': user.user_id, 'username': user.username, 'avatar': user.avatar.url})
        else:
            return JsonResponse({'error': '用户名或密码错误'}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误'}, status=400)


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(username=username).first()
        if user:
            return JsonResponse({'error': '用户名已存在'}, status=400)
        else:
            user = User(username=username, password=password)
            user.save()
            return JsonResponse({'user_id': user.user_id, 'username': user.username, 'avatar': user.avatar.url})
    else:
        return JsonResponse({'error': '请求方法错误'}, status=400)


def testLogin(request):
    if request.method == 'GET':
        username = request.session.get('username')
        return JsonResponse({'username': username})
    else:
        return JsonResponse({'error': '请求方法错误'}, status=400)
