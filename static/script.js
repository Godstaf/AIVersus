document.querySelector("form").addEventListener("submit", async function (event) {
  console.log('Form submitted'); // Log form submission for debugging
  event.preventDefault(); // Prevent the form from reloading the page

  const formData = new FormData(this); // Get form data
  const queryUrl = this.getAttribute("data-query-url"); // Get the query URL from the form attribute
  try {
    let response = await fetch(queryUrl, {
      method: "POST",
      body: formData,
    });
    response = await response.json(); // Get the response text

    console.log('Response:', response.response); // Log the response for debugging
    // alert(x.response)
    let divCount = 0
    // Display the response between <nav> and <form>
    const responseContainer = document.getElementById("response-container"+divCount); // Check if the div already exists
    if (!responseContainer) {
      divCount+=1
      // Create a new div if it doesn't exist
      const newDiv = document.createElement("div");
      newDiv.id = "response-container"+divCount; // Unique ID for the new div
      newDiv.className = "response-container";
      newDiv.innerText = response.response; // Set the response text
      document.querySelector("nav").insertAdjacentElement("afterend", newDiv);
    } else {
      // Update the existing div
      responseContainer.innerText = response.response;
    }

  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  }
});