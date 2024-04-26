src = "https://code.jquery.com/jquery-3.6.0.min.js";
let sectionCounter = 1;
document.addEventListener("DOMContentLoaded", function () {
  fetch("/firebase-config")
    .then((response) => response.json())
    .then((data) => {
      // Utiliza la configuración de Firebase recibida
      initializeFirebase(data);
    })
    .catch((error) => {
      console.error("Error al obtener la configuración de Firebase:", error);
    });
});

document.getElementById('theaterImage').addEventListener('change', function() {
  const fileInput = document.getElementById('theaterImage');
  const filePath = fileInput.value;
  // Lista de extensiones permitidas
  const allowedExtensions = /(\.jpg|\.jpeg|\.png|\.gif)$/i;
  // Verificar si la extensión del archivo seleccionado es permitida
  if (!allowedExtensions.exec(filePath)) {
      alert('Por favor, selecciona un archivo de imagen válido (JPEG, PNG, GIF).');
      fileInput.value = '';
      return false;
  }
});

function initializeFirebase(config) {
  // Inicializa Firebase con la configuración proporcionada
  firebase.initializeApp(config);
  // Aquí puedes seguir con la inicialización de Firebase
}

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
$(document).ready(function () {
  $("#sectionForm").on("submit", function (event) {
    event.preventDefault(); // Evitar el envío del formulario de forma predeterminada

    // Serializar los datos del formulario
    var formData = $(this).serialize();

    // Enviar los datos al servidor usando AJAX
    $.ajax({
      type: "POST",
      url: "/register_theater",
      data: formData,
      success: function (response) {
        if (response.status_code == 200) {
          alert("Teatro registrado correctamente");
          window.location.href = "/register_location"; // Redirigir al usuario
        } else if (response.status_code == 409) {
          alert("Error con el id");
        }
      },
      error: function (xhr, status, error) {
        console.error("Error al enviar los datos de las secciones:", error);
      },
    });
  });
});


function uploadImage() {
  const file = document.getElementById("theaterImage").files[0];
  const storageRef = firebase.storage().ref();
  const imageRef = storageRef.child("theater_images/" + file.name);

  // Mostrar el loader
  document.getElementById("loader_t").style.display = "block";

  if (file == null) {
    alert("Selecciona una imagen");
    // Ocultar el loader
    document.getElementById("loader_t").style.display = "none";
  } else {
    imageRef
      .put(file)
      .then((snapshot) => {
        console.log("Imagen cargada exitosamente");
        // Obtener la URL de la imagen cargada
        imageRef
          .getDownloadURL()
          .then((url) => {
            // Colocar la URL en el campo de entrada de URL
            document.getElementById("theaterUrl").value = url;
            // Ocultar el loader
            document.getElementById("loader_t").style.display = "none";
          })
          .catch((error) => {
            console.error("Error al obtener la URL de la imagen:", error);
            // Ocultar el loader
            document.getElementById("loader_t").style.display = "none";
          });
      })
      .catch((error) => {
        console.error("Error al cargar la imagen:", error);
        // Ocultar el loader
        document.getElementById("loader_t").style.display = "none";
      });
  }
}
