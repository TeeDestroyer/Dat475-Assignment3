import csv
from pyexpat import model

def get_data_from_csv(file_path):
    data = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data


#@prefix : <http://www.semanticweb.org/DAT475-Group1/ontologies/2026/3/untitled-ontology-12/> .


def convert_dictionary_to_rdf(file, data, output_file):
    for row in data:
        for key, value in row.items():
            if value != "":
                output_file.write(f"ex:{file} ex:{key} \"{value}\" .\n")

                

def main():
    f = open("ttl/output.ttl", "w")
    model = open("ttl/model.ttl")
    f.write(model.read())
    model.close()
    f.write("@prefix ex: <http://www.semanticweb.org/DAT475-Group1/ontologies/2026/3/untitled-ontology-12/> . \n\n")
    # Process Hours.csv with added reportedHours column
    # ¤ Write to Hours.csv with reportedHours column
    with open("csv/Assigned_Hours.csv", "r") as assigned_hours_file:
        reader = csv.DictReader(assigned_hours_file)
        rows = list(reader)
    # Read reported hours data
    reported_hours_data = get_data_from_csv("csv/Reported_Hours.csv")
    # Create a lookup dictionary for reported hours
    reported_hours_dict = {}
    for row in reported_hours_data:
        key = (row["courseCode"], row["teacherID"])
        reported_hours_dict[key] = row["hours"]
    
    # Write to Hours.csv with reportedHours column
    with open("csv/Hours.csv", "w", newline='') as hours_file:
        fieldnames = reader.fieldnames + ["reportedHours"]
        writer = csv.DictWriter(hours_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # For-loop through reported hours and add matched rows
            key = (row["courseInstance"], row["teacherID"])
            if key in reported_hours_dict:
                row["reportedHours"] = reported_hours_dict[key]
            else:
                row["reportedHours"] = "0"
            writer.writerow(row)


    files = [
    "Courses_Planning",
    "Courses",
    "Hours",
    "Program_Courses",
    "Programs",
    "Registrations",
    "Senior_Teachers",
    "Students",
    "Teaching_Assistants"
    ]

    for file in files:
        file_path = f"csv/{file}.csv"
        data = get_data_from_csv(file_path)
        convert_dictionary_to_rdf(file, data, f)


    f.close()
    

if __name__ == "__main__":  
    main()
    
    




    