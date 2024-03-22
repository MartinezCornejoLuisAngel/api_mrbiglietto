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
