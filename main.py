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



def create_course_instances():
    column_headers = ("instanceID", "courseCode", "teacherID", "studyPeriod", "academicYear")
    assigned_hours_data = get_data_from_csv("csv/Assigned_Hours.csv")
    assigned_hours_dict = {}
    for row in assigned_hours_data:
        key = row["instanceID"]
        assigned_hours_dict[key] = (row["courseCode"], row["teacherID"], row["studyPeriod"], row["academicYear"])
    f = open("csv/Course_Instances.csv", "w", newline='')
    writer = csv.DictWriter(f, fieldnames=column_headers)
    writer.writeheader()
    for key, values in assigned_hours_dict.items():
        writer.writerow({"instanceID": key, "courseCode": values[0], "teacherID": values[1], "studyPeriod": values[2], "academicYear": values[3]})
    f.close()
    return



def create_departments():
    column_headers = ["departmentName"]
    courses_data = get_data_from_csv("csv/Courses.csv")
    department_dict = {}
    for row in courses_data:
        key = row["departmentName"]
        department_dict[key] = row["departmentName"]   
    f = open("csv/Departments.csv", "w", newline='')
    writer = csv.DictWriter(f, fieldnames=column_headers)   
    writer.writeheader()
    for department in department_dict:
        writer.writerow({"departmentName": department}) 
    f.close()
    return




def create_divisions():
    column_headers = ["divisionName", "departmentName"]
    courses_data = get_data_from_csv("csv/Courses.csv")
    division_dict = {}
    for row in courses_data:
        key = row["divisionName"]
        division_dict[key] = row["divisionName"]
    f = open("csv/Divisions.csv", "w", newline='')
    writer = csv.DictWriter(f, fieldnames=column_headers)
    writer.writeheader()
    for key in division_dict:
        writer.writerow({"divisionName": key, "departmentName": key[0:2]})
    f.close()
    return


def create_hours():
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
            key = (row["instanceID"], row["teacherID"])
            if key in reported_hours_dict:
                row["reportedHours"] = reported_hours_dict[key]
            else:
                row["reportedHours"] = "0"
            writer.writerow(row)
    return

def create_entity_maps(all_data): 
    # Build lookup dictionaries for each entity type by their key identifiers
    entity_maps = {}
    
    # Division lookup by divisionName
    if "Divisions" in all_data:
        entity_maps["Divisions"] = {}
        for i, row in enumerate(all_data["Divisions"], start=1):
            if "divisionName" in row and row["divisionName"]:
                entity_maps["Divisions"][row["divisionName"]] = f"Divisions_{i}"
    
    # Department lookup by departmentName
    if "Departments" in all_data:
        entity_maps["Departments"] = {}
        for i, row in enumerate(all_data["Departments"], start=1):
            if "departmentName" in row and row["departmentName"]:
                entity_maps["Departments"][row["departmentName"]] = f"Departments_{i}"

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
    
    # Students lookup by studentID
    if "Students" in all_data:
        entity_maps["Students"] = {}
        for i, row in enumerate(all_data["Students"], start=1):
            if "studentID" in row and row["studentID"]:
                entity_maps["Students"][row["studentID"]] = f"Students_{i}"
   
    # Program_Courses lookup by courseCode
    if "Program_Courses" in all_data:
        entity_maps["Program_Courses"] = {}
        for i, row in enumerate(all_data["Program_Courses"], start=1):
            if "courseCode" in row and row["courseCode"]:
                entity_maps["Program_Courses"][row["courseCode"]] = f"Program_Courses_{i}"
    
    # Course_Instances lookup by instanceID
    if "Course_Instances" in all_data:
        entity_maps["Course_Instances"] = {}
        for i, row in enumerate(all_data["Course_Instances"], start=1):
            if "instanceID" in row and row["instanceID"]:
                entity_maps["Course_Instances"][row["instanceID"]] = f"Course_Instances_{i}"

   #--------------------------------------------------------------
 
   # Registrations lookup by (studentID, instanceID)
   # ¤ Note: Weak entity
    if "Registrations" in all_data:
        entity_maps["Registrations"] = {}
        for i, row in enumerate(all_data["Registrations"], start=1):
            s_id = row.get("studentID")
            inst_id = row.get("instanceID")
            # Check that both parts of the identifying relationship exist
            if s_id and inst_id:
                # Create a composite key using a tuple
                composite_key = (s_id, inst_id)
                # Map the composite key to your unique TTL ID
                entity_maps["Registrations"][composite_key] = f"Registrations_{i}"
              
              
    
   # Hours lookup by (teacherID, instanceID)
   # ¤ Note: Weak entity
    if "Hours" in all_data:
        entity_maps["Hours"] = {}
        for i, row in enumerate(all_data["Hours"], start=1):
            t_id = row.get("teacherID")
            inst_id = row.get("instanceID")

            # Check that both parts of the identifying relationship exist
            if t_id and inst_id:
                # Create a composite key using a tuple
                composite_key = (t_id, inst_id)
                # Map the composite key to your unique TTL ID
                entity_maps["Hours"][composite_key] = f"Hours_{i}"
    



   # Courses_Planning lookup by instanceID
   # ¤ Note: Weak entity
    if "Courses_Planning" in all_data:
        entity_maps["Courses_Planning"] = {}
        for i, row in enumerate(all_data["Courses_Planning"], start=1):
            inst_id = row.get("instanceID")

            # Check that both parts of the identifying relationship exist
            if inst_id:
                # Create a composite key using a tuple
                composite_key = (inst_id)
                # Map the composite key to your unique TTL ID
                entity_maps["Courses_Planning"][composite_key] = f"Courses_Planning_{i}"
    




    return entity_maps


