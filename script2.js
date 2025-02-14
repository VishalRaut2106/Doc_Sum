document.getElementById("pdfUploadForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("pdfFile");
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        fetch("http://localhost:5000/upload", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);
            displayResults(data);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while processing the document.");
        });
    } else {
        alert("Please select a file to upload.");
    }
});

function displayResults(data) {
    const resultDiv = document.getElementById("analysisResult");
    resultDiv.classList.remove("d-none");

    if (!data.summary || !data.text) {
        resultDiv.innerHTML = "<p>Error: Incomplete data received.</p>";
        console.error("Incomplete data:", data);
        return;
    }

    const resultHTML = `
        <h3>Summary</h3>
        <p>${data.summary}</p>
        <h3>Extracted Text</h3>
        <div class="extracted-text">${data.text}</div>
    `;
    document.getElementById("resultText").innerHTML = resultHTML;
}
