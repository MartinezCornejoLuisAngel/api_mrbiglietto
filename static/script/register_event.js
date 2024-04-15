const theaterCampo = document.getElementById("theaters");
const objetoTheaterString = theaterCampo.value;
const jsonStringConComillasDobles = objetoTheaterString.replace(/'/g, '"');
const jsonStringConNull = jsonStringConComillasDobles.replace(/None/g, "null");
const jsonStringConFalseModificado = jsonStringConNull.replace(
  /False/g,
  "false"
);
try {
  var objetoTheater = JSON.parse(jsonStringConFalseModificado);
  // Resto del código para trabajar con objetoTheater
} catch (error) {
  console.error("Error al analizar el JSON:", error);
}
if (objetoTheater) {
  const sections = objetoTheater["sections"];
  const sectionCardsContainer = document.getElementById(
    "sectionCardsContainer"
  );

  // Limpiar el contenedor antes de agregar nuevas tarjetas
  sectionCardsContainer.innerHTML = "";

  // Iterar sobre las secciones y crear tarjetas para cada una
  sections.forEach((section) => {
    const sectionCard = document.createElement("div");
    sectionCard.classList.add("section-card");
    sectionCard.innerHTML = `
              <h3>${section.sectionName}</h3>
              <p>ID de Sección: ${section.idSection}</p>
              <p>Asientos Disponibles: ${section.availableSeats}</p>
              <label for="precio">Precio de la Sección:</label>
              <input type="number" id="precio${section.idSection}" name="precio${section.idSection}" placeholder="Ingrese el precio" required>
          
          `;
    sectionCardsContainer.appendChild(sectionCard);
  });
} else {
  console.log("El objeto del campo theater es nulo o indefinido.");
}

theaterCampo.addEventListener("change", function (event) {
  // Obtener el objeto del campo theater
  const objetoTheaterString = event.target.value;
  const jsonStringConComillasDobles = objetoTheaterString.replace(/'/g, '"');
  const jsonStringConNull = jsonStringConComillasDobles.replace(
    /None/g,
    "null"
  );
  const jsonStringConFalseModificado = jsonStringConNull.replace(
    /False/g,
    "false"
  );

  try {
    var objetoTheater = JSON.parse(jsonStringConFalseModificado);
    // Resto del código para trabajar con objetoTheater
  } catch (error) {
    console.error("Error al analizar el JSON:", error);
  }
  if (objetoTheater) {
    const sections = objetoTheater["sections"];
    const sectionCardsContainer = document.getElementById(
      "sectionCardsContainer"
    );

    // Limpiar el contenedor antes de agregar nuevas tarjetas
    sectionCardsContainer.innerHTML = "";

    // Iterar sobre las secciones y crear tarjetas para cada una
    sections.forEach((section) => {
      const sectionCard = document.createElement("div");
      sectionCard.classList.add("section-card");
      sectionCard.innerHTML = `
                <h3>${section.sectionName}</h3>
                <p>ID de Sección: ${section.idSection}</p>
                <p>Asientos Disponibles: ${section.availableSeats}</p>
                <label for="precio">Precio de la Sección:</label>
                <input type="number" id="precio${section.idSection}" name="precio${section.idSection}" placeholder="Ingrese el precio" required>
            
            `;
      sectionCardsContainer.appendChild(sectionCard);
    });
  } else {
    console.log("El objeto del campo theater es nulo o indefinido.");
  }
});

// Manejar el envío del formulario
$(document).ready(function () {
  $("#sectionForm").on("submit", function (event) {
    event.preventDefault(); // Evitar el envío del formulario de forma predeterminada

    // Serializar los datos del formulario
    var formData = $(this).serialize();

    // Enviar los datos al servidor usando AJAX
    $.ajax({
      type: "POST",
      url: "/home",
      data: formData,
      success: function (response) {
        if (response.status_code == 200) {
          console.log("Teatro registrado correctamente");
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
