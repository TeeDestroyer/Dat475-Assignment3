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


# def convert_dictionary_to_rdf(file, data, output_file):
#     for row in data:
#         for key, value in row.items():
#             if value != "":
#                 output_file.write(f"ex:{file} ex:{key} \"{value}\" .\n")

def convert_dictionary_to_rdf(file, data, output_file, all_data=None):
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

        # Add object properties based on entity type and data
        if all_data:
            add_object_properties(file, row, subject, output_file, all_data)

        output_file.write("\n")


def add_object_properties(file, row, subject, output_file, all_data):
    """Add object properties linking entities based on ontology relationships"""
    
    # Hours dependencies
    if file == "Hours":
        # Link to Teachers via teacherID
        if "teacherID" in row and row["teacherID"]:
            teacher_subject = find_entity_by_field("Teachers", "teacherID", row["teacherID"], all_data)
            if teacher_subject:
                output_file.write(f"ex:{subject} ex:DepedentOnEmployee ex:{teacher_subject} .\n")
        
        # Link to Course_Instances via courseInstance
        if "courseInstance" in row and row["courseInstance"]:
            course_instance_subject = find_entity_by_field("Course_Instances", "courseInstance", row["courseInstance"], all_data)
            if course_instance_subject:
                output_file.write(f"ex:{subject} ex:DependentOnCourseInstances ex:{course_instance_subject} .\n")
    
    # Registrations dependencies
    elif file == "Registrations":
        # Link to Students
        if "studentID" in row and row["studentID"]:
            student_subject = find_entity_by_field("Students", "studentID", row["studentID"], all_data)
            if student_subject:
                output_file.write(f"ex:{subject} ex:DependentOnStudents ex:{student_subject} .\n")
        
        # Link to Course_Instances
        if "courseInstance" in row and row["courseInstance"]:
            course_instance_subject = find_entity_by_field("Course_Instances", "courseInstance", row["courseInstance"], all_data)
            if course_instance_subject:
                output_file.write(f"ex:{subject} ex:hasCourseInstances ex:{course_instance_subject} .\n")


def find_entity_by_field(entity_type, field_name, field_value, all_data):
    """Find an entity by field value and return its subject identifier"""
    if entity_type in all_data:
        for i, row in enumerate(all_data[entity_type], start=1):
            if row.get(field_name) == field_value:
                return f"{entity_type}_{i}"
    return None


                

def main():
    f = open("ttl/output.ttl", "w")
    model = open("ttl/model.ttl")
    f.write(model.read())
    model.close()
    f.write("@prefix ex: <http://www.semanticweb.org/DAT475-Group1/ontologies/2026/3/untitled-ontology-12/> .\n")
    f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
    f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")
    
    # Process Hours.csv with added reportedHours column
    with open("csv/Assigned_Hours.csv", "r") as assigned_hours_file:
        reader = csv.DictReader(assigned_hours_file)
        rows = list(reader)
    # Read reported hours data
    reported_hours_data = get_data_from_csv("csv/Reported_Hours.csv")
    # Create a lookup dictionary for reported hours
    reported_hours_dict = {}
    for row in reported_hours_data:
        key = (row["CourseCode"], row["TeacherID"])
        reported_hours_dict[key] = row["Hours"]
    
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

    # Convert to RDF with dependencies
    for file in files:
        data = all_data[file]
        convert_dictionary_to_rdf(file, data, f, all_data)

    f.close()
    

if __name__ == "__main__":  
    main()
    
    




    