from django.shortcuts import render
from django.views import View

class LoginView(View):
    def post(self, request):
        print(request.session)
        return redirect('/')
