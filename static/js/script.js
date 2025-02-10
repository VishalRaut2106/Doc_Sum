document.getElementById("pdfUploadForm").addEventListener("submit", function (event) {
  event.preventDefault();

  // Get the file input element
  const fileInput = document.getElementById("pdfFile");
  const file = fileInput.files[0];  // Get the selected file

  // Ensure a file is selected
  if (file) {
    const formData = new FormData();  // Create a new FormData object
    formData.append("file", file);  // Append the file to the FormData object

    // Send the form data to the Flask server
    fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData,
      headers: {
        // The browser will automatically set Content-Type for multipart/form-data
        // No need to manually set Content-Type in this case
      },
    })
      .then((response) => {
        if (!response.ok) {
          console.error(`HTTP error! status: ${response.status}`);
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();  // Parse the JSON response from the server
      })
      .then((data) => {
        console.log("Received data:", data);  // Log the received data
        displayResults(data);  // Display the results on the page
      })
      .catch((error) => {
        console.error("Error:", error);  // Log any errors
        alert("An error occurred while processing the document. Check the console for details.");
      });
  } else {
    alert("Please select a file to upload.");  // Alert if no file is selected
  }
});
function showPage(pageId) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));

  // Show the selected page
  document.getElementById(pageId).classList.add('active');

  // Update active class on nav links
  document.querySelectorAll('nav .nav-link').forEach(link => link.classList.remove('active'));
  document.querySelector(`nav .nav-link[onclick="showPage('${pageId}')"]`).classList.add('active');
}


// Function to display the analysis results on the page
function displayResults(data) {
  const resultDiv = document.getElementById("analysisResult");  // Get the result div
  resultDiv.classList.remove("d-none");  // Make the result div visible

  // Check if the required data is present
  if (!data.summary || !data.text || !data.sentences || !data.questions || !data.answers) {
    resultDiv.innerHTML = "<p>Error: Incomplete data received from the server.</p>";  // Show error if data is incomplete
    console.error("Incomplete data:", data);  // Log the incomplete data
    return;
  }

  // Generate HTML for displaying the results
  const resultHTML = `
        <h3>Summary</h3>
        <p>${data.summary}</p>
        
        <h3>Extracted Text</h3>
        <div class="extracted-text">${data.text}</div>
        
        <h3>Sentences</h3>
        <ul>
            ${data.sentences.map((sentence) => `<li>${sentence}</li>`).join("")}
        </ul>
        
        <h3>Questions and Answers</h3>
        <ul class="list-group">
            ${data.questions
      .map(
        (question, index) => `
                <li class="list-group-item">
                    <strong>Q: ${question}</strong>
                    <br>
                    A: ${data.answers[index]}
                </li>
            `
      )
      .join("")}
        </ul>
    `;

  // Insert the generated HTML into the result div
  document.getElementById("resultText").innerHTML = resultHTML;
}
