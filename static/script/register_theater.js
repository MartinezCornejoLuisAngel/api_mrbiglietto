src="https://code.jquery.com/jquery-3.6.0.min.js"

let sectionCounter = 1;

function addSectionFields() {
  var sectionFieldsContainer = document.getElementById("sectionFields");

  var sectionContainer = document.createElement("div");
  sectionContainer.classList.add("section-container");

  var sectionNameLabel = document.createElement("label");
  sectionNameLabel.innerHTML = "Sección " + sectionCounter + " - Nombre:";
  var sectionNameInput = document.createElement("input");
  sectionNameInput.type = "text";
  sectionNameInput.name = "section_name_" + sectionCounter; // Nombre único para el campo de nombre
  sectionNameInput.placeholder = "Nombre de la Sección";
  sectionNameInput.classList.add("form-control");
  sectionNameInput.required = true;

  var numColumnsLabel = document.createElement("label");
  numColumnsLabel.innerHTML = "Número de Columnas:";
  var numColumnsInput = document.createElement("input");
  numColumnsInput.type = "number";
  numColumnsInput.name = "num_columns_" + sectionCounter; // Nombre único para el campo de número de columnas
  numColumnsInput.placeholder = "Número de Columnas";
  numColumnsInput.classList.add("form-control");
  numColumnsInput.required = true;

  var numRowsLabel = document.createElement("label");
  numRowsLabel.innerHTML = "Número de Filas:";
  var numRowsInput = document.createElement("input");
  numRowsInput.type = "number";
  numRowsInput.name = "num_rows_" + sectionCounter; // Nombre único para el campo de número de columnas
  numRowsInput.placeholder = "Número de Filas";
  numRowsInput.classList.add("form-control");
  numRowsInput.required = true;

  var seatsAvailableLabel = document.createElement("label");
  seatsAvailableLabel.innerHTML = "Asientos Disponibles:";
  var seatsAvailableInput = document.createElement("input");
  seatsAvailableInput.type = "number";
  seatsAvailableInput.name = "seats_ave_" + sectionCounter; // Nombre único para el campo de número de columnas
  seatsAvailableInput.placeholder = "Asientos Disponibles";
  seatsAvailableInput.classList.add("form-control");
  seatsAvailableInput.required = true;

  sectionContainer.appendChild(sectionNameLabel);
  sectionContainer.appendChild(sectionNameInput);
  sectionContainer.appendChild(numColumnsLabel);
  sectionContainer.appendChild(numColumnsInput);
  sectionContainer.appendChild(numRowsLabel);
  sectionContainer.appendChild(numRowsInput);
  sectionContainer.appendChild(seatsAvailableLabel);
  sectionContainer.appendChild(seatsAvailableInput);

  sectionFieldsContainer.appendChild(sectionContainer);

  sectionCounter++;
}

// Manejar el envío del formulario
$(document).ready(function() {
    $('#sectionForm').on('submit', function(event) {
        event.preventDefault(); // Evitar el envío del formulario de forma predeterminada

        // Serializar los datos del formulario
        var formData = $(this).serialize();

        // Enviar los datos al servidor usando AJAX
        $.ajax({
            type: 'POST',
            url: '/register_theater',
            data: formData,
            success: function(response) {
                if (response.status_code == 200) {
                    alert("Teatro registrado correctamente");
                    window.location.href = '/register_location'; // Redirigir al usuario
                } else if (response.status_code == 409) {
                    alert("Error con el id");
                }
            },
            error: function(xhr, status, error) {
                console.error("Error al enviar los datos de las secciones:", error);
            }
        });
    });
});