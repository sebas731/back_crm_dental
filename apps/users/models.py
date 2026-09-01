from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel
# Create your models here.

class User(AbstractUser):

    ROLES =[
        ("ADMIN","SOPORTE"),
        ("MANAGER","ADMINISTRADOR"),
        ("ASSISTANT","ASISTENTE"),
        ("MEDICO","MÉDICO")
    ]

    rol = models.CharField(max_length=150,choices=ROLES,default="ASSISTANT")
    #property
    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class UserProfile(BaseModel):
    user = models.OneToOneField("User",on_delete=models.CASCADE)




