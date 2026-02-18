document.querySelector("form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the form from reloading the page 


    // Get the form element and form data
    const form = event.target; // Get the form element that triggered the event
    const formData = new FormData(form); // Create a FormData object from the form


    try {
        const response = await fetch(form.action, {
            method: "POST",
            body: formData,
        });
        const result = await response.json(); // Parse the JSON response

        if (response.status === 200) {
            // Save the JWT token to localStorage
            if (result.access_token) {
                localStorage.setItem("access_token", result.access_token);
                // alert(result.message); // Optional: show success message
                window.location.href = "/"; // Redirect to the home page
            } else {
                alert("Login successful but no token received!");
            }
        } else {
            alert(`Error: ${result.message}`); // Show error message
        }

    } catch (error) {
        console.error("Error:", error);
        alert("An unexpected error occurred. Please check your connection and try again.");
    }


})