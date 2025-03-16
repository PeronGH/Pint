import csv
model_data = {}


    
def process_rows(rows):
    global model_data
    for row in rows:
        # Convert the first cell to string, handling None case
        first_cell = str(row[0]).strip() if row[0] is not None else ""
        
        # Skip empty rows or rows with empty first cell
        if not row or first_cell == "":
            continue
        
        key = first_cell
        
        # Convert all other cells to strings, handling None case
        values = []
        for item in row[1:]:
            item_str = str(item).strip() if item is not None else ""
            if item_str:  # Only add non-empty strings
                values.append(item_str)
                
        model_data[key] = values[0] if len(values) == 1 else values
    
def load_model_data(filename):
    global model_data
    model_data = {}

    if filename.lower().endswith(".csv"):
        with open(filename, "r", newline="") as f:
            reader = csv.reader(f)
            process_rows(reader)
    elif filename.lower().endswith(".xlsx"):
        try:
            import openpyxl
        except:
            raise RuntimeError("To use an Excel file openpyxl must be installed.  csv files need no other libraries.")           
        wb = openpyxl.load_workbook(filename, data_only=True)
        sheet = wb.active
        process_rows(sheet.iter_rows(values_only=True))
    
 
    
def get_model_data():
    return model_data