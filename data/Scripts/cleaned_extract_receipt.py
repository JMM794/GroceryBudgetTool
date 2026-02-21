import os
import requests
import time

import pyodbc

endpoint = "https://reciepttool.cognitiveservices.azure.com/"
key = #AzureKey
model_id = "prebuilt-receipt"

headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/pdf"
}

folder = "C:\\Users\\Owner\\Desktop\\Costco\\GroceryBudgetTool\\data\\raw_pdfs"
for filename in  os.listdir(folder):
    if filename.endswith(".pdf"):
        print(f"\n📄 Processing: {filename}")
        filepath = os.path.join(folder, filename)

        with open(filepath, "rb") as f:
            data = f.read()

        submit_response = requests.post(
            f"{endpoint}/formrecognizer/documentModels/{model_id}:analyze?api-version=2022-08-31",
            headers=headers,
            data=data
        )

        operation_url = submit_response.headers.get("Operation-Location")
        if not operation_url:
            print("❌ No operation URL returned.")
            continue

        while True:
            result_response = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": key})
            result_json = result_response.json()
            status = result_json.get("status")

            if status in ["succeeded", "failed"]:
                break
            time.sleep(1)

        try:
            doc = result_json["analyzeResult"]["documents"][0]
            fields = doc["fields"]

            merchant = fields.get("MerchantName", {}).get("valueString")
            date = fields.get("TransactionDate", {}).get("valueDate")
            total = fields.get("Total", {}).get("valueNumber")

            items = []
            for item in fields.get("Items", {}).get("valueArray", []):
                obj = item.get("valueObject", {})
                description = obj.get("Description", {}).get("valueString")
                price = obj.get("TotalPrice", {}).get("valueNumber")
                items.append((description, price))

            print("Merchant:", merchant)
            print("Date:", date)
            print("Total:", total)
            print("Items:")
            for desc, price in items:
                print(f"  - {desc}: ${price}")

        except Exception as e:
            print("❌ Failed to parse receipt:", e)

# Store in database
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost,1433;"
        "Database=GroceryBudget;"
        "UID=sa;"
        "PWD=Project_002FINC;"
            )

    cursor = conn.cursor()

    # Insert into Receipts table
    cursor.execute("""
        INSERT INTO Receipts (Merchant, TransactionDate, TotalAmount, FileName)
        OUTPUT INSERTED.ReceiptID
        VALUES (?, ?, ?, ?)
    """, merchant, date, total, filename)

    receipt_id = cursor.fetchone()[0]

    # Insert each item
    for desc, price in items:
        cursor.execute("""
            INSERT INTO ReceiptItems (ReceiptID, Description, Price)
            VALUES (?, ?, ?)
        """, receipt_id, desc, price)

    conn.commit()