import csv
from pyexpat import model

def get_data_from_csv(file_path):
    data = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data


def convert_dictionary_to_rdf(file, data, output_file):
    for i, row in enumerate(data, start=1):

        # Create unique subject
        subject = f"{file}_{i}"

        # RDF type
        output_file.write(
            f"ex:{subject} rdf:type ex:{file} .\n"
        )

        for key, value in row.items():

            if value == "":
                continue

            # Detect numeric values
            try:
                float_value = float(value)

                # Integer
                if float_value.is_integer():
                    output_file.write(
                        f'ex:{subject} ex:{key} {int(float_value)} .\n'
                    )

                # Float
                else:
                    output_file.write(
                        f'ex:{subject} ex:{key} {float_value} .\n'
                    )

            # String
            except ValueError:
                safe_value = value.replace('"', '\\"')

                output_file.write(
                    f'ex:{subject} ex:{key} "{safe_value}" .\n'
                )

        output_file.write("\n")


def generate_dependencies(all_data, output_file):
    """Generate object properties linking entities based on ontology relationships"""
    
    # Build lookup dictionaries for each entity type by their key identifiers
    entity_maps = {}
    
    # Teachers lookup by teacherID
    if "Teachers" in all_data:
        entity_maps["Teachers"] = {}
        for i, row in enumerate(all_data["Teachers"], start=1):
            if "teacherID" in row and row["teacherID"]:
                entity_maps["Teachers"][row["teacherID"]] = f"Teachers_{i}"
    
    # Students lookup by studentID
    if "Students" in all_data:
        entity_maps["Students"] = {}
        for i, row in enumerate(all_data["Students"], start=1):
            if "studentID" in row and row["studentID"]:
                entity_maps["Students"][row["studentID"]] = f"Students_{i}"
    
    # Senior_Teachers lookup by teacherID
    if "Senior_Teachers" in all_data:
        entity_maps["Senior_Teachers"] = {}
        for i, row in enumerate(all_data["Senior_Teachers"], start=1):
            if "teacherID" in row and row["teacherID"]:
                entity_maps["Senior_Teachers"][row["teacherID"]] = f"Senior_Teachers_{i}"
    
    # Teaching_Assistants lookup by studentID
    if "Teaching_Assistants" in all_data:
        entity_maps["Teaching_Assistants"] = {}
        for i, row in enumerate(all_data["Teaching_Assistants"], start=1):
            if "studentID" in row and row["studentID"]:
                entity_maps["Teaching_Assistants"][row["studentID"]] = f"Teaching_Assistants_{i}"
    
    # Courses lookup by courseCode
    if "Courses" in all_data:
        entity_maps["Courses"] = {}
        for i, row in enumerate(all_data["Courses"], start=1):
            if "courseCode" in row and row["courseCode"]:
                entity_maps["Courses"][row["courseCode"]] = f"Courses_{i}"
    
    # Programs lookup by programCode
    if "Programs" in all_data:
        entity_maps["Programs"] = {}
        for i, row in enumerate(all_data["Programs"], start=1):
            if "programCode" in row and row["programCode"]:
                entity_maps["Programs"][row["programCode"]] = f"Programs_{i}"
    
    # Courses_Planning lookup by course (courseInstance)
    if "Courses_Planning" in all_data:
        entity_maps["Courses_Planning"] = {}
        for i, row in enumerate(all_data["Courses_Planning"], start=1):
            if "course" in row and row["course"]:
                entity_maps["Courses_Planning"][row["course"]] = f"Courses_Planning_{i}"
    
    # Program_Courses lookup by courseCode
    if "Program_Courses" in all_data:
        entity_maps["Program_Courses"] = {}
        for i, row in enumerate(all_data["Program_Courses"], start=1):
            if "courseCode" in row and row["courseCode"]:
                entity_maps["Program_Courses"][row["courseCode"]] = f"Program_Courses_{i}"
    
    # Registrations lookup by courseInstance and studentID
    if "Registrations" in all_data:
        entity_maps["Registrations"] = {}
        for i, row in enumerate(all_data["Registrations"], start=1):
            key = (row.get("courseInstance", ""), row.get("studentID", ""))
            if key[0] and key[1]:
                entity_maps["Registrations"][key] = f"Registrations_{i}"
    
    # Generate object properties
    output_file.write("\n# Object Properties / Dependencies\n\n")
    
    # Hours dependencies
    if "Hours" in all_data:
        for i, row in enumerate(all_data["Hours"], start=1):
            subject = f"Hours_{i}"
            
            # Link to Teachers via teacherID (DepedentOnEmployee, hasEmployee)
            if "teacherID" in row and row["teacherID"] in entity_maps.get("Teachers", {}):
                target = entity_maps["Teachers"][row["teacherID"]]
                output_file.write(f"ex:{subject} ex:DepedentOnEmployee ex:{target} .\n")
                output_file.write(f"ex:{subject} ex:hasEmployee ex:{target} .\n")
            
            # Link to Courses_Planning via courseInstance (DependentOnCourseInstances, hasHours)
            if "courseInstance" in row and row["courseInstance"] in entity_maps.get("Courses_Planning", {}):
                target = entity_maps["Courses_Planning"][row["courseInstance"]]
                output_file.write(f"ex:{subject} ex:DependentOnCourseInstances ex:{target} .\n")
    
    # Registrations dependencies
    if "Registrations" in all_data:
        for i, row in enumerate(all_data["Registrations"], start=1):
            subject = f"Registrations_{i}"
            
            # Link to Students via studentID (DependentOnStudents)
            if "studentID" in row and row["studentID"] in entity_maps.get("Students", {}):
                target = entity_maps["Students"][row["studentID"]]
                output_file.write(f"ex:{subject} ex:DependentOnStudents ex:{target} .\n")
            
            # Link to Courses_Planning via courseInstance (hasCourseInstances, DependentOnCourseInstances)
            if "courseInstance" in row and row["courseInstance"] in entity_maps.get("Courses_Planning", {}):
                target = entity_maps["Courses_Planning"][row["courseInstance"]]
                output_file.write(f"ex:{subject} ex:hasCourseInstances ex:{target} .\n")
                output_file.write(f"ex:{subject} ex:DependentOnCourseInstances ex:{target} .\n")
    
    # Courses_Planning dependencies
    if "Courses_Planning" in all_data:
        for i, row in enumerate(all_data["Courses_Planning"], start=1):
            subject = f"Courses_Planning_{i}"
            
            # Link to Hours via courseInstance (hasHours)
            if "course" in row and row["course"]:
                if "Hours" in all_data:
                    for j, hour_row in enumerate(all_data["Hours"], start=1):
                        if hour_row.get("courseInstance") == row["course"]:
                            target = f"Hours_{j}"
                            output_file.write(f"ex:{subject} ex:hasHours ex:{target} .\n")
    
    # Program_Courses dependencies
    if "Program_Courses" in all_data:
        for i, row in enumerate(all_data["Program_Courses"], start=1):
            subject = f"Program_Courses_{i}"
            
            # Link to Programs via programCode (hasPrograms)
            if "programCode" in row and row["programCode"] in entity_maps.get("Programs", {}):
                target = entity_maps["Programs"][row["programCode"]]
                output_file.write(f"ex:{subject} ex:hasPrograms ex:{target} .\n")
            

    # Courses dependencies
    if "Courses" in all_data:
        for i, row in enumerate(all_data["Courses"], start=1):
            subject = f"Courses_{i}"
            
            # Link to Programs via programCode (hasOwner)
            if "programCode" in row and row["programCode"] in entity_maps.get("Programs", {}):
                target = entity_maps["Programs"][row["programCode"]]
                output_file.write(f"ex:{subject} ex:hasOwner ex:{target} .\n")
    
    # Programs dependencies
    if "Programs" in all_data:
        for i, row in enumerate(all_data["Programs"], start=1):
            subject = f"Programs_{i}"
            
            # Link to Senior_Teachers via directorID (hasDirector)
            if "teacherID" in row and row["teacherID"] in entity_maps.get("Senior_Teachers", {}):
                target = entity_maps["Senior_Teachers"][row["teacherID"]]
                output_file.write(f"ex:{subject} ex:hasDirector ex:{target} .\n")
    
    # Students dependencies
    if "Students" in all_data:
        for i, row in enumerate(all_data["Students"], start=1):
            subject = f"Students_{i}"

            



            
            # Link to Registrations via studentID (hasRegistrations)
            if "studentID" in row and row["studentID"]:
                if "Registrations" in all_data:
                    for j, reg_row in enumerate(all_data["Registrations"], start=1):
                        if reg_row.get("studentID") == row["studentID"]:
                            target = f"Registrations_{j}"
                            output_file.write(f"ex:{subject} ex:hasRegistrations ex:{target} .\n")
    
    # Teaching_Assistants dependencies
    if "Teaching_Assistants" in all_data:
        for i, row in enumerate(all_data["Teaching_Assistants"], start=1):
            subject = f"Teaching_Assistants_{i}"
            
            # Link to Teachers via teacherID (hasTeachers)
            if "teacherID" in row and row["teacherID"] in entity_maps.get("Teachers", {}):
                target = entity_maps["Teachers"][row["teacherID"]]
                output_file.write(f"ex:{subject} ex:hasTeachers ex:{target} .\n")


                

def main():
    f = open("ttl/output.ttl", "w")
    model = open("ttl/model.ttl")
    f.write(model.read())
    model.close()
    f.write("@prefix ex: <http://www.semanticweb.org/DAT475-Group1/ontologies/2026/3/untitled-ontology-12/> .\n")
    f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n")
    
    # Process Hours.csv with added reportedHours column
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

    # Load all data first
    all_data = {}
    for file in files:
        file_path = f"csv/{file}.csv"
        all_data[file] = get_data_from_csv(file_path)

    # Convert to RDF
    for file in files:
        data = all_data[file]
        convert_dictionary_to_rdf(file, data, f)

    # Generate all dependencies
    generate_dependencies(all_data, f)

    f.close()
    

if __name__ == "__main__":  
    main()
    
    




    