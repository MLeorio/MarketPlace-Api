from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise, HTTPNotFoundError
from passlib.hash import bcrypt
from models import User, user_Pydantic, userIn_Pydantic, Seller, seller_pydantic, sellerIn_pydantic, Offre, offre_pydantic, offreIn_pydantic
import jwt
from pydantic import BaseModel

app = FastAPI(title="Market-Place Api", version="1.0.2", description="Api pour la gestion d'un MarketPlace. Une clé d'authentification est obligatoire pour l'exécution des requêtes !")

class Message(BaseModel):
    message:str

JWT_SECRET = "myJwtSecret"

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.post("/users", response_model=user_Pydantic)
async def create_user(user: userIn_Pydantic):
    user_obj = User(
        fullname=user.fullname,
        email=user.email,
        tel=user.tel,
        password=bcrypt.hash(user.password),
        )
    await user_obj.save()
    return await user_Pydantic.from_tortoise_orm(user_obj)

async def verify_token(token:str = Depends(oauth2_scheme)):
    try:
        user_obj = jwt.decode(token, JWT_SECRET, algorithms="HS256")
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Token non accepter")
    
    try:
        user = await User.get(email=user_obj.get('email'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non autorisé")
    
    return token

async def authenticate_user(username:str, password:str):
    user = await User.get(email=username)
    if not user:
        return False
    if not user.verif_password(password):
        return False
    return user

async def get_current_user(token:str = Depends(oauth2_scheme)):
    try:
        user_auth_obj = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Token non accepter")
    
    try:
        user = await User.get(email=user_auth_obj['email'])
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        
    return await user_Pydantic.from_tortoise_orm(user)

@app.post("/token")
async def generate_token(form_data:OAuth2PasswordRequestForm=Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Coordonnees non valides")
    
    user_obj = await userIn_Pydantic.from_tortoise_orm(user)
    
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    
    return {'Statut': 200, 'Message': 'Connexion reussie', 'access_token': token, 'token_type':'bearer'}


@app.get("/users")
async def get_users(token:str = Depends(verify_token)):
    users = await User.all()
    return users

@app.get("/users/me", response_model=user_Pydantic)
async def get_user(user:user_Pydantic = Depends(get_current_user)):
    return user

@app.get("/")
async def index(token:str = Depends(oauth2_scheme)):
    return {'the_token' : token,
            'hello' : "world"}

###########################
#    Route for Sellers    #
###########################

@app.get("/sellers")
async def get_sellers(token:str = Depends(verify_token)):
    """Retourne tous les vendeurs inscrits dans la base de donnees

    Args:
        token (str, optional): Token de l'utilisateur qui doit etre fourni obligatoirement. Defaults to Depends(oauth2_scheme).
    """
    sellers = await Seller.all()
    return sellers

@app.get("/sellers/{id}", response_model=sellerIn_pydantic, responses={404:{'model':HTTPNotFoundError}})
async def get_one_seller(id:int, token:str = Depends(verify_token)):
    try:
        seller = await Seller.get(id=id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client non trouvé")
    
    return await sellerIn_pydantic.from_tortoise_orm(seller)
    

@app.post("/sellers", response_model=seller_pydantic)
async def add_seller(seller:sellerIn_pydantic, token:str = Depends(verify_token)):
    seller_obj = Seller(
        nom = seller.nom,
        prenom = seller.prenom,
        tel = seller.tel,
        mail = seller.mail,
        statut = seller.statut
    )
    await seller_obj.save()
    return await seller_pydantic.from_tortoise_orm(seller_obj)

@app.put("/sellers/{id}", response_model=seller_pydantic, responses={404: {'model': HTTPNotFoundError}})
async def update_seller(id:int, seller:sellerIn_pydantic, token:str = Depends(verify_token)):
    await Seller.filter(id=id).update(**seller.dict(exclude_unset=True))
    return await seller_pydantic.from_queryset_single(Seller.get(id=id))

@app.delete("/sellers/{id}", response_model=Message, responses={404:{'model':HTTPNotFoundError}})
async def delete_seller(id:int, token:str = Depends(verify_token)):
    seller_deleted = await Seller.filter(id=id).delete()
    if not seller_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client non trouvé")
    return Message(message = "Client supprimé avec succès")


###########################
#     Route for Offres    #
###########################

@app.get("/offres")
async def get_offres(token:str = Depends(verify_token)):
    """Retourne tous les offres enregistrees dans la base de donnees

    Args:
        token (str, optional): Token de l'utilisateur qui doit etre fourni obligatoirement. Defaults to Depends(oauth2_scheme).
    """
    offres = await Offre.all()
    return offres

@app.get("/offres/{id}", response_model=offreIn_pydantic, responses={404:{'model':HTTPNotFoundError}})
async def get_one_seller(id:int, token:str = Depends(verify_token)):
    """Retourne une offre bien preciser par son id fournie en parametre

    Args:
        id (int): Identifiant de l'offre souhaitee
        token (str, optional): Token de l'utilisateur qui doit etre fourni obligatoirement. Defaults to Depends(verify_token).
    """
    try:
        offre = await Offre.get(id=id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit non trouvé")
    
    return await offreIn_pydantic.from_tortoise_orm(offre)


@app.post("/offres", response_model=offre_pydantic)
async def add_seller(offre:offreIn_pydantic, token:str = Depends(verify_token)):
    """Enregistre une offre pour un client

    Args:
        offre (offreIn_pydantic): Informations necessaires pour une offre
        token (str, optional): Token de l'utilisateur qui doit etre fourni obligatoirement. Defaults to Depends(verify_token).

    Returns:
        offre_obj: Objet Offre qui vient d'etre enregistrer
    """
    print(offre.dict())
    offre_obj = Offre(
        libelle = offre.libelle,
        description = offre.description,
        prix = offre.prix,
        quantite = offre.quantite,
        sort = offre.sort,
        owner_id = offre.owner
    )
    await offre_obj.save()
    return await offre_pydantic.from_tortoise_orm(offre_obj)