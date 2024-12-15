from rest_framework import serializers

from .models import Benefactor
from .models import Charity, Task
from rest_framework.request import Request

class BenefactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefactor
        fields = ['BenefactorExperience', 'experience', 'free_time_per_week']

    pass
'''
    def create(self, validated_data, request):
        ben = Benefactor(**validated_data)
        #ben.user = request.user()
        ben.experience = request.POST.get("experience")
        ben.free_time_per_week = request.POST.get("free_time_per_week")
        #ben.save()
        ben.save(user=request.user)
        return ben
'''



class CharitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Charity
        fields = ['name', 'reg_number']

    pass
'''
    def create(self, validated_data, request):
        cha = Charity(**validated_data)
        #cha.user = request.user()
        cha.name = request.POST.get("name")
        cha.reg_number = request.POST.get("reg_number")
        #cha.save()
        cha.save(user=request.user)
        return cha
'''



class TaskSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(read_only=True, choices=Task.TaskStatus.choices)
    assigned_benefactor = BenefactorSerializer(required=False)
    charity = CharitySerializer(read_only=True)
    charity_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Charity.objects.all(), source='charity')

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'state',
            'charity',
            'charity_id',
            'description',
            'assigned_benefactor',
            'date',
            'age_limit_from',
            'age_limit_to',
            'gender_limit',
        )
