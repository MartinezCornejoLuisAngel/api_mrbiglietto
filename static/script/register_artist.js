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

const firebaseConfig = JSON.parse(document.currentScript.getAttribute('data-firebase-config'));
// Utiliza firebaseConfig aquí
firebase.initializeApp(firebaseConfig);


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