def create_dependencies(all_data, entity_maps, output_file):
    # Add All Course Relations
    if "Courses" in all_data:
        for row in all_data["Courses"]:
            course_code = row.get("courseCode")
            department_name = row.get("departmentName")
            division_name = row.get("divisionName")
            program_code = row.get("programCode")
            # Course to Department Relation
            if course_code and department_name:
                course_instance = entity_maps["Courses"].get(course_code)
                department_instance = entity_maps["Departments"].get(department_name)

                if course_instance and department_instance:
                    output_file.write(f"ex:{course_instance} ex:hasDepartment ex:{department_instance} .\n")
            # Course to Division Relation
            if course_code and division_name:
                course_instance = entity_maps["Courses"].get(course_code)
                division_instance = entity_maps["Divisions"].get(division_name)
                
                if course_instance and division_instance:
                 output_file.write(f"ex:{course_instance} ex:hasDivision ex:{division_instance} .\n")
            # Course to Programs Relation (hasOwner Rela)
            if course_code and program_code:
                course_instance = entity_maps["Courses"].get(course_code)
                program_instance = entity_maps["Programs"].get(program_code)
                
                if course_instance and program_instance:
                    output_file.write(f"ex:{course_instance} ex:hasOwner ex:{program_instance} .\n")
            
    # Add All Divisions Relations
    if "Divisions" in all_data:
            for row in all_data["Divisions"]:
                division_name = row.get("divisionName")
                department_name = row.get("departmentName")
                # Division to Department Relation
                if division_name and department_name:
                    division_instance = entity_maps["Divisions"].get(division_name)
                    department_instance = entity_maps["Departments"].get(department_name)

                    if division_instance and department_instance:
                        output_file.write(f"ex:{division_instance} ex:hasDepartment ex:{department_instance} .\n")
    
    # Add All Programs Relations
    if "Programs" in all_data:
        for row in all_data["Programs"]:
            program_code = row.get("programCode")
            department_name = row.get("departmentName")
            teacher_id = row.get("teacherID")
            
            # Program to Department Relation
            if program_code and department_name:
                program_instance = entity_maps["Programs"].get(program_code)
                department_instance = entity_maps["Departments"].get(department_name)

                if program_instance and department_instance:
                    output_file.write(f"ex:{program_instance} ex:hasDepartment ex:{department_instance} .\n")                    
            
            # Program to Senior Teachers Relation (ha)  
            if program_code and teacher_id:
                program_instance = entity_maps["Programs"].get(program_code)
                teacher_instance = entity_maps["Senior_Teachers"].get(teacher_id)

                if program_instance and teacher_instance:
                    output_file.write(f"ex:{program_instance} ex:hasDirector ex:{teacher_instance} .\n")                    

    # Add All Senior Teachers Relations       
    if "Senior_Teachers" in all_data:
        for row in all_data["Senior_Teachers"]:
            teacher_id = row.get("teacherID")
            department_name = row.get("departmentName")
            division_name = row.get("divisionName")

            # Senior Teacher to Department Relation
            if teacher_id and department_name:
                teacher_instance = entity_maps["Senior_Teachers"].get(teacher_id)
                department_instance = entity_maps["Departments"].get(department_name)

                if teacher_instance and department_instance:
                    output_file.write(f"ex:{teacher_instance} ex:hasDepartment ex:{department_instance} .\n")
            
            # Senior Teacher to Division Relation
            if teacher_id and division_name:
                teacher_instance = entity_maps["Senior_Teachers"].get(teacher_id)
                division_instance = entity_maps["Divisions"].get(division_name)

                if teacher_instance and division_instance:
                    output_file.write(f"ex:{teacher_instance} ex:hasDivision ex:{division_instance} .\n")
    
    # Add All Students Relations
    if "Students" in all_data:
        for row in all_data["Students"]:
            student_id = row.get("studentID")
            program_code = row.get("programCode")

            # Student to Program Relation
            if student_id and program_code:
                student_instance = entity_maps["Students"].get(student_id)
                program_instance = entity_maps["Programs"].get(program_code)

                if student_instance and program_instance:
                    output_file.write(f"ex:{student_instance} ex:hasProgram ex:{program_instance} .\n")
    
    # Add All Program Courses Relations
    if "Program_Courses" in all_data:
        for row in all_data["Program_Courses"]:
            course_code = row.get("courseCode")
            program_code = row.get("programCode")

            # Program Courses to Program Relation
            if course_code and program_code:
                program_course_instance = entity_maps["Program_Courses"].get(course_code)
                program_instance = entity_maps["Programs"].get(program_code)

                if program_course_instance and program_instance:
                    output_file.write(f"ex:{program_course_instance} ex:hasProgram ex:{program_instance} .\n")
    
    # Add All Courses Planning Relations
    if "Courses_Planning" in all_data:
        for row in all_data["Courses_Planning"]:
            instance_id = row.get("instanceID")

            # Courses Planning to Course Relation
            if instance_id:
                courses_planning_instance = entity_maps["Courses_Planning"].get(instance_id)
                course_instance_instance = entity_maps["Course_Instances"].get(instance_id)

                if courses_planning_instance == course_instance_instance:
                    output_file.write(f"ex:{courses_planning_instance} ex:hasCourseInstances ex:{course_instance_instance} .\n")
    
    # Add All Registrations Relations
    if "Registrations" in all_data:
        for row in all_data["Registrations"]:
            student_id = row.get("studentID")
            instance_id = row.get("instanceID")

            # Registrations to Students Relations
            if student_id and instance_id:
                registration_instance = entity_maps["Registrations"].get((student_id, instance_id))
                student_instance = entity_maps["Students"].get(student_id)

                if registration_instance and student_instance:
                    output_file.write(f"ex:{registration_instance} ex:hasStudent ex:{student_instance} .\n")
            
            # Registration to Course Instance Relation
            if student_id and instance_id:
                registration_instance = entity_maps["Registrations"].get((student_id, instance_id))
                course_instance_instance = entity_maps["Course_Instances"].get(instance_id)

                if registration_instance and course_instance_instance:
                    output_file.write(f"ex:{registration_instance} ex:hasCourseInstances ex:{course_instance_instance} .\n")
        
    # Add All Course Instances Relations    
    if "Course_Instances" in all_data:
        for row in all_data["Course_Instances"]:
            instance_id = row.get("instanceID")
            course_code = row.get("courseCode")
            teacher_id = row.get("teacherID")

            # Course Instance to Courses Planning Relation
            if instance_id:
                course_instance_instance = entity_maps["Course_Instances"].get(instance_id)
                courses_planning_instance = entity_maps["Courses_Planning"].get(instance_id)

                if course_instance_instance and courses_planning_instance:
                    output_file.write(f"ex:{course_instance_instance} ex:hasCoursesPlanning ex:{courses_planning_instance} .\n")
            
            # Course Instances to Course Relation
            # ¤ Course Instances has no course code attribute, so we pick it from Hours instead
            if instance_id and course_code:
                course_instance_instance = entity_maps["Course_Instances"].get(instance_id)
                course_instance = entity_maps["Courses"].get(course_code)

                if course_instance_instance and course_instance:
                    output_file.write(f"ex:{course_instance_instance} ex:hasCourse ex:{course_instance} .\n")
                    
            # Course Instances to Senior Teacher Relation
            if instance_id and teacher_id:
                course_instance_instance = entity_maps["Course_Instances"].get(instance_id)
                teacher_instance = entity_maps["Senior_Teachers"].get(teacher_id)

                if course_instance_instance and teacher_instance:
                    output_file.write(f"ex:{course_instance_instance} ex:hasExaminer ex:{teacher_instance} .\n")
    
    # Add All Hours Relations
    if "Hours" in all_data:
        for row in all_data["Hours"]:
            teacher_id = row.get("teacherID")
            instance_id = row.get("instanceID")

            # Hours to Teachers Relations (including TA's)
            if teacher_id and instance_id:
                hours_instance = entity_maps["Hours"].get((teacher_id, instance_id))
                teacher_instance = entity_maps["Senior_Teachers"].get(teacher_id)
                ta_instance = entity_maps["Teaching_Assistants"].get(teacher_id)

                if hours_instance and teacher_instance:
                    output_file.write(f"ex:{hours_instance} ex:hasTeachers ex:{teacher_instance} .\n")
                if hours_instance and ta_instance:
                    output_file.write(f"ex:{hours_instance} ex:hasTeachers ex:{ta_instance} .\n")

            # Hours to Course Instance Relation
            if teacher_id and instance_id:
                hours_instance = entity_maps["Hours"].get((teacher_id, instance_id))
                course_instance_instance = entity_maps["Course_Instances"].get(instance_id)

                if hours_instance and course_instance_instance:
                    output_file.write(f"ex:{hours_instance} ex:hasCourseInstances ex:{course_instance_instance} .\n")

