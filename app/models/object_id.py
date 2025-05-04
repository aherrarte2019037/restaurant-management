from bson import ObjectId
from pydantic import Field, BaseModel
from typing import Any, Optional

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, (str, ObjectId)):
            raise TypeError('Valor ObjectId debe ser str o ObjectId')
        
        if isinstance(v, str):
            try:
                ObjectId(v)
            except Exception:
                raise ValueError('ObjectId inválido')
        
        return v
    
    def to_mongo(self):
        if isinstance(self, ObjectId):
            return self
        return ObjectId(self)

    def model_dump(self):
        return self
    
    def __json__(self):
        return self

    def __repr__(self):
        return self
        
    def __str__(self):
        return self
        
    def __eq__(self, other):
        if isinstance(other, str):
            return self == other
        return False 