// Fonction pour afficher le message de succès
function showSuccessMessage() {
    var successMessage = document.getElementById("successMessage");
    successMessage.style.display = "block";

    // Ajoutez un délai pour masquer le message après quelques secondes (facultatif)
    setTimeout(function() {
        successMessage.style.display = "none";
    }, 5000); // Le message disparaîtra après 5 secondes (ajustez la valeur selon vos préférences)
}