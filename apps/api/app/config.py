from pydantic import BaseModel
class Settings(BaseModel):
    app_name:str="Advance Trading System"
    environment:str="development"
    database_url:str="postgresql://ats:ats@localhost:5432/ats"
settings=Settings()
