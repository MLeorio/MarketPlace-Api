from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt


class User(Model):
    id = fields.UUIDField(pk=True, unique=True)
    fullname = fields.CharField(max_length=100, unique=True, null=False)
    email = fields.CharField(80, unique=True, null=False)
    tel = fields.CharField(50, unique=True, null=False)
    password = fields.CharField(max_length=255, default=bcrypt.hash("admin"))
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
    id = fields.BigIntField(pk=True, index=True)
    nom = fields.CharField(max_length=150, null=False)
    prenom = fields.CharField(max_length=255, null=False)
    tel = fields.CharField(max_length=20, null=False, unique=True)
    mail = fields.CharField(max_length=100, null=False, unique=True)
    statut = fields.CharField(50, null=False, default="active")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "SELLER"
        unique_together = ("nom", "prenom")
    
    def __str__(self) -> str:
        return self.nom + " " + self.prenom + "/" + self.statut


class Offre(Model):
    id = fields.BigIntField(pk=True, index=True)
    libelle = fields.CharField(max_length=100, unique=True, null=False)
    description = fields.CharField(max_length=255)
    prix = fields.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    quantite = fields.IntField(default=0)
    sort = fields.CharField(max_length=80, null=False, default="Bien")
    owner = fields.ForeignKeyField(model_name="models.Seller",related_name="offre", on_delete="CASCADE")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "OFFRE"
        
    def __str__(self) -> str:
        return self.libelle + " : " + self.sort


user_Pydantic = pydantic_model_creator(User, name='User')
userIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

seller_pydantic = pydantic_model_creator(Seller, name="Seller")
sellerIn_pydantic = pydantic_model_creator(Seller, name="SellerIn", exclude_readonly=True)

offre_pydantic = pydantic_model_creator(Offre, name="Offre")
offreIn_pydantic = pydantic_model_creator(Offre, name="OffreIn", exclude_readonly=True)
