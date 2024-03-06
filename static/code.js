// Fonction pour afficher le message de succès
function showSuccessMessage() {
    var successMessage = document.getElementById("successMessage");
    successMessage.style.display = "block";

    // Ajoutez un délai pour masquer le message après quelques secondes (facultatif)
    setTimeout(function() {
        successMessage.style.display = "none";
    }, 5000); // Le message disparaîtra après 5 secondes (ajustez la valeur selon vos préférences)
}


 function updateEmployee(employeeId, employeeName, department, role, manager, salary) {
        document.getElementById('employee_id');
        document.getElementById('employee_name').value = employeeName;
        document.getElementById('department').value = department;
        document.getElementById('role').value = role;
        document.getElementById('manager').value = manager;
        document.getElementById('salary').value = salary;
    }

