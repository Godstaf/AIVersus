
var u_email = null;
var u_name = null;

async function fetchUserEmail() {

  try {
    const response = await fetch("/get_user");
    const result = await response.json();

    if (response.status === 200) {
      // console.log("Logged-in user email:", result.email);
      u_email = result.email;
      u_name = result.name;

    } else {
      // console.log("No user is logged in.");
      u_email = null;
      u_name = null;
    }
  } catch (error) {
    console.error("Error fetching user email:", error);
  }

}



async function main() {

  await fetchUserEmail(); // Wait for fetchUserEmail to complete
  console.log("User email:", u_email); // Now this will log the updated value
  console.log("User name:", u_name);

  // -->Non logged Ins

  if (u_email == null) {

    document.querySelector(".profile").addEventListener("click", () => {
      let profBtn = document.querySelector(".profile");
      let existingProfileTab = document.querySelector(".main-profile-tab");

      if (existingProfileTab) {
        existingProfileTab.remove();
        return;
      }

      let profileTab = document.createElement("div");
      profileTab.classList.add("main-profile-tab");

      const navbar = document.querySelector(".navbar");
      const navbarHeight = navbar.offsetHeight;
      profileTab.style.top = `${navbarHeight}px`;

      let dp = document.createElement("div");
      dp.classList.add("prof-dp");
      dp.innerText = "?";
      let userName = document.createElement("div");
      userName.classList.add("prof-U-name");
      userName.innerText = "No-Data";

      let logger = document.createElement("div");
      logger.classList.add("logger");

      let profSignUp = document.createElement("a");
      profSignUp.classList.add("profSignUp");
      profSignUp.innerText = "SignUp";

      let profLogIn = document.createElement("a");
      profLogIn.classList.add("profLogIn");
      profLogIn.innerText = "LogIn";

      profSignUp.href = "/register";
      profLogIn.href = "/login";

      logger.appendChild(profSignUp);
      logger.appendChild(profLogIn);

      profileTab.appendChild(dp);
      profileTab.appendChild(userName);
      profileTab.appendChild(logger);

      document.body.appendChild(profileTab);

      function handleDocumentClick(event) {
        if (!profileTab.contains(event.target) && !profBtn.contains(event.target)) {
          profileTab.remove();
          document.removeEventListener("click", handleDocumentClick);
        }
      }
      document.addEventListener("click", handleDocumentClick);
    })

  }

  // -->loggen In

  else {
    document.querySelector(".profile").addEventListener("click", () => {
      let profBtn = document.querySelector(".profile");
      let existingProfileTab = document.querySelector(".main-profile-tab");

      if (existingProfileTab) {
        existingProfileTab.remove();
        return;
      }

      let profileTab = document.createElement("div");
      profileTab.classList.add("main-profile-tab");

      const navbar = document.querySelector(".navbar");
      const navbarHeight = navbar.offsetHeight;
      profileTab.style.top = `${navbarHeight}px`;

      let wave = document.createElement("div");
      wave.classList.add("wave-user");
      wave.innerText = "Hello " + u_name + "!";


      let logOut = document.createElement("div");
      logOut.classList.add("logOut");
      logOut.innerHTML = `Log Out <a><i class="fa-solid fa-right-from-bracket"></i></a>`

      // Add an event listener to the logout button
      logOut.addEventListener("click", (event) => {
        // event.preventDefault(); // Prevent the default behavior of the click event

        // Clear the user data
        u_email = null;
        u_name = null;

        // Optionally, clear session data on the server (if applicable)
        fetch("/logout", { method: "POST" })
          .then(() => {
            // Reload the page to reflect the logout state
            location.reload();
          })
          .catch((error) => {
            console.error("Error during logout:", error);
          });
      });

      profileTab.appendChild(wave);
      profileTab.appendChild(logOut);

      document.body.appendChild(profileTab);

      function handleDocumentClick(event) {
        if (!profileTab.contains(event.target) && !profBtn.contains(event.target)) {
          profileTab.remove();
          document.removeEventListener("click", handleDocumentClick); // remove the listener here
        }
      }
      document.addEventListener("click", handleDocumentClick);
    })
  }




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


    sendBtn = document.querySelector(".btn-search");
    sendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    sendBtn.disabled = true;

    const inputField = document.getElementById("qry");
    inputField.disabled = true; // Disable the input field to prevent Enter key submission

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


      // Re-enable the send button and Enter key
      sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
      sendBtn.disabled = false;
      inputField.disabled = false; // Re-enable the input field



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

    if (existingSideTab) {
      existingSideTab.classList.toggle("visible");
      return;
    }

    let sideTab = document.createElement("div");
    sideTab.classList.add("history-tab-div");

    let removeIcon = document.createElement("button");
    removeIcon.innerHTML = `<i class="fa-solid fa-xmark"></i>`;

    let nav = document.createElement("nav");
    let navText = document.createElement("h3");
    navText.innerHTML = `History`;


    let contentdiv = document.createElement("div");
    contentdiv.classList.add("sidebar-content-div");
    contentdiv.innerText = "Simple Conversation"

    sideTab.appendChild(nav);
    nav.appendChild(navText);
    nav.appendChild(removeIcon);
    sideTab.appendChild(contentdiv);
    document.body.appendChild(sideTab);

    setTimeout(() => {
      sideTab.classList.add("visible");
    }, 10);

    removeIcon.addEventListener("click", () => {
      sideTab.classList.remove("visible");
      setTimeout(() => {
        sideTab.remove();
      }, 300);
    });
  });

}

main();











