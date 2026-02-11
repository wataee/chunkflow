from fastapi import Depends
from app.core.security import get_api_key
from app.db.session import get_db

# Common reusable dependencies
AuthDependency = Depends(get_api_key)
DbDependency = Depends(get_db)
