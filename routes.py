from flask import Flask, request, jsonify,Response
from neo4j import GraphDatabase
from flask_cors import CORS
from flask import send_file, send_from_directory, render_template, redirect, url_for
import os
import csv
import pandas as pd
from io import StringIO
from neo4j.exceptions import ClientError
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from dotenv import load_dotenv
from werkzeug.utils import url_quote
from add_data import add_data_to_database

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Utiliser les variables d'environnement dans votre application
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# connection à la base de données Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


app = Flask(__name__)
CORS(app)  # Activez CORS pour toutes les routes



# Enregistrez la fonction pour qu'elle soit exécutée avant la première requête
@app.before_first_request
def before_first_request():
    add_data_to_database(driver)


@app.route('/')
def index():
    #return render_template('page.html')
    return redirect(url_for('get_employees'))

@app.route('/add_employee_form')
def add_employee_form():
    return render_template('add_employee_form.html')

@app.route('/add_department_form')
def add_departement_form():
    return render_template('add_department_form.html')

@app.route('/update_employee_form')
def update_employee_form():
    return render_template('update_employee_form.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# ************************************************GET EMPLOYEES ***********************************************************
@app.route('/get_employees')
def get_employees():
    print("La route get_employees est atteinte !")
    try:
        # Exécution de  la requête Neo4j pour récupérer tous les employés
        query = """
            MATCH (e:EMPLOYEE)-[:WORKS_IN]->(d:DEPARTMENT)
            RETURN ID(e) AS employee_id, e.name AS name, d.name AS department, e.role AS role, e.manager AS manager, e.salary AS salary
        """

        result = driver.execute_query(query)
        employees= result.records
        print("Liste des employés:", employees)

        # Renvoyer la liste des employés au modèle
        return render_template('get_employees.html', employees=employees)

    except Exception as e:
        print(f"Erreur lors de la récupération des employés : {str(e)}")
        return render_template('error.html', error=str(e))

# ***********************************************ADD Employee*****************************************************************
@app.route('/add_employee', methods=['POST'])
def api_add_employee():
    try:
        # Récupérer les données à partir du formulaire
        employee_name = request.form.get('EmployeeName')
        employee_dept = request.form.get('EmployeeDept')
        role = request.form.get('EmployeeRole')
        manager = request.form.get('EmployeeManager')
        salary = request.form.get('EmployeeSalary')

        #  tous les champs nécessaires sont présents!!
        if employee_name and employee_dept and role and manager and salary:
            # Exécution de la requête Neo4j pour ajouter l'employée
            result = driver.execute_query(
                """
                MERGE (e:EMPLOYEE {name: $name, Dept: $deptName, role: $role, manager: $manager, salary: $salary})
                MERGE (d:DEPARTMENT {name: $deptName})
                MERGE (e)-[:WORKS_IN]->(d)
                """,
                name=employee_name, role=role, manager=manager, salary=salary, deptName=employee_dept
            )

            # Stockage de résultat dans une variable employee_node
            employee_node = result.records
            # Vérification si le résultat est non nul
            if employee_node is not None:
                # Retourner une réponse réussie
                response_data = {
                    "employeeData": {
                        "EmployeeName": employee_name,
                        "EmployeeDept": employee_dept,
                        "Role": role,
                        "Manager": manager,
                        "Salary": salary
                    },
                    "message": "Employee ajoutée avec succès !!",
                    "success": True
                }
                message=response_data['message']
                success=response_data['success']
               # Rediriger vers la page add_employee_form avec les paramètres d'URL
                return render_template('add_employee_form.html', message=message, success=success)

            else:
                # Si aucun nœud n'a été retourné, cela signifie que l'ajout a échoué
                return jsonify({"error": "L'ajout de l'employé a échoué"}), 500
        else:
            return jsonify({"error": "Les champs nécessaires sont manquants"}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ***********************************************ADD Department*****************************************************************
@app.route('/add_department', methods=['POST'])
def api_add_department():
    print("ADD DEPARTMENT")
    try:
        # Récupérer les données a partir du formulaire
        department = request.form.get('DepartmentName')
        description =request.form.get('DepartmentDescription')

        if department:
            # Exécution de  la requête Neo4j pour vérifier si le département existe!
            check_result = driver.execute_query(
                """
                MATCH (d:DEPARTMENT {name: $name})
                RETURN COUNT(d) AS departmentCount
                """,
                name=department
            )
            
            # Récupérer le nombre de départements avec ce nom
            print("check_result",check_result)
            result = check_result.records
            department_count = result[0]["departmentCount"]

            print("department_count :",department_count)
            if department_count == 0:
                add_result = driver.execute_query(
                    """
                    CREATE (d:DEPARTMENT {name: $name, description: $description})

                    """,
                    name=department,description=description
                )

                # Retourner une réponse réussie
                response_data = {
                    "DepartmentData": {
                        "Dept": department,
                        "Description":description
                    },
                    "message": "Departement ajouté avec succès !!",
                    "success": True
                }

                message = response_data['message']
                success = response_data['success']
                # Rediriger vers la page add_department_form avec les paramètres d'URL
                #return render_template('add_department_form.html', message=message, success=success)
                return redirect(url_for('get_departments', message="Departement ajouté avec succès !!"))
                #return redirect(url_for('get_departments'))
            else:

                # Retourner une réponse réussie
                response_data = {
                    "DepartmentData": {
                        "Dept": department,
                    },
                    "message": "Departement existe dans la base de données  !!",
                    "success": True
                }

                message = response_data['message']
                success = response_data['success']
                # Rediriger vers la page add_department_form avec les paramètres d'URL
                #return render_template('add_department_form.html', message=message, success=success)
                return redirect(url_for('get_departments', message=message))
                
        else:
            return jsonify({"error": "Les champs nécessaires sont manquants"}), 422
    except ClientError as ce:
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#********************************************************** Get Departments ************************************************************
@app.route('/get_departments')
def get_departments():
    print("La route get_departemet est atteinte !")
    try:
        # Exécution de  la requête Neo4j pour récupérer tous les employés
        query = """
            MATCH (d:DEPARTMENT)
            RETURN ID(d) AS department_id,d.name AS departmentName, d.description AS departmentDescription

        """
        result = driver.execute_query(query)
        departments= result.records
        print("departments list:", departments)

        # Renvoyer la liste des employés au modèle
        return render_template('add_department_form.html', departments=departments)

    except Exception as e:
        print(f"Erreur lors de la récupération des departements : {str(e)}")
        return render_template('error.html', error=str(e))

# ******************************************SEARCH**************************************************************

@app.route('/search_employee', methods=['POST'])
def search_employee():
    employee_name = request.form.get('employee_name', '')
    try:
       # Exécution de  la requête Cypher pour rechercher l'employée par nom
        result = driver.execute_query("""
            MATCH (e:EMPLOYEE)-[:WORKS_IN]->(d:DEPARTMENT)
            WHERE toLower(e.name) CONTAINS toLower($name)
            RETURN  ID(e) AS employee_id,e.name AS name, d.name AS department, e.role AS role, e.manager AS manager, e.salary AS salary
        """, name=employee_name)

        search_results = result.records

        print("Employés trouvés :", search_results)
        return render_template('get_employees.html', search_results=search_results) 
    
    except Exception as e:
        print("Erreur lors de la recherche d'employés :", str(e))
        return render_template('error.html', error=str(e))
    

# Route Flask pour la recherche par département
@app.route('/search_departement', methods=['POST'])
def search_departement():
    departement_name = request.form.get('departement_name', '')
    try:
        # Exécution de la requête Cypher pour la recherche des employés par département
        result = driver.execute_query("""
            MATCH (e:EMPLOYEE)-[:WORKS_IN]->(d:DEPARTMENT)
            WHERE toLower(d.name) CONTAINS toLower($name)
            RETURN e.name AS name, d.name AS department, e.role AS role, e.manager AS manager, e.salary AS salary
            
        """, name=departement_name)

        search_results = result.records
      
        print("Employés trouvés :", search_results)
        return render_template('get_employees.html', search_results=search_results) 
    except Exception as e:
        print("Erreur lors de la recherche d'employés par département :", str(e))
        return render_template('error.html', error=str(e))

# ************************EXPORTER LES EMPLOYÉES EN CSV ***********************************************
@app.route('/export_employees_csv')
def export_employees_csv():
    try:
        # Exécution de la requête Neo4j pour récupérer tous les employés
        result = driver.execute_query(
            """
            MATCH (e:EMPLOYEE)-[:WORKS_IN]->(d:DEPARTMENT)
            RETURN e.name AS name, d.name AS department, e.role AS role, e.manager AS manager, e.salary AS salary
            """
        )

        # Convertir les données en format CSV
        csv_content = "EmployeeName,EmployeeDept,EmployeeRole,EmployeeManager,EmployeeSalary\n"
        for record in result.records:
            csv_content += f"{record['name']},{record['department']},{record['role']},{record['manager']},{record['salary']}\n"

        # Création d'une réponse avec le contenu CSV
        response = Response(csv_content, content_type='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=employees_data.csv'

        return response
    
    except Exception as e:
        print(f"Erreur lors de l'export CSV des employés : {str(e)}")
        return render_template('error.html', error=str(e))


# **************************************************UPLOAD CSV************************************************************
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:

        uploaded_file = request.files['csv_file']  
        # Check if the file is uploaded
        if uploaded_file:
            # Read the contents of the file
            csv_content = uploaded_file.read().decode('utf-8')

            # Convert CSV content to a pandas DataFrame
            df = pd.read_csv(StringIO(csv_content))  # Use StringIO from io module
            
            # Connect to Neo4j and run queries to add data
            for _, row in df.iterrows():
                driver.execute_query("""
                    CREATE (e:EMPLOYEE {name: $name, Dept: $deptName, role: $role, manager: $manager, salary: $salary})
                    MERGE (e)-[:WORKS_IN]->(d:DEPARTMENT {name: $deptName})
                """, name=row['EmployeeName'], deptName=row['EmployeeDept'], role=row['EmployeeRole'], manager=row['EmployeeManager'], salary=row['EmployeeSalary'])

            # Redirect to get_employees with a success message
            return redirect(url_for('get_employees', message="Data imported successfully."))

        else:
            return "No file uploaded.", 400

    except Exception as e:
        return f"Error uploading CSV and adding data to Neo4j: {str(e)}", 500
    

# ************************************DELETE EMPLOYEE***************************************************************************
    
@app.route('/delete_employee', methods=['POST'])
def delete_employee():
    try:
        employee_id = request.form.get('employee_id', '')
        print("Empoyee_id",employee_id)
        
        # Connect to Neo4j and run queries to delete employee
        driver.execute_query("MATCH (e:EMPLOYEE) WHERE ID(e) = toInteger($employee_id) DETACH DELETE e", employee_id=employee_id)
       

        # After deletion, redirect to the page showing the updated table
        return redirect(url_for('get_employees'))
    except Exception as e:
        return render_template('error.html', error=str(e))
    
    
# ************************************DELETE DEPARTMENT***************************************************************************
    
@app.route('/delete_department', methods=['POST'])
def delete_department():
    try:
        department_name = request.form.get('department_name', '')
        
        # Add code to delete the employee from the database
        driver.execute_query("MATCH (d:DEPARTMENT {name: $name}) DETACH DELETE d", name=department_name)

        # After deletion, you may want to redirect to the page showing the updated table
        return redirect(url_for('get_departments'))
    except Exception as e:
        return render_template('error.html', error=str(e))
    
# **************************************UPDATE EMPLOYEE***************************************************************************
@app.route('/update_employee_form2', methods=['GET'])
def update_employee_form2():
    employee_id = request.args.get('employee_id')
    employee_name = request.args.get('employee_name')
    department = request.args.get('department')
    role = request.args.get('role')
    manager = request.args.get('manager')
    salary = request.args.get('salary')

    return render_template('update_employee_form.html', employee_id=employee_id, employee_name=employee_name, department=department, role=role, manager=manager, salary=salary)
    

@app.route('/update_employee', methods=['POST'])
def update_employee():
    try:     
        
        employee_id = int(request.form.get('employee_id'))
        name = request.form.get('employee_name')
        department = request.form.get('department')
        role = request.form.get('role')
        manager = request.form.get('manager')
        salary = request.form.get('salary')
        print("Employee ID dans update_employee :", employee_id,name,department,role,manager,salary)

        # Connect to Neo4j and run queries to update employee

        result = driver.execute_query(
            """
            MATCH (e:EMPLOYEE)
            WHERE ID(e) = $employee_id
            SET e.name = $employee_name,
                e.Dept = $department,
                e.role = $role,
                e.manager = $manager,
                e.salary = $salary
            RETURN e
            """,
            employee_id=employee_id , employee_name=name, department=department,
            role=role, manager=manager, salary=salary
        )

        print("Neo4j Result:", result.records)

        # Check if the result contains any records
        if result and result.records:
            # Redirect to the main employees' table page after the update
            message = "Employee updated"
            success = "True"
            return render_template('update_employee_form.html', message=message, success=success)
        else:
            # Handle the case where the employee is not found or the update didn't happen
            message = "Employee not found or update failed"
            success = "False"
            return render_template('update_employee_form.html', message=message, success=success)


    except Exception as e:
        return f"Error updating employee details: {str(e)}", 500


# **************************************Visualisation********************************************************
@app.route('/visualisation')
def visualisation():
    # Initialisez des listes vides pour stocker les données
    departments = []
    employee_counts = []
    average_salaries = []

    # Exécutez une requête Cypher pour récupérer les données
    result = driver.execute_query("""MATCH (d:DEPARTMENT)<-[:WORKS_IN]-(e:EMPLOYEE) 
        RETURN d.name AS department, COUNT(e) AS employee_count, AVG(toInteger(e.salary)) AS average_salary""")

    # Parcourez les résultats et remplissez les listes
    for record in result.records:
        departments.append(record['department'])
        employee_counts.append(record['employee_count'])
        average_salaries.append(record['average_salary'])

    # Créez un premier diagramme à barres pour le nombre d'employés
    plt.bar(departments, employee_counts, color='#4AD489')
    plt.xlabel('Departments')
    plt.ylabel('Number of employees')
    plt.title('Number of employees per department')

    # Sauvegardez le premier graphique dans un fichier
    plot_file_path = os.path.join('static', 'plot1.png')
    plt.savefig(plot_file_path)
    plt.close()

   
    # Créez un deuxième diagramme à barres pour la moyenne des salaires
    plt.bar(departments, average_salaries, color='orange')
    plt.xlabel('Departments')
    plt.ylabel('Average Salary')
    plt.title('Average Salary per department')

    # Sauvegardez le deuxième graphique dans un fichier
    plot_file_path_2 = os.path.join('static', 'plot2.png')
    plt.savefig(plot_file_path_2)
    plt.close()

    # Renvoyez le modèle HTML avec les deux images intégrées
    return render_template('visualisation.html', plot_url_1='/static/plot1.png', plot_url_2='/static/plot2.png')




 