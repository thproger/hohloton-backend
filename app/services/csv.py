import app.db.mongo import businesses_collection
from fastapi.responses import StreamingResponse
import io
import csv

def get_csv():
    businnes = businesses_collection.find_all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(business)
    output.seek(0)

    return StreamingResponse(
        output, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=data.csv"}
    )
