# routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from .db import get_db
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Pydantic models
class UserCreate(BaseModel):
    rn: int
    na: str
    m: int

class UserUpdate(BaseModel):
    na: Optional[str] = None
    m: Optional[int] = None

# Existing GET endpoints
@router.get("/users/", response_model=list)
async def read_users(db=Depends(get_db)):
    cursor, _ = db
    query = "SELECT rn, na, m FROM stu"
    cursor.execute(query)
    users = [{"rn": user["rn"], "na": user["na"], "m": user["m"]} for user in cursor.fetchall()]
    return users

@router.get("/users/{rn}", response_model=dict)
async def read_user(rn: int, db=Depends(get_db)):
    cursor, _ = db
    query = "SELECT rn, na, m FROM stu WHERE rn = %s"
    cursor.execute(query, (rn,))
    user = cursor.fetchone()
    if user:
        return {"rn": user["rn"], "na": user["na"], "m": user["m"]}
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/users/{rn}", response_model=dict)
async def delete_user(rn: int, db=Depends(get_db)):
    cursor, connection = db
    try:
        # Check if the user exists
        query = "SELECT rn, na, m FROM stu WHERE rn = %s"
        cursor.execute(query, (rn,))
        user = cursor.fetchone()
        if not user:
            logger.debug(f"User with rn {rn} not found.")
            raise HTTPException(status_code=404, detail="User not found")

        # Debug: Print the user data to verify
        logger.debug(f"User to delete: {user}")

        # Delete the user
        delete_query = "DELETE FROM stu WHERE rn = %s"
        cursor.execute(delete_query, (rn,))

        # Commit the transaction on the connection object
        connection.commit()

        # Debug: Confirm deletion
        cursor.execute(query, (rn,))
        user = cursor.fetchone()
        logger.debug(f"User after deletion (should be None): {user}")

        return {"message": "User deleted successfully"}

    except Exception as e:
        # Debug: Print any exceptions
        logger.error(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# New POST endpoint to insert a user
@router.post("/users/", response_model=dict)
async def create_user(user: UserCreate, db=Depends(get_db)):
    cursor, connection = db
    try:
        # Insert the user
        insert_query = "INSERT INTO stu (rn, na, m) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (user.rn, user.na, user.m))

        # Commit the transaction on the connection object
        connection.commit()

        # Debug: Confirm insertion
        logger.debug(f"User created: {user}")

        return {"message": "User created successfully"}

    except Exception as e:
        # Debug: Print any exceptions
        logger.error(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update endpoint
@router.put("/users/{rn}", response_model=dict)
async def update_user(rn: int, user: UserUpdate, db=Depends(get_db)):
    cursor, connection = db
    try:
        # Check if the user exists
        query = "SELECT rn, na, m FROM stu WHERE rn = %s"
        cursor.execute(query, (rn,))
        existing_user = cursor.fetchone()
        if not existing_user:
            logger.debug(f"User with rn {rn} not found.")
            raise HTTPException(status_code=404, detail="User not found")

        # Update the user
        update_data = user.dict(exclude_unset=True)  # Get only provided fields
        if update_data:
            update_query = "UPDATE stu SET "
            update_values = []
            for key, value in update_data.items():
                update_query += f"{key} = %s, "
                update_values.append(value)
            update_query = update_query.rstrip(", ") + " WHERE rn = %s"
            update_values.append(rn)

            cursor.execute(update_query, update_values)
            connection.commit()

        # Fetch and return updated user
        cursor.execute(query, (rn,))
        updated_user = cursor.fetchone()
        return {"message": "User updated successfully", "user": updated_user}

    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
