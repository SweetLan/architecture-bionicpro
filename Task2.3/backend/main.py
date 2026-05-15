from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from clickhouse_driver import Client

app = FastAPI(title="BionicPRO Reports API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_clickhouse_client():
    return Client(
        host="clickhouse",
        port=9000,
        user="default",
        password="",
        database="default",
    )


@app.get("/reports")
def get_report(x_user_id: str = Header(...)):
    client = get_clickhouse_client()

    result = client.execute(
        """
        SELECT
            report_date,
            user_id,
            prosthesis_id,
            client_name,
            client_country,
            telemetry_events_count,
            avg_response_ms,
            max_response_ms,
            avg_battery_level,
            min_battery_level,
            processed_at
        FROM prosthesis_report_mart
        WHERE user_id = %(user_id)s
        ORDER BY report_date DESC
        """,
        {"user_id": x_user_id},
    )

    if not result:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "user_id": x_user_id,
        "reports": [
            {
                "report_date": str(row[0]),
                "user_id": row[1],
                "prosthesis_id": row[2],
                "client_name": row[3],
                "client_country": row[4],
                "telemetry_events_count": row[5],
                "avg_response_ms": row[6],
                "max_response_ms": row[7],
                "avg_battery_level": row[8],
                "min_battery_level": row[9],
                "processed_at": str(row[10]),
            }
            for row in result
        ],
    }