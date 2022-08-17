from msilib.schema import tables
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt

class User(Model):
    id = fields.UUIDField(pk=True)
    fullname = fields.CharField(max_length=100, unique=True)
    email = fields.CharField(80, unique=True)
    tel = fields.CharField(50, unique=True)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "USER"
        
    def __str__(self) -> str:
        return self.fullname
        
        
    @classmethod
    async def get_user(cls, fullname):
        return cls.get(fullname=fullname)
    
    def verif_password(self, password):
        return bcrypt.verify(password, self.password)




class Seller(Model):
    id = fields.BigIntField(pk=True)
    nom = fields.CharField(max_length=150)
    prenom = fields.CharField(max_length=255)
    tel = fields.CharField(max_length=20)
    mail = fields.CharField(max_length=100)
    statut = fields.CharField(50)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "SELLER"
        unique = ("nom", "prenom", "tel", "mail", "statut")
    
    def __str__(self) -> str:
        return self.nom + " " + self.prenom + "/" + self.statut



# class Offre(Model):
#     id = fields.BigIntField(pk=True)
#     libelle = fields.CharField(max_length=100)
#     description = fields.CharField(max_length=255)
#     prix = fields.FloatField()
#     quantite = fields.IntField()
#     sort = fields.CharEnumField(typeOffre)


user_Pydantic = pydantic_model_creator(User, name='User')
userIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)