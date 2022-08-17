from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise
from passlib.hash import bcrypt
from model import User, user_Pydantic, userIn_Pydantic
import jwt

app = FastAPI(title="Market-Place Api", version="1.0.2")

JWT_SECRET = "myJwtSecret"

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['model']},
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


async def authenticate_user(username:str, password:str):
    user = await User.get(email=username)
    if not user:
        return False
    if not user.verif_password(password):
        return False
    return user

@app.post("/token")
async def generate_token(form_data:OAuth2PasswordRequestForm=Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        return {'Erreur': "Coordonnees invalides"}
    
    user_obj = await userIn_Pydantic.from_tortoise_orm(user)
    
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    
    return {'access_token': token, 'token_type':'bearer'}

@app.get("/")
async def index(token:str = Depends(oauth2_scheme)):
    return {'the_token' : token,
            'hello' : "world"}

@app.get("/users")
async def get_users():
    users = await User.all()
    return users