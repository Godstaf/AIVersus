var u_email = null;
var u_name = null;
var chatgptBtn = true; // Initialize chatgptBtn to true
var deepseekBtn = true; // Initialize DeepSeekBtn to true
var geminiBtn = true; // Initialize geminiBtn to true

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

// delete empty chats
async function deleteEmptyChats() {
  try {
    const response = await fetch("/delete_empty_chats", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });

    if (response.status === 200) {
      console.log("Empty chats deleted successfully.");
    } else {
      console.error("Error deleting empty chats:", await response.text());
    }
  } catch (error) {
    console.error("Error deleting empty chats:", error);
  }
}

async function main() {

  // Helper to render all chats in the sidebar
  async function renderSidebarChats(selectedChatId = null) {
    console.log('Rendering sidebar chats with selectedChatId:', selectedChatId);

    const sidebarContent = document.querySelector(".sidebar-content-div");
    sidebarContent.innerHTML = "";


    const response = await fetch("/get_all_chats");
    const result = await response.json();
    const chats = result.chats || [];

    let anySelected = false;

    chats.slice().reverse().forEach((chat) => {
      chat.title = chat.queries[0] || ""; // Get the first query as the title, or an empty string if not present
      const chatDiv = document.createElement("div");
      chatDiv.className = "sidebar-chat-entry";
      chatDiv.dataset.chatId = chat.chat_id;

      // Create span for chat title text
      const chatTitleSpan = document.createElement("span");
      chatTitleSpan.className = "chat-title-text";
      chatTitleSpan.innerText = chat.title || "New Chat";
      chatDiv.appendChild(chatTitleSpan);

      // Create delete icon
      const deleteIcon = document.createElement("i");
      deleteIcon.className = "fa-solid fa-trash delete-chat-icon";
      deleteIcon.title = "Delete chat";
      deleteIcon.addEventListener("click", async function (event) {
        event.stopPropagation(); // Prevent triggering chat selection

        // Call delete API
        try {
          const response = await fetch("/delete_chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ chat_id: chat.chat_id })
          });

          if (response.status === 200) {
            console.log("Chat deleted successfully:", chat.chat_id);
            // Remove the chat div from sidebar
            chatDiv.remove();

            // If deleted chat was active, select another one
            if (chatDiv.classList.contains("active-chat")) {
              const remainingChats = document.querySelectorAll(".sidebar-chat-entry");
              if (remainingChats.length > 0) {
                remainingChats[0].classList.add("active-chat");
                loadChatHistory(remainingChats[0].dataset.chatId);
              } else {
                // No chats left, create a new one
                await createNewChat();
              }
            }
          } else {
            console.error("Error deleting chat:", await response.text());
          }
        } catch (error) {
          console.error("Error deleting chat:", error);
        }
      });
      chatDiv.appendChild(deleteIcon);

      // Highlight if this is the selected chat
      // console.log('Selected chat ID:', selectedChatId);
      // console.log('Current chat ID:', chat.chat_id);

      if (selectedChatId && chat.chat_id === selectedChatId) {
        chatDiv.classList.add("active-chat");
        anySelected = true;
        console.log("If Ran! Selected chat:", chat.chat_id);
      }



      chatDiv.addEventListener("click", function () {
        document.querySelectorAll(".sidebar-chat-entry").forEach(e => e.classList.remove("active-chat"));
        chatDiv.classList.add("active-chat");
        loadChatHistory(chat.chat_id);
      });

      sidebarContent.appendChild(chatDiv);
    });

    // If no chat is selected, select and load the first one
    const allChats = document.querySelectorAll(".sidebar-chat-entry");
    if (allChats.length > 0 && !anySelected) {
      allChats[0].classList.add("active-chat");
      loadChatHistory(allChats[0].dataset.chatId);
    }
  }


  // Update loadChatHistory to accept chat_id
  async function loadChatHistory(chat_id) {
    chatgptBtn = true; // Initialize chatgptBtn to true
    deepseekBtn = true; // Initialize DeepSeekBtn to true
    geminiBtn = true; // Initialize geminiBtn to true
    try {
      const response = await fetch(`/get_chat_history?chat_id=${chat_id}`);
      const result = await response.json();

      // Check if the response is successful
      if (response.status === 200) {
        const convoDiv = document.querySelector(".convo");
        convoDiv.innerHTML = ""; // Clear existing chat

        // Display queries and responses
        const queries = result.queries || []; // Default to empty array if not present
        const response = result.response || []; // Default to empty array if not present
        const response2 = result.response2 || [];
        const response3 = result.response3 || [];
        for (let i = 0; i < queries.length; i++) {
          const queryDiv = document.createElement("div");
          queryDiv.className = "query-container";
          queryDiv.innerText = queries[i];
          convoDiv.appendChild(queryDiv);

          // const responseDiv = document.createElement("div");
          // responseDiv.className = "response-container";
          // responseDiv.innerText = response[i] || "No response"; // Default to "No response" if not present
          // convoDiv.appendChild(responseDiv); // Append the response div after the query div

          // const responseDiv2 = document.createElement("div");
          // responseDiv2.className = "response-container";
          // responseDiv2.innerText = response2[i];
          // convoDiv.appendChild(responseDiv2);


          // const responseDiv3 = document.createElement("div");
          // responseDiv3.className = "response-container";  
          // responseDiv3.innerText = response3[i];
          // convoDiv.appendChild(responseDiv3);

          const wholeResponseContainer = document.createElement("div");
          wholeResponseContainer.className = "whole-res-container";

          // Add the response in .convo div
          if (response[i]) {
            const newDiv = document.createElement("div");
            newDiv.className = "response-container";

            const responseNav = document.createElement("nav");
            responseNav.className = "response-nav";
            responseNav.innerText = "Chat-Gpt"
            newDiv.appendChild(responseNav);

            const responseContent = document.createElement("div");
            responseContent.className = "response-content";
            responseContent.innerText = response[i];
            // console.log(response[i]);
            newDiv.appendChild(responseContent);


            wholeResponseContainer.appendChild(newDiv);
          }


          // Add the second response
          if (response2[i]) {
            const newDiv2 = document.createElement("div");
            newDiv2.className = "response-container";
            const responseNav2 = document.createElement("nav");
            responseNav2.className = "response-nav";
            responseNav2.innerText = "DeepSeek";
            newDiv2.appendChild(responseNav2);

            const responseContent2 = document.createElement("div");
            responseContent2.className = "response-content";
            responseContent2.innerText = response2[i];
            // console.log(response2[i]);
            newDiv2.appendChild(responseContent2);

            wholeResponseContainer.appendChild(newDiv2);
          }


          // Add the third response
          if (response3[i]) {
            const newDiv3 = document.createElement("div");
            newDiv3.className = "response-container";
            const responseNav3 = document.createElement("nav");
            responseNav3.className = "response-nav";
            responseNav3.innerText = "Gemini";
            newDiv3.appendChild(responseNav3);

            const responseContent3 = document.createElement("div");
            responseContent3.className = "response-content";
            responseContent3.innerText = response3[i];
            // console.log(response3[i]);
            newDiv3.appendChild(responseContent3);

            wholeResponseContainer.appendChild(newDiv3);
          }

          convoDiv.appendChild(wholeResponseContainer); // Append the new div to .convo



        }
      } else {
        console.error("Error loading chat history:", result.message);
      }
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  }


  // Create a new chat and highlight it
  async function createNewChat() {
    chatgptBtn = true; // Initialize chatgptBtn to true
    deepseekBtn = true; // Initialize DeepSeekBtn to true
    geminiBtn = true; // Initialize geminiBtn to true
    try {
      const response = await fetch("/new_chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: u_email })
      });

      if (response.status === 200) {
        const result = await response.json();
        // console.log("New chat created successfully.");
        console.log("New chat created successfully with ID:", result.chat_id);
        if (result.chat_id) {
          await renderSidebarChats(result.chat_id); // Only this highlights and loads the new chat
          // console.log("If condition met, chat_id:", result.chat_id);
          await loadChatHistory(result.chat_id);   // Explicitly load the new chat's content
        } else {
          console.warn("New chat created but no chat_id returned. Rendering all chats.");
          await renderSidebarChats();
          // console.log("No chat_id found, rendering all chats.");
        }
      } else {
        console.error("Error creating new chat:", await response.text());
      }
    } catch (error) {
      console.error("Error creating new chat:", error);
    }
  }

  // Fetch user email and name
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
    await deleteEmptyChats(); // Delete empty chats before creating a new one
    // Call loadChatHistory after successful login
    if (u_email !== null) {
      console.log("User is logged in with email:", u_email);
      await createNewChat(); // Create a new chat when the user logs in

    }
    // get chat id of the current chat

    // await loadChatHistory(); // Load the default chat history or the first chat
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


  document.querySelector(".chatgpt-btn").addEventListener("click", async () => {
    // Handle ChatGPT button click
    if (chatgptBtn === true && deepseekBtn === false && geminiBtn === false) {
      alert("Choose at least one AI model to query.");
    }
    else {
      chatgptBtn = !chatgptBtn;
      if (chatgptBtn === false) {
        document.querySelector(".chatgpt-logo").style.filter = "grayscale(50%) brightness(0.5)";
        // console.log('ChatGPT button is now disabled');

      }
      else {
        document.querySelector(".chatgpt-logo").style.filter = "grayscale(0%) brightness(1)";
        // console.log('ChatGPT button is now enabled');
      }
      console.log("ChatGPT button toggled:", chatgptBtn);
      await fetch('/chatgpt-btn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chatgptBtn: chatgptBtn })
      });
    }
  });


  document.querySelector(".deepseek-btn").addEventListener("click", async () => {
    // Handle DeepSeek button click
    if (deepseekBtn === true && chatgptBtn === false && geminiBtn === false) {
      alert("Choose at least one AI model to query.");
    }
    else {
      deepseekBtn = !deepseekBtn;
      if (deepseekBtn === false) {
        document.querySelector(".deepseek-logo").style.filter = "grayscale(50%) brightness(0.5)";
        // console.log('DeepSeek button is now disabled');
      }
      else {
        document.querySelector(".deepseek-logo").style.filter = "grayscale(0%) brightness(1)";
        // console.log('DeepSeek button is now enabled');
      }
      console.log("DeepSeek button toggled:", deepseekBtn);
      await fetch('/deepseek-btn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ deepseekBtn: deepseekBtn })
      });
    }
  });


  document.querySelector(".gemini-btn").addEventListener("click", async () => {
    // Handle Gemini button click
    if (geminiBtn === true && chatgptBtn === false && deepseekBtn === false) {
      alert("Choose at least one AI model to query.");
    }
    else {
      geminiBtn = !geminiBtn;
      if (geminiBtn === false) {
        document.querySelector(".gemini-logo").style.filter = "grayscale(50%) brightness(0.5)";
        // console.log('Gemini button is now disabled');
      }
      else {
        document.querySelector(".gemini-logo").style.filter = "grayscale(0%) brightness(1)";
      }
      console.log("Gemini button toggled:", geminiBtn);
      await fetch('/gemini-btn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ geminiBtn: geminiBtn })
      });
    }
  });



  document.querySelector("form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const convoDiv = document.querySelector(".convo");
    const queryText = document.getElementById("qry").value;

    // Add the query/topic to conversation
    const newDiv = document.createElement("div");
    newDiv.className = "query-container";
    newDiv.innerHTML = `<strong>🎯 Debate Topic:</strong> ${queryText}`;
    convoDiv.appendChild(newDiv);

    const formData = new FormData(this);
    const queryUrl = this.getAttribute("data-query-url");
    document.getElementById("qry").value = "";

    const sendBtn = document.querySelector(".btn-search");
    sendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    sendBtn.disabled = true;

    const inputField = document.getElementById("qry");
    inputField.disabled = true;

    // Add loading indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "debate-loading";
    loadingDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Starting debate... (this may take a minute)';
    loadingDiv.style.cssText = "padding: 20px; text-align: center; color: #888; font-style: italic;";
    convoDiv.appendChild(loadingDiv);

    try {
      const apiCall = await fetch(queryUrl, {
        method: "POST",
        body: formData,
      });
      const response = await apiCall.json();

      // Remove loading indicator
      loadingDiv.remove();

      // Check if topic was not debatable
      if (response.status === "not_debatable") {
        const notDebatableDiv = document.createElement("div");
        notDebatableDiv.className = "response-container not-debatable";
        notDebatableDiv.innerHTML = `
          <nav class="response-nav" style="background: #ff6b6b;">⚠️ Not Debatable</nav>
          <div class="response-content">
            <strong>Reason:</strong> ${response.reason}<br><br>
            ${response.suggested_topic ? `<strong>Try instead:</strong> "${response.suggested_topic}"` : ''}
          </div>
        `;
        convoDiv.appendChild(notDebatableDiv);
      }
      // Render debate rounds
      else if (response.status === "success") {
        const rounds = response.rounds || [];

        // Render each round
        rounds.forEach((round, index) => {
          const roundContainer = document.createElement("div");
          roundContainer.className = "debate-round";

          // Round header
          const roundHeader = document.createElement("div");
          roundHeader.className = "round-header";
          roundHeader.innerHTML = `<h3>📢 Round ${round.round}</h3>`;
          roundHeader.style.cssText = "background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px 15px; border-radius: 8px 8px 0 0; margin-top: 20px;";
          roundContainer.appendChild(roundHeader);

          const wholeResponseContainer = document.createElement("div");
          wholeResponseContainer.className = "whole-res-container";

          // FOR Agent (Green)
          if (round.for) {
            const forDiv = document.createElement("div");
            forDiv.className = "response-container for-agent";
            forDiv.innerHTML = `
              <nav class="response-nav" style="background: linear-gradient(135deg, #11998e, #38ef7d);">🟢 FOR</nav>
              <div class="response-content">${round.for}</div>
            `;
            wholeResponseContainer.appendChild(forDiv);
          }

          // AGAINST Agent (Red)
          if (round.against) {
            const againstDiv = document.createElement("div");
            againstDiv.className = "response-container against-agent";
            againstDiv.innerHTML = `
              <nav class="response-nav" style="background: linear-gradient(135deg, #eb3349, #f45c43);">🔴 AGAINST</nav>
              <div class="response-content">${round.against}</div>
            `;
            wholeResponseContainer.appendChild(againstDiv);
          }

          // BALANCED Agent (Yellow/Gold)
          if (round.balanced) {
            const balancedDiv = document.createElement("div");
            balancedDiv.className = "response-container balanced-agent";
            balancedDiv.innerHTML = `
              <nav class="response-nav" style="background: linear-gradient(135deg, #f7971e, #ffd200);">🟡 BALANCED</nav>
              <div class="response-content">${round.balanced}</div>
            `;
            wholeResponseContainer.appendChild(balancedDiv);
          }

          roundContainer.appendChild(wholeResponseContainer);
          convoDiv.appendChild(roundContainer);
        });

        // Render Judge Verdict
        const verdict = response.verdict;
        if (verdict) {
          const verdictContainer = document.createElement("div");
          verdictContainer.className = "judge-verdict";
          verdictContainer.style.cssText = "margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; border: 2px solid gold;";

          // Winner banner
          const winnerEmoji = verdict.winner === "FOR" ? "🟢" : verdict.winner === "AGAINST" ? "🔴" : verdict.winner === "BALANCED" ? "🟡" : "🤝";

          let scoresHTML = "";
          if (verdict.scores) {
            const scores = verdict.scores;
            scoresHTML = `
              <div style="display: flex; justify-content: space-around; margin: 15px 0; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 10px; background: rgba(17,153,142,0.2); border-radius: 8px; min-width: 100px;">
                  <div style="color: #38ef7d;">🟢 FOR</div>
                  <div style="font-size: 24px; font-weight: bold;">${scores.for?.total || '?'}/30</div>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(235,51,73,0.2); border-radius: 8px; min-width: 100px;">
                  <div style="color: #f45c43;">🔴 AGAINST</div>
                  <div style="font-size: 24px; font-weight: bold;">${scores.against?.total || '?'}/30</div>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(247,151,30,0.2); border-radius: 8px; min-width: 100px;">
                  <div style="color: #ffd200;">🟡 BALANCED</div>
                  <div style="font-size: 24px; font-weight: bold;">${scores.balanced?.total || '?'}/30</div>
                </div>
              </div>
            `;
          }

          let remarksHTML = "";
          if (verdict.remarks) {
            remarksHTML = `
              <div style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <strong>📝 Judge's Remarks:</strong><br>
                <div style="color: #38ef7d; margin-top: 8px;">FOR: ${verdict.remarks.for || 'No remarks'}</div>
                <div style="color: #f45c43; margin-top: 8px;">AGAINST: ${verdict.remarks.against || 'No remarks'}</div>
                <div style="color: #ffd200; margin-top: 8px;">BALANCED: ${verdict.remarks.balanced || 'No remarks'}</div>
              </div>
            `;
          }

          verdictContainer.innerHTML = `
            <div style="text-align: center; margin-bottom: 15px;">
              <span style="font-size: 28px;">⚖️</span>
              <h2 style="color: gold; margin: 5px 0;">JUDGE'S VERDICT</h2>
            </div>
            <div style="text-align: center; font-size: 32px; margin: 15px 0;">
              ${winnerEmoji} <span style="color: gold; font-weight: bold;">${verdict.winner}</span> WINS!
            </div>
            ${scoresHTML}
            <div style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px;">
              <strong>💬 Reasoning:</strong> ${verdict.reasoning || 'No reasoning provided.'}
            </div>
            ${remarksHTML}
          `;

          convoDiv.appendChild(verdictContainer);
        }
      }

      // Re-enable controls
      sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
      sendBtn.disabled = false;
      inputField.disabled = false;

    } catch (error) {
      console.error("Error:", error);
      loadingDiv.remove();

      let ErrorDiv = document.createElement('div');
      ErrorDiv.classList.add('error-div');
      ErrorDiv.classList.add('response-container');
      ErrorDiv.innerHTML = `
        <i class="fa-solid fa-triangle-exclamation"></i>
        An error occurred. Please try again.
      `;
      convoDiv.appendChild(ErrorDiv);
      sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
      sendBtn.disabled = false;
      inputField.disabled = false;
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

  document.querySelector(".history-tab").addEventListener("click", () => {
    let sideTab = document.querySelector(".history-tab-div");
    sideTab.classList.add("visible", true);
  });

  document.querySelector(".history-tab-div .new-chat").addEventListener("click", async (event) => {

    // check if there already exists an empty chat and if it exists then simply open it
    const response = await fetch("/get_all_chats");
    const result = await response.json();
    const chats = result.chats || [];
    const emptyChat = chats.find(chat => (chat.queries.length === 0 || !chat.queries[0]));
    if (emptyChat) {
      await renderSidebarChats(emptyChat.chat_id);
      loadChatHistory(emptyChat.chat_id);
      let sideTab = document.querySelector(".history-tab-div");
      sideTab.classList.add("visible", true);
      return;
    }


    event.preventDefault();
    await deleteEmptyChats(); // Delete empty chats before creating a new one
    await createNewChat(); // Create a new chat when the user clicks "New Chat"

    // createNewChat will now also load the chat content.

    // Keep the sidebar visible after creating a new chat
    let sideTab = document.querySelector(".history-tab-div");
    sideTab.classList.add("visible", true);
  });

  document.querySelector(".rmvIc0").addEventListener("click", () => {
    let sideTab = document.querySelector(".history-tab-div");
    setTimeout(() => {
      sideTab.classList.toggle("visible", false);
    }, 100);
  });


}

main();

