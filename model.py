from msilib.schema import tables
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

# typeOffre = ["Bien", "Service"]


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


 Enum typeOffre = [
     ""
 ]


class Offre(Model):
    id = fields.BigIntField(pk=True)
    libelle = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255)
    prix = fields.FloatField()
    quantite = fields.IntField()
    sort = fields.CharEnumField(typeOffre)