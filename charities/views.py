from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task
from charities.serializers import (
    TaskSerializer, CharitySerializer, BenefactorSerializer
)
from .models import *
from rest_framework.permissions import IsAuthenticated

from rest_framework.request import Request


#tests.testsample_task_done.py
class BenefactorRegistration(APIView):
#    permission_classes = (IsAuthenticated, )
    def post(self, request):
        benef = BenefactorSerializer(data= request.data)
        if benef.is_valid():
            benef.save(user=request.user)
            return Response(status=200)
    pass


class CharityRegistration(CreateAPIView):
   # permission_classes = (IsAuthenticated,)

    def post(self, request):
        cha = CharitySerializer(data=request.data)
        if cha.is_valid():
            cha.save(user=request.user)
            return Response(status=200)
    pass


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    def get(self, request, task_id):
        try:
            user= Benefactor.objects.get(user= request.user)
            try:
                query = Task.objects.get(id= task_id)
                if not query.state=='P':
                    return Response(data= {'detail': 'This task is not pending.'},status=404)
                else:
                    query.state='W'
                    query.assigned_benefactor= user
                    query.save()
                    data = {'detail': 'Request sent.'}
                    return Response(data= data, status=200)
            except Task.DoesNotExist:
                return Response(data= {}, status=404)
        except Benefactor.DoesNotExist:
            return Response(data={}, status=403)

    pass


class TaskResponse(APIView):
    def post(self, request, task_id):
        try:
            user= Charity.objects.get(user= request.user)
            response = request.data.get("response")
            if response!='A' and response!='R':
                return Response(data= {'detail': 'Required field ("A" for accepted / "R" for rejected)'}, status=400)
            try:
                task= Task.objects.get(id= task_id)
                if not task.state=='W':
                    return Response(data={'detail': 'This task is not waiting.'}, status=404)
                elif response=='A':
                    task.state= 'A'
                    task.save()
                    return Response(data={'detail': 'Response sent.'}, status=200)
                elif response=='R':
                    task.state = 'P'
                    task.assigned_benefactor= None
                    task.save()
                    return Response(data={'detail': 'Response sent.'}, status=200)
            except Task.DoesNotExist:
                return Response(data={}, status=404)
        except Charity.DoesNotExist:
            return Response(data={}, status=403)
    pass


class DoneTask(APIView):
    def post(self, request, task_id):
        try:
            user = Charity.objects.get(user=request.user)
            try:
                task = Task.objects.get(id=task_id)
                if not task.state=='A':
                    return Response(data={'detail': 'Task is not assigned yet.'}, status=404)
                else:
                    task.state='D'
                    task.save()
                    return Response(data={'detail': 'Task has been done successfully.'}, status=200)
            except Task.DoesNotExist:
                return Response(data={}, status=404)
        except Charity.DoesNotExist:
            return Response(data={}, status=403)
    pass


