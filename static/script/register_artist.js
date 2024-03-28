function validateForm() {
  var eventName = document.getElementById("artistName").value.trim();
  var eventDescription = document
    .getElementById("artistDescription")
    .value.trim();
  var eventGenre = document.getElementById("artistGenre").value.trim();
  var eventUrl = document.getElementById("artistUrl").value.trim();
  var eventTourName = document.getElementById("artistTourName").value.trim();

  if (
    eventName === "" ||
    eventDescription === "" ||
    eventGenre === "" ||
    eventUrl === "" ||
    eventTourName === ""
  ) {
    alert("Por favor, llene todos los campos.");
    return false;
  }

  // Si pasa todas las validaciones, puedes enviar el formulario aquí
  document.getElementById("eventForm").submit();
}

// register_theater.js

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

function initializeFirebase(config) {
  // Inicializa Firebase con la configuración proporcionada
  firebase.initializeApp(config);
  // Aquí puedes seguir con la inicialización de Firebase
}

function uploadImage() {
  const file = document.getElementById("artistImage").files[0];
  const storageRef = firebase.storage().ref();
  const imageRef = storageRef.child("artist_images/" + file.name);

  // Mostrar el loader
  document.getElementById("loader").style.display = "block";

  if (file == null) {
    alert("Selecciona una imagen");
    // Ocultar el loader
    document.getElementById("loader").style.display = "none";
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
            document.getElementById("artistUrl").value = url;
            // Ocultar el loader
            document.getElementById("loader").style.display = "none";
          })
          .catch((error) => {
            console.error("Error al obtener la URL de la imagen:", error);
            // Ocultar el loader
            document.getElementById("loader").style.display = "none";
          });
      })
      .catch((error) => {
        console.error("Error al cargar la imagen:", error);
        // Ocultar el loader
        document.getElementById("loader").style.display = "none";
      });
  }
}