def main():
    
    # Create & Modify CSV Files
    create_course_instances()
    create_hours()
    create_divisions()
    create_departments()

    # Create TTL Output File
    f = open("ttl/output.ttl", "w")

    # Open TTL Model File & Copy Content to Output
    model = open("ttl/model.ttl")
    f.write(model.read())
    model.close()

    # Add New Prefixes to Output File
    f.write("@prefix ex: <http://www.semanticweb.org/DAT475-Group1/ontologies/2026/3/untitled-ontology-12/> .\n")
    f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n")
    
    # List File Names
    files = [
    "Course_Instances",
    "Courses_Planning",
    "Courses",
    "Departments",
    "Divisions",
    "Hours",
    "Program_Courses",
    "Programs",
    "Registrations",
    "Senior_Teachers",
    "Students",
    "Teaching_Assistants"
    ]

    # Load All Data
    all_data = {}
    for file in files:
        file_path = f"csv/{file}.csv"
        all_data[file] = get_data_from_csv(file_path)

    # Add All Entities
    for file in files:
        data = all_data[file]
        convert_dictionary_to_rdf(file, data, f)


    # Add All Relations    
    entity_maps = create_entity_maps(all_data)
    create_dependencies(all_data, entity_maps, f)

    f.close()
    

if __name__ == "__main__":  
    main()
    
    




    