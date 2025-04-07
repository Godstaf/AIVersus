
document.querySelector("form").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent the default form submission behavior

    // Get the form element and form data
    const form = event.target;
    const formData = new FormData(form);

    try {
        // Send the form data to the server
        const response = await fetch(form.action, {
            method: "POST",
            body: formData,
        });

        // Parse the JSON response
        const result = await response.json();

        if (response.status === 200) {
            alert(result.message); // Show success message
            window.location.href = "/login"; // Redirect to the login page
        } else {
            alert(`Error: ${result.message}`); // Show error message
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An unexpected error occurred. Please check your connection and try again.");
    }
});