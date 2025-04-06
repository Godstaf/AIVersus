

document.querySelector("form").addEventListener("submit", async function (event) {
  // console.log('Form submitted'); // Log form submission for debugging
  event.preventDefault(); // Prevent the form from reloading the page

  // Add the query in .convo div
  const convoDiv = document.querySelector(".convo");
  const newDiv = document.createElement("div");
  newDiv.className = "query-container"; // Add a class to the new div
  newDiv.innerText = document.getElementById("qry").value; // Set the query text
  console.log(document.getElementById("qry").value)
  convoDiv.appendChild(newDiv); // Append the new div to .convo
  

  const formData = new FormData(this); // Get form data
  const queryUrl = this.getAttribute("data-query-url"); // Get the query URL from the form attribute
  document.getElementById("qry").value = ""; // Clear the input field
    // Add the response to the .convo div
  try {
    let response = await fetch(queryUrl, {
      method: "POST",
      body: formData,
    });
    response = await response.json(); // Get the response text

    console.log('Response:', response.response); // Log the response for debugging
    // alert(x.response) 
    
    const convoDiv = document.querySelector(".convo");
    const newDiv = document.createElement("div");
    newDiv.className = "response-container";
    newDiv.innerText = response.response; // Set the response text
    convoDiv.appendChild(newDiv); // Append the new div to .convo


  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  }
});



// Add event listener for the Enter key on the text box
document.getElementById("qry").addEventListener("keydown", function (event) {
  if (event.key === "Enter" && !event.shiftKey) {
    // If Enter is pressed without Shift, trigger form submission
    event.preventDefault(); // Prevent default behavior (e.g., adding a new line)
    document.querySelector("form").dispatchEvent(new Event("submit")); // Trigger the form submission
  } else if (event.key === "Enter" && event.shiftKey) {
    // If Shift + Enter is pressed, allow a new line
    event.stopPropagation(); // Prevent triggering the form submission
  }
});

// let sideBar = document.querySelector(".history-tab").addEventListener("click", ()=>{
//   let sideTab = document.createElement("div");
//   sideTab.classList.add("history-tab-div");
//   sideBar.appendChild(sideTab);
// })

document.querySelector(".history-tab").addEventListener("click", () => {
  let existingSideTab = document.querySelector(".history-tab-div");

  if (existingSideTab) return;
  
  let sideTab = document.createElement("div");
  sideTab.classList.add("history-tab-div");

  let removeIcon = document.createElement("button");
  removeIcon.innerHTML = `<i class="fa-solid fa-xmark"></i>`;

  let nav = document.createElement("nav");
  let navText = document.createElement("h3");
  navText.innerHTML=`History`;
  

  let contentdiv = document.createElement("div");
  contentdiv.classList.add("sidebar-content-div");
  contentdiv.innerText = "Simple Conversation"

  sideTab.appendChild(nav);
  nav.appendChild(navText);
  nav.appendChild(removeIcon);
  sideTab.appendChild(contentdiv);
  document.body.appendChild(sideTab);

    removeIcon.addEventListener("click", ()=>{
      sideTab.remove();
    })
});
