from fastapi import FastAPI, HTTPException
from db import get_connection
from config import CONTROL_SCHEMA_MAP
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Recon Chatbot API is running Properly!"}

# Api for total exception txn/records count for a control
@app.get("/exception_records/{control}")
def get_exception_record_count(control: str):

    if control not in CONTROL_SCHEMA_MAP:
        raise HTTPException(status_code=400, detail="Invalid control")

    schema = CONTROL_SCHEMA_MAP[control]

    query = f"""
        SELECT COUNT(*)
        FROM {schema}.records r
        JOIN {schema}.exceptionrecordlink erl ON r.pk = erl.recordpk
        JOIN {schema}.exceptions e ON e.pk = erl.exceptionpk
        WHERE r.activestatus IS DISTINCT FROM 5
        AND e.activestatus IS DISTINCT FROM 5
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {"control": control, "exception_count": count}




@app.get("/single_ton_exception_records/{control}")
def get_single_ton_exception_record_count(control: str):

    if control not in CONTROL_SCHEMA_MAP:
        raise HTTPException(status_code=400, detail="Invalid control")

    schema = CONTROL_SCHEMA_MAP[control]

    query = f"""
        SELECT COUNT(*)
        FROM {schema}.records r
        JOIN {schema}.exceptionrecordlink erl ON r.pk = erl.recordpk
        JOIN {schema}.exceptions e ON e.pk = erl.exceptionpk
        WHERE e.name ILIKE '%single%' AND r.activestatus IS DISTINCT FROM 5
        AND e.activestatus IS DISTINCT FROM 5
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {"control": control, "exception_count": count}





@app.get("/quantity_exceptions/details/{control}")
def get_quantity_exceptions(control: str):
    if control not in CONTROL_SCHEMA_MAP:
        raise HTTPException(status_code=400, detail="Invalid control")

    schema = CONTROL_SCHEMA_MAP[control]

    query = f"""
        SELECT
            name AS Quantity_Exception,
            netamount AS Amount_Difference,
            netquantity AS Quantity_Difference,
            trade_date,
            age
        FROM {schema}.exceptions
        WHERE name = 'TradeQuantityBreak'
          AND activestatus = 0
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    exceptions = [
        {
            "Quantity_Exception": row[0],
            "Amount_Difference": float(row[1]) if row[1] is not None else None,
            "Quantity_Difference": float(row[2]) if row[2] is not None else None,
            "trade_date": row[3],
            "age": row[4],
        }
        for row in rows
    ]

    return {"control": control, "exceptions": exceptions}



@app.get("/amount_exceptions/details/{control}")
def get_amount_exceptions(control: str):
    if control not in CONTROL_SCHEMA_MAP:
        raise HTTPException(status_code=400, detail="Invalid control")

    schema = CONTROL_SCHEMA_MAP[control]

    query = f"""
        SELECT
            name AS Amount_Exception,
            netamount AS Amount_Difference,
            netquantity AS Quantity_Difference,
            trade_date,
            age
        FROM {schema}.exceptions
        WHERE name = 'TradeAmountBreak'
          AND activestatus = 0
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    exceptions = [
        {
            "Amount_Exception": row[0],
            "Amount_Difference": float(row[1]) if row[1] is not None else None,
            "Quantity_Difference": float(row[2]) if row[2] is not None else None,
            "trade_date": row[3],
            "age": row[4],
        }
        for row in rows
    ]

    return {"control": control, "exceptions": exceptions}





@app.get("/validate_control/{control}")
def validate_control(control: str):
    if control not in CONTROL_SCHEMA_MAP:
        raise HTTPException(status_code=404, detail="Invalid control")
    return {"valid": True}


@app.get("/check_record")
def check_record(control: str, trade_date: str, age: int):

    schema = CONTROL_SCHEMA_MAP.get(control)

    conn = get_connection()
    cur = conn.cursor()

    query = f"""
        SELECT 1 FROM {schema}.exceptions
        WHERE trade_date = %s AND age = %s
        LIMIT 1
    """

    cur.execute(query, (trade_date, age))
    exists = cur.fetchone() is not None

    cur.close()
    conn.close()

    return {"exists": exists}


class UpdateRequest(BaseModel):
    control: str
    trade_date: str
    age: int
    reason: str
    resolution: str


@app.post("/update_exception")
def update_exception(req: UpdateRequest):

    schema = CONTROL_SCHEMA_MAP.get(req.control)

    conn = get_connection()
    cur = conn.cursor()

    query = f"""
        UPDATE {schema}.exceptions
        SET exceptionreasoncode = %s,
            exceptionresolutioncode = %s
        WHERE trade_date = %s AND age = %s
    """

    cur.execute(query, (
        req.reason,
        req.resolution,
        req.trade_date,
        req.age
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Record updated successfully"}